"""Planning cost quote for re-running the paper's TI_var pipeline (exp16 protocol) on Verina.

Zero-spend arithmetic only: no inference client, no credentials.
Per-configuration item counts mirror the VeriBench exp16 run that feeds the paper's TI_var
(72 candidate-gold pairs + 24 golds x 4 rewrites + 24 golds x 5 bug-ladder levels, 3 repeats).
Prompt sizes are the VeriBench means measured by the 09-22-2026 lookup (pairs ~3.6 KB,
property probes ~0.9 KB); Verina `task.lean` files are similar (median 1,769 B), so these are
planning estimates. The exact quote must be regenerated from the real Verina request manifest.
Token rule (frozen PTI-v0 convention): input <= UTF-8 bytes + 128 tokens, output <= 256 tokens,
all input billed uncached.
"""

import json

REPEATS = 3
OUT_TOKENS = 256
OVERHEAD_TOKENS = 128
PAIR_BYTES = 3600
PROBE_BYTES = 900
REWRITES_PER_GOLD = 4  # RENAME, REORDER, STYLE, ALPHA
BUG_LEVELS_PER_GOLD = 5  # L0 (gold vs gold) .. L4

# USD per million tokens, copied from the frozen repo config
# experiments/archive/04_veribench_validation/pti_v0_v4/frozen_config.json (sources dated 2026-08-21).
PRICES = {
    "gpt-5.3-codex": {"input": 1.75, "output": 14.0},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
}

# Codex family as in the paper's Codex-family table: 4 gpt-5.3-codex prompts, 2 gpt-4o-mini
# prompts, and 2 deterministic controls (editdist_e1, random_r1) that cost nothing.
CODEX_FAMILY = [("gpt-5.3-codex", 4), ("gpt-4o-mini", 2)]

DESIGNS = {
    "matched_24": {"golds": 24, "pairs": 72},  # same counts as VeriBench (3 agents x 24 items)
    "full_189": {"golds": 189, "pairs": 567},  # every Verina item, 3 agents each
}


def per_config(golds: int, pairs: int) -> dict:
    probes = golds * (REWRITES_PER_GOLD + BUG_LEVELS_PER_GOLD)
    items = pairs + probes
    input_tokens = REPEATS * (pairs * (PAIR_BYTES + OVERHEAD_TOKENS) + probes * (PROBE_BYTES + OVERHEAD_TOKENS))
    return {
        "items": items,
        "calls": items * REPEATS,
        "input_tokens": input_tokens,
        "output_tokens": items * REPEATS * OUT_TOKENS,
    }


def main() -> None:
    quote = {}
    for name, d in DESIGNS.items():
        c = per_config(d["golds"], d["pairs"])
        rows, total_usd, total_calls = [], 0.0, 0
        for model, n_cfg in CODEX_FAMILY:
            p = PRICES[model]
            usd = c["input_tokens"] / 1e6 * p["input"] + c["output_tokens"] / 1e6 * p["output"]
            rows.append({"model": model, "configs": n_cfg, "calls": c["calls"] * n_cfg, "usd": round(usd * n_cfg, 2)})
            total_usd += usd * n_cfg
            total_calls += c["calls"] * n_cfg
        quote[name] = {
            **d,
            "per_config": c,
            "codex_family": rows,
            "total_calls": total_calls,
            "total_usd": round(total_usd, 2),
            "candidates_to_generate": d["pairs"],
        }
    print(json.dumps(quote, indent=2))


if __name__ == "__main__":
    main()
