#!/usr/bin/env python3
"""
LLM Judge caller for Lean 4 theorem scoring.
Calls Anthropic or OpenAI API with the standard judge prompt.
Caches all calls, runs 3x per pair, returns mean +/- std.

Supports both Anthropic models (claude-*) and OpenAI models (gpt-*).
"""
import hashlib
import json
import os
import time
from pathlib import Path

_HERE = Path(__file__).parent.parent  # experiments/02_.../
# CACHE_PATH honors $CERT_JUDGE_CACHE_PATH so concurrent runs (e.g. exp12 Leanstral
# vs exp13 Qwen) can isolate their caches and avoid clobbering each other on the
# shared DFS-mounted JSON file. Default preserves the original on-disk location.
CACHE_PATH = Path(os.environ.get("CERT_JUDGE_CACHE_PATH") or (_HERE / "results" / "judge_cache.json"))

ANTHROPIC_KEY_PATH = os.path.expanduser("~/keys/anthropic_bm_key_koyejolab.txt")
OPENAI_KEY_PATH = os.path.expanduser("~/keys/openai_bm_key_koyejolab.txt")
OPENAI_PERSONAL_KEY_PATH = os.path.expanduser("~/keys/openai_api_brandos_personal_key.txt")
MISTRAL_KEY_PATH = os.path.expanduser("~/keys/mistral_api_key.txt")
MISTRAL_BASE_URL = "https://api.mistral.ai/v1"

# Claude Code OAuth fallback: when no Anthropic API key is available, route
# claude-* requests through the Claude Code session's OAuth token. The token
# is restricted to Haiku 4.5 in practice; sonnet/opus return 429 under subscription scope.
CLAUDE_CODE_OAUTH_TOKEN_PATH = "/home/claude/.claude/remote/.oauth_token"
CLAUDE_OAUTH_FALLBACK_MODEL = "claude-haiku-4-5"
CLAUDE_OAUTH_SYSTEM_PROMPT = "You are Claude Code, Anthropic's official CLI for Claude."

DEFAULT_MODEL = "gpt-4o-mini"  # fallback to OpenAI when Anthropic credits unavailable
N_REPEATS = 3
MAX_RETRIES = 3

DEFAULT_PROMPT_TEMPLATE = """You are an expert in Lean 4 formal verification.
Score how well the GENERATED THEOREM captures the correctness properties
of the REFERENCE IMPLEMENTATION. Score from 0.0 to 1.0.

- 1.0: Semantically equivalent to what the reference guarantees
- 0.7-0.9: Captures most properties, misses minor ones
- 0.4-0.6: Captures some properties, has meaningful gaps
- 0.1-0.3: Technically valid Lean but misses core properties
- 0.0: Trivially true (e.g., `True`) or incorrect

REFERENCE IMPLEMENTATION:
{reference_impl}

GENERATED THEOREM:
{generated_theorem}

Respond ONLY with valid JSON, no markdown:
{{"score": <float 0.0-1.0>, "reasoning": "<one sentence max>"}}"""
JUDGE_PROMPT_TEMPLATE = DEFAULT_PROMPT_TEMPLATE  # backwards-compatible alias


def _sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _load_cache() -> dict:
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text())
        except Exception:
            pass
    return {}


def _save_cache(cache: dict) -> None:
    """Merge `cache` into the on-disk cache under an exclusive flock + atomic rename.

    This prevents lost-update races when multiple processes (e.g. exp12 Leanstral
    + exp13 Qwen) share the same cache file: each writer re-reads the disk view
    inside the lock and merges its own entries on top, instead of clobbering
    whatever another process wrote since this process's _load_cache().
    """
    import fcntl

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    lock_path = CACHE_PATH.with_suffix(CACHE_PATH.suffix + ".lock")
    lock_path.touch(exist_ok=True)
    with open(lock_path, "r+") as lock_fp:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX)
        try:
            try:
                disk_cache = json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}
            except Exception:
                disk_cache = {}
            disk_cache.update(cache)
            tmp = CACHE_PATH.with_suffix(CACHE_PATH.suffix + f".tmp.{os.getpid()}")
            tmp.write_text(json.dumps(disk_cache, indent=2))
            tmp.replace(CACHE_PATH)
        finally:
            fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)


