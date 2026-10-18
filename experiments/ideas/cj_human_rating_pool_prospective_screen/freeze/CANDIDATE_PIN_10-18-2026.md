# Candidate-file pin, 10-18-2026

**Doc link:** <https://github.com/brando90/cert-judge/blob/main/experiments/ideas/cj_human_rating_pool_prospective_screen/freeze/CANDIDATE_PIN_10-18-2026.md>

**TLDR:** 124 of the 125 wave-1 candidate files have a SHA-256 taken from experiment 109's sealed receipts on skampere3. One Mistral cell, `realcode_set/29_statistics_median_high`, has no file (`missing_output`). No model calls. A packet can name that cell as missing; it cannot substitute another file.

The five generators are Terminus 2 runs `t2_fable51`, `t2_astra`, `t2_kimik3`, `t2_glm` and `t2_mistral`. The hash is `collected_sha256` in `private/sealed/cells`. One spot check, Fable on `easy_set/21_is_palindrome`, matched the saved `solution.lean` byte for byte (`4c5f4506…`, 16,012 bytes).

Receipts: [CANDIDATE_PIN_10-18-2026.json](CANDIDATE_PIN_10-18-2026.json).
