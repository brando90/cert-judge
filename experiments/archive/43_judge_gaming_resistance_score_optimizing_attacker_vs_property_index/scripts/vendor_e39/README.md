# Vendored from experiment 39 (read-only copy)

Byte-identical copies of experiment 39's legacy prompt renderer and the paper's four legacy judge prompts, taken from
`origin/main` commit 84e1c0e (`experiments/39_label_free_proxy_index_train_val_test_over_judge_families/{scripts/legacy.py,prompts/*.txt}`),
so experiment 43 renders exactly experiment 39's prompt bytes without importing from (and writing bytecode into) experiment 39's folder.
`scripts/test_e43.py` checks that every file still matches experiment 39's bytes.