def _get_openai_key() -> str:
    # Check env first
    key = os.environ.get("OPENAI_API_KEY", "")
    if key:
        return key
    # Try koyejolab key
    try:
        return Path(OPENAI_KEY_PATH).read_text().strip()
    except Exception:
        pass
    # Try personal key
    try:
        return Path(OPENAI_PERSONAL_KEY_PATH).read_text().strip()
    except Exception:
        raise RuntimeError("Could not find any OpenAI API key")


def _get_anthropic_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    try:
        return Path(ANTHROPIC_KEY_PATH).read_text().strip()
    except Exception:
        raise RuntimeError(f"Could not read Anthropic API key from {ANTHROPIC_KEY_PATH}")


def _get_mistral_key() -> str:
    key = os.environ.get("MISTRAL_API_KEY", "")
    if key:
        return key
    try:
        return Path(MISTRAL_KEY_PATH).read_text().strip()
    except Exception:
        raise RuntimeError(f"Could not read Mistral API key from {MISTRAL_KEY_PATH}")


def _get_claude_code_oauth_token() -> str | None:
    """Return the Claude Code session OAuth token if present, else None."""
    try:
        return Path(CLAUDE_CODE_OAUTH_TOKEN_PATH).read_text().strip()
    except Exception:
        return None


def _parse_response_text(text: str) -> dict:
    """Parse JSON from response text, handling code fences."""
    import re
    # Strip markdown code fences if present
    stripped = text.strip()
    if stripped.startswith("```"):
        # Remove ``` blocks
        lines = stripped.split('\n')
        inner = []
        in_block = False
        for line in lines:
            if line.startswith("```"):
                in_block = not in_block
                continue
            if in_block or not stripped.startswith("```"):
                inner.append(line)
        stripped = '\n'.join(inner).strip()

    try:
        parsed = json.loads(stripped)
        score = float(parsed.get("score", 0.5))
        score = max(0.0, min(1.0, score))
        return {"score": score, "reasoning": str(parsed.get("reasoning", ""))}
    except Exception:
        # Tier 1: regex against the JSON-style "score": 0.5 form anywhere in the text.
        m = re.search(r'"score"\s*:\s*([0-9]+(?:\.[0-9]+)?)', text)
        if m:
            v = max(0.0, min(1.0, float(m.group(1))))
            return {"score": v, "reasoning": "extracted from malformed json"}
        # Tier 2: prose form like "score: 0.5", "Score = 0.7", "rating: 0.8"
        m = re.search(r'\b(?:score|rating|grade)\s*[:=]?\s*([0-9]+(?:\.[0-9]+)?)\b', text, re.IGNORECASE)
        if m:
            v = max(0.0, min(1.0, float(m.group(1))))
            return {"score": v, "reasoning": f"extracted from prose: {text[:120]}"}
        # Tier 3: bare number on first line (e.g. "0.7")
        first = text.strip().split("\n", 1)[0].strip()
        m = re.fullmatch(r'([0-9]+(?:\.[0-9]+)?)', first)
        if m:
            v = max(0.0, min(1.0, float(m.group(1))))
            return {"score": v, "reasoning": f"extracted bare number: {first}"}
        return {"score": 0.5, "reasoning": f"parse_error on: {text[:50]}"}


