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
CACHE_PATH = _HERE / "results" / "judge_cache.json"

ANTHROPIC_KEY_PATH = os.path.expanduser("~/keys/anthropic_bm_key_koyejolab.txt")
OPENAI_KEY_PATH = os.path.expanduser("~/keys/openai_bm_key_koyejolab.txt")
OPENAI_PERSONAL_KEY_PATH = os.path.expanduser("~/keys/openai_api_brandos_personal_key.txt")

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
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2))


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
        # Try regex extraction
        m = re.search(r'"score"\s*:\s*([0-9.]+)', text)
        if m:
            return {"score": float(m.group(1)), "reasoning": "extracted from malformed json"}
        return {"score": 0.5, "reasoning": f"parse_error on: {text[:50]}"}


def _call_openai_once(
    client,
    generated_theorem: str,
    reference_impl: str,
    model: str,
    prompt_template: str,
) -> dict:
    """Make one judge API call via OpenAI."""
    prompt = prompt_template.format(
        reference_impl=reference_impl,
        generated_theorem=generated_theorem,
    )
    for attempt in range(MAX_RETRIES):
        try:
            # Prefer Responses API for newer OpenAI model families (e.g., GPT-5/Codex).
            text = None
            try:
                response = client.responses.create(
                    model=model,
                    input=prompt,
                    max_output_tokens=256,
                )
                text = getattr(response, "output_text", None)
            except Exception:
                response = None

            # Fallback to chat completions for chat-compatible models.
            if not text:
                try:
                    response = client.chat.completions.create(
                        model=model,
                        max_tokens=256,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    text = response.choices[0].message.content
                except Exception:
                    response = None

            # Legacy fallback to classic completions endpoint.
            if not text:
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


def _make_client(model: str):
    """Create appropriate API client for the given model."""
    if model.startswith("gpt") or model.startswith("o1") or model.startswith("o3"):
        import openai
        key = _get_openai_key()
        return openai.OpenAI(api_key=key), "openai"
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

    scores = []
    reasonings = []
    for i in range(n_repeats):
        if backend == "openai":
            result = _call_openai_once(
                client=client,
                generated_theorem=generated_theorem,
                reference_impl=reference_impl,
                model=model,
                prompt_template=prompt_template,
            )
        elif backend == "claude_oauth":
            result = _call_claude_oauth_once(
                token=client,  # OAuth token string, not an SDK client
                generated_theorem=generated_theorem,
                reference_impl=reference_impl,
                model=model,
                prompt_template=prompt_template,
            )
        else:
            result = _call_anthropic_once(
                client=client,
                generated_theorem=generated_theorem,
                reference_impl=reference_impl,
                model=model,
                prompt_template=prompt_template,
            )

        scores.append(result["score"])
        reasonings.append(result["reasoning"])
        if i < n_repeats - 1:
            time.sleep(0.3)  # small delay

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