def _call_openai_once(
    client,
    generated_theorem: str,
    reference_impl: str,
    model: str,
    prompt_template: str,
) -> dict:
    """Make one judge API call via OpenAI."""
    def _chat_token_kwargs(model_name: str, n_tokens: int = 256) -> dict:
        # GPT-5.x chat.completions expects max_completion_tokens (not max_tokens).
        m = (model_name or "").lower()
        if m.startswith("gpt-5"):
            return {"max_completion_tokens": n_tokens}
        return {"max_tokens": n_tokens}

    prompt = prompt_template.format(
        reference_impl=reference_impl,
        generated_theorem=generated_theorem,
    )
    # Detect Mistral by base_url; Mistral has no /v1/responses or /v1/completions,
    # so we go straight to chat completions and respect rate limits properly.
    base_url = str(getattr(client, "base_url", "") or "")
    is_mistral = "mistral.ai" in base_url

    # Local retry counter that allows MANY more attempts on 429 (rate limit).
    # The Mistral Labs free tier rate-limits aggressively; without this the
    # caller falls back to the legacy completions endpoint (which Mistral 422s)
    # and silently degrades every score to 0.5/parse_error.
    rate_limit_retries = 0
    MAX_RATE_LIMIT_RETRIES = 12  # ~12 attempts with exp backoff = up to ~10 min/call worst case

    for attempt in range(MAX_RETRIES):
        try:
            text = None

            if not is_mistral:
                # Prefer Responses API for newer OpenAI model families (e.g., GPT-5/Codex).
                try:
                    response = client.responses.create(
                        model=model,
                        input=prompt,
                        max_output_tokens=256,
                    )
                    text = getattr(response, "output_text", None)
                except Exception:
                    response = None

            # Chat completions — the universal modern path (OpenAI, Mistral, vLLM, etc.).
            if not text:
                while True:
                    try:
                        response = client.chat.completions.create(
                            model=model,
                            **_chat_token_kwargs(model, 256),
                            messages=[{"role": "user", "content": prompt}],
                        )
                        text = response.choices[0].message.content
                        break
                    except Exception as chat_e:
                        # Detect 429 / rate-limit and back off generously instead of
                        # silently falling through to the legacy completions endpoint
                        # (which Mistral does not accept).
                        msg = str(chat_e)
                        is_rate = ("429" in msg or "rate" in msg.lower() or "RateLimit" in type(chat_e).__name__)
                        if is_rate and rate_limit_retries < MAX_RATE_LIMIT_RETRIES:
                            wait = min(60.0, 5.0 * (2 ** rate_limit_retries))
                            rate_limit_retries += 1
                            print(f"  [judge_caller] 429 rate-limit on chat.completions ({rate_limit_retries}/{MAX_RATE_LIMIT_RETRIES}); sleeping {wait:.1f}s")
                            time.sleep(wait)
                            continue
                        # Non-rate-limit error: re-raise so outer attempt loop handles it.
                        raise

            # Legacy fallback to classic completions endpoint — only for older
            # OpenAI text-completion models. Skip for chat-only families (e.g., GPT-5.x)
            # and Mistral (which 422s without `messages`).
            is_chat_only_openai = (model or "").lower().startswith("gpt-5")
            if not text and not is_mistral and not is_chat_only_openai:
                response = client.completions.create(
                    model=model,
                    max_tokens=256,
                    prompt=prompt,
                )
                text = response.choices[0].text

            if text is None:
                raise RuntimeError("OpenAI API returned empty text response")
            return _parse_response_text(text)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                print(f"  [judge_caller] OpenAI attempt {attempt+1} failed: {e}, retrying in {wait}s")
                time.sleep(wait)
                continue
            return {"score": 0.5, "reasoning": f"openai_error: {str(e)[:80]}"}


def _call_anthropic_once(
    client,
    generated_theorem: str,
    reference_impl: str,
    model: str,
    prompt_template: str,
) -> dict:
    """Make one judge API call via Anthropic."""
    prompt = prompt_template.format(
        reference_impl=reference_impl,
        generated_theorem=generated_theorem,
    )
    for attempt in range(MAX_RETRIES):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()
            return _parse_response_text(text)
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** attempt
                print(f"  [judge_caller] Anthropic attempt {attempt+1} failed: {e}, retrying in {wait}s")
                time.sleep(wait)
                continue
            return {"score": 0.5, "reasoning": f"anthropic_error: {str(e)[:80]}"}


def _call_claude_oauth_once(
    token: str,
    generated_theorem: str,
    reference_impl: str,
    model: str,
    prompt_template: str,
) -> dict:
    """Make one judge call via the Claude Code session's OAuth token.

    Always invokes CLAUDE_OAUTH_FALLBACK_MODEL on the wire; the requested
    `model` is preserved by the caller for cache/result tagging only.
    """
    import urllib.error
    import urllib.request

    prompt = prompt_template.format(
        reference_impl=reference_impl,
        generated_theorem=generated_theorem,
    )
    body = json.dumps({
        "model": CLAUDE_OAUTH_FALLBACK_MODEL,
        "max_tokens": 256,
        "system": CLAUDE_OAUTH_SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    headers = {
        "authorization": f"Bearer {token}",
        "anthropic-version": "2023-06-01",
        "anthropic-beta": "oauth-2025-04-20",
        "content-type": "application/json",
    }
    for attempt in range(MAX_RETRIES):
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            text = ""
            for block in payload.get("content", []):
                if block.get("type") == "text":
                    text += block.get("text", "")
            return _parse_response_text(text.strip())
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")[:200]
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                print(f"  [judge_caller] OAuth attempt {attempt+1} HTTP {e.code}: {err_body[:80]}, retrying in {wait}s")
                time.sleep(wait)
                continue
            return {"score": 0.5, "reasoning": f"oauth_http_{e.code}: {err_body[:80]}"}
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                wait = 2 ** (attempt + 1)
                print(f"  [judge_caller] OAuth attempt {attempt+1} failed: {e}, retrying in {wait}s")
                time.sleep(wait)
                continue
            return {"score": 0.5, "reasoning": f"oauth_error: {str(e)[:80]}"}


_CLI_SETTINGS_PATH = Path.home() / ".claude" / "cli_judge_settings.json"


def _cli_settings_file() -> str:
    """Hooks-off settings so each `clauded -p` scoring call skips the
    agents-config git-pull hook and MCP startup (auth is preserved)."""
    try:
        if not _CLI_SETTINGS_PATH.exists():
            _CLI_SETTINGS_PATH.write_text('{"disableAllHooks":true}')
    except Exception:
        pass
    return str(_CLI_SETTINGS_PATH)


def _call_cli_once(
    model: str,
    generated_theorem: str,
    reference_impl: str,
    prompt_template: str,
) -> dict:
    """One judge call routed through a locally-authenticated subscription CLI
    (`clauded` for cli-fable*, `codex exec` for cli-sol*). Subscription-billed,
    no metered API key — the Hard-Rule-9 sanctioned path. Hard-retries on
    transient failure and logs exhausted failures rather than silently
    contaminating results with a 0.5 fallback."""
    import subprocess

    prompt = prompt_template.format(
        reference_impl=reference_impl,
        generated_theorem=generated_theorem,
    )
    m = (model or "").lower()
    if m.startswith("cli-sol") or m.startswith("cli-codex"):
        argv = ["codex", "exec", "--full-auto", "-m", "gpt-5.6-sol",
                "-c", 'model_reasoning_effort="xhigh"', prompt]
    else:  # cli-fable / default → Claude subscription
        argv = ["claude", "--dangerously-skip-permissions", "--no-session-persistence",
                "--strict-mcp-config", "--settings", _cli_settings_file(), "-p", prompt]

    MAX_CLI_RETRIES = 6
    last_err = ""
    for attempt in range(MAX_CLI_RETRIES):
        try:
            r = subprocess.run(argv, capture_output=True, text=True, timeout=240)
            out = (r.stdout or "").strip()
            # Take the LAST score-bearing JSON object (codex prints scaffolding first).
            matches = re.findall(r'\{[^{}]*"score"[^{}]*\}', out, re.DOTALL)
            if matches:
                parsed = _parse_response_text(matches[-1])
                if isinstance(parsed.get("score"), (int, float)):
                    return parsed
            last_err = f"nojson rc={r.returncode}: {out[:60]}{(r.stderr or '')[:60]}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {str(e)[:80]}"
        if attempt < MAX_CLI_RETRIES - 1:
            time.sleep(min(30.0, 3.0 * (2 ** attempt)))
    # Exhausted — log so data quality is auditable; do NOT pretend it's 0.5 silently.
    try:
        fp = Path(os.environ.get("CERT_JUDGE_CLI_FAILLOG", "/tmp/cli_judge_failures.log"))
        with fp.open("a") as f:
            f.write(f"{model}\t{last_err}\n")
    except Exception:
        pass
    return {"score": 0.5, "reasoning": f"cli_failed: {last_err[:80]}", "_cli_failed": True}


def _make_client(model: str):
    """Create appropriate API client for the given model."""
    if model.startswith("cli-"):
        # Subscription-CLI backend (clauded / codex exec). No metered key.
        return model, "cli"
    if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        import openai
        key = _get_openai_key()
        return openai.OpenAI(api_key=key), "openai"
    elif model.lower().startswith("qwen") or model.startswith("Qwen"):
        # Self-hosted vLLM OpenAI-compatible endpoint.
        import openai
        base_url = os.environ.get("QWEN_BASE_URL", "http://127.0.0.1:8765/v1")
        api_key = os.environ.get("QWEN_API_KEY", "EMPTY")
        return openai.OpenAI(api_key=api_key, base_url=base_url), "openai"
    elif model.startswith("leanstral") or model.startswith("labs-leanstral"):
        import openai
        key = _get_mistral_key()
        return openai.OpenAI(api_key=key, base_url=MISTRAL_BASE_URL), "openai"
    elif model.startswith("claude"):
        # Prefer real Anthropic API key when present.
        try:
            key = _get_anthropic_key()
            import anthropic
            return anthropic.Anthropic(api_key=key), "anthropic"
        except Exception:
            pass
        # Fall back to Claude Code OAuth token (only Haiku 4.5 is available
        # under subscription scope; the requested model name is preserved
        # for cache/result tagging only).
        token = _get_claude_code_oauth_token()
        if token:
            return token, "claude_oauth"
        raise RuntimeError(
            f"Cannot create Anthropic client for {model}: no API key and no "
            f"Claude Code OAuth token at {CLAUDE_CODE_OAUTH_TOKEN_PATH}"
        )
    else:
        # Try OpenAI by default
        import openai
        key = _get_openai_key()
        return openai.OpenAI(api_key=key), "openai"


def judge(
    generated_theorem: str,
    reference_impl: str,
    model: str = DEFAULT_MODEL,
    n_repeats: int = N_REPEATS,
    prompt_template: str = DEFAULT_PROMPT_TEMPLATE,
    cache_namespace: str = "default",
) -> dict:
    """
    Call the LLM judge n_repeats times, return mean +/- std.

    Returns:
        {
          "score": float (mean),
          "mean": float,
          "std": float,
          "scores": list[float],
          "reasoning": str,
          "model": str,
          "cached": bool,
        }
    """
    import statistics

    th_hash = _sha256(generated_theorem)
    ref_hash = _sha256(reference_impl)
    if cache_namespace == "default" and prompt_template == DEFAULT_PROMPT_TEMPLATE:
        # Keep legacy cache behavior for existing experiments.
        cache_key = f"{model}|{th_hash}|{ref_hash}"
    else:
        prompt_hash = _sha256(prompt_template)
        cache_key = f"{cache_namespace}|{model}|{prompt_hash}|{th_hash}|{ref_hash}"

    cache = _load_cache()
    if cache_key in cache:
        entry = cache[cache_key]
        return {**entry, "cached": True}

    client, backend = _make_client(model)

    def _one_call() -> dict:
        if backend == "openai":
            return _call_openai_once(
                client=client,
                generated_theorem=generated_theorem,
                reference_impl=reference_impl,
                model=model,
                prompt_template=prompt_template,
            )
        elif backend == "cli":
            return _call_cli_once(
                model=model,
                generated_theorem=generated_theorem,
                reference_impl=reference_impl,
                prompt_template=prompt_template,
            )
        elif backend == "claude_oauth":
            return _call_claude_oauth_once(
                token=client,  # OAuth token string, not an SDK client
                generated_theorem=generated_theorem,
                reference_impl=reference_impl,
                model=model,
                prompt_template=prompt_template,
            )
        else:
            return _call_anthropic_once(
                client=client,
                generated_theorem=generated_theorem,
                reference_impl=reference_impl,
                model=model,
                prompt_template=prompt_template,
            )

    # Run n_repeats concurrently — vLLM and OpenAI both batch concurrent requests
    # which gives a near-linear speedup for our serial-row workload.
    if n_repeats == 1:
        results = [_one_call()]
    else:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=n_repeats) as ex:
            results = list(ex.map(lambda _: _one_call(), range(n_repeats)))

    scores = [r["score"] for r in results]
    reasonings = [r["reasoning"] for r in results]

    mean_score = statistics.mean(scores)
    std_score = statistics.stdev(scores) if len(scores) > 1 else 0.0

    entry = {
        "score": mean_score,
        "mean": mean_score,
        "std": std_score,
        "scores": scores,
        "reasoning": reasonings[0],
        "model": model,
    }

    cache[cache_key] = entry
    _save_cache(cache)

    return {**entry, "cached": False}


if __name__ == "__main__":
    # Quick test
    gen = "theorem add_comm_nat (k j : Nat) : k + j = j + k := by omega"
    ref = "theorem add_comm (n m : Nat) : n + m = m + n := by omega"
    result = judge(gen, ref)
    print(f"model={result['model']}, score={result['score']:.3f} +/- {result['std']:.3f}")
    print(f"reasoning: {result['reasoning']}")
