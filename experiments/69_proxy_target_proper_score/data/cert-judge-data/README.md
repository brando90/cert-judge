# cert-judge-data inventory (reconnaissance, 2026-11-26)

Collected 2026-11-26 around 15:36 America/Los_Angeles (Pacific).
This is a local snapshot for CloudAgent / analysis planning. No repo was cloned; files were fetched with curl from public GitHub raw URLs (commit `460466dd` on `brando90/trustworthy-theorem-judges`). No emails or Slack messages were sent. No cert-judge code was modified.

## Official source of the new human data

The collection owner is **not** `cert-judge`. It is:

https://github.com/brando90/trustworthy-theorem-judges/tree/main/experiments/09_prepare_packets_and_collect_human_ratings_start_28Sep2026

Latest live sync commit (author listed as Brando Miranda / `brando90`):
https://github.com/brando90/trustworthy-theorem-judges/commit/460466dd10b735c5ff25f9e9cb21f0441fcf960b

- Commit time: 2026-11-26 15:30 America/Los_Angeles (23:30 UTC)
- Sheet readback in the experiment README: 2026-11-26 15:29 America/Los_Angeles
- Message: "Exp 09 live sync (11-26-2026): 250 main numeric ratings across 6 active raters (T05, T06, T08, T12, V02, V04)"
- Packet: 100 Lean files = 25 tasks x 4 frontier agents (GPT-6 Astra / Codex, Claude Fable 5.1 / Claude Code, Grok 4.7 / Grok CLI, Gemini 4 Argon / Antigravity). Scale is `final_score_0_5` (0-5).
- Progress: **250 of 3300** main scores (33 invited raters x 100 files). Two raters are complete (Sri T05, Amy T08).

The same 250-count was already used in theorem-judges Exp 25 on 2026-11-24 19:12 PT and in cert-judge Exp 67/68 (then described as 247 non-A1 ratings earlier on 11-24). Today's commit mainly **revises** existing rows (Sri's 100-row CSV was fully rewritten after his 11-24 / 11-25 "updated the sheet with the fixes" emails) and refreshes Nikil/Vaibhav exports. The planned 11-25 18:00 PT rating wave did **not** add a new completed rater (AGI log and the live table still show 250).

## Local paths

### New main ratings (this snapshot)
`ttj-exp09-live-sync-2026-11-26/ratings/`

Schema (name-first; 16 columns):
`rater_name, rater_id, item_id, task_folder, candidate_file, A_key_gold_theorems_covered (Y/N), B_gold_pre_postconditions_preserved_or_strengthened (Y/N), C_obvious_theorem_spam (Y/N), D_spam_handful_or_dominates (none/handful/dominates), final_score_0_5, ai_assisted_rating_attestation (AI help is allowed), minutes_spent, confidence, problem_note, rationale (optional), source_label`

| File | Rater | ID | Scored / 100 | Score counts (0-5) | AI attestation on scored rows | Sheet (live) |
|---|---|---|---:|---|---|---|
| `Srivatsava_Daruru_Sri__native_main_T05.csv` | Srivatsava Daruru (Sri) | T05 | 100 | 5:61, 4:25, 3:11, 1:3 | 100 yes | https://docs.google.com/spreadsheets/d/163ZxKeTXqseLrmwY-b5QjqeBulinHsZAiAPo1zsJdJI/edit |
| `Amy_Lu__native_main_T08.csv` | Amy Lu | T08 | 100 | 5:85, 4:10, 3:2, 1:3 | 100 partial | https://docs.google.com/spreadsheets/d/1YLq64komUf0lD8fdChDYeTZS--zpulbn-XTVhLWVUlE/edit |
| `Rakshit_Kaushik__native_main_T12.csv` | Rakshit Kaushik | T12 | 30 | 5:21, 4:6, 3:1, 2:1, 1:1 | 30 blank | https://docs.google.com/spreadsheets/d/1rHhh1sCq_Trzlda3fRu-RXES9QG_M1Wb0CzP6Utj7eQ/edit |
| `Donald_Poindexter_Jr__native_main_T06.csv` | Donald Poindexter Jr | T06 | 16 | 5:16 | 15 yes, 1 blank | https://docs.google.com/spreadsheets/d/1l_zdHObt3_0hd0MJkIJ5btU51hxNsHKwHyBUv0cuSLg/edit |
| `Vaibhav_Mahajan__native_main_V04.csv` | Vaibhav Mahajan | V04 | 3 | 5:2, 4:1 | 3 yes | https://docs.google.com/spreadsheets/d/1J7t7N2pd19PnJTrkPq3AIHytEWmtz1HxXdVKnNCpr2g/edit |
| `Nikil_Ravi__native_main_V02.csv` | Nikil Ravi | V02 | 1 | 3:1 | 1 blank | https://docs.google.com/spreadsheets/d/1iuxZBCPDm0LMSZ2iAgiB9twyHoThcQMPPOGx4eTBnGc/edit |

**Combined 250 main scores:** 5:185 (74%), 4:42, 3:15, 2:1, 1:7, 0:0. Strong ceiling / leniency. Attestations: 118 yes, 100 partial, 32 blank. Coordinator flag in Exp 09 README: preserve attestations verbatim; 100 "partial" are non-dropdown free text.

Also saved:
- `ratings/SUMMARY.json`, `ratings/RAW_MANIFEST.json`, `ratings/README.md`
- `docs/EXP09_README.md` (includes the live 33-rater table)
- Warm-up copies already scored earlier: Sri T05 6/6, Rylan T01 6/6, Yegor T02 3 numeric + 3 N/A

Unscored main CSVs for the other invited raters remain in the public repo under the same `ratings/` folder (0/100 each, including Brando A1). They were not all copied here to keep the snapshot focused on returned scores. Max Sieb (`T30`) is not in the auto table (Sheets OAuth 401 on 11-26).

## Older / already-in-repo human labels (not "new")

These predate the Nov 2026 set-N / native-100 collection and already live in `brando90/cert-judge`:

- `experiments/human_labels/` — VeriBench participants 1-5 TSVs plus harsh/lenient sets; used in the paper panel / Exp 41 / Exp 67 "old" 59-artifact corrected labels (4-5 ratings each).
- `experiments/ethan_hand_labels/` — Ethan's earlier split-wise hand labels (easy / CS / HumanEval / real_code / security).

Cert-judge Exp 67/68 already re-scored the old panel against those corrected labels and against an earlier 247-rating new-set snapshot. They did **not** yet have judge scores on the 100 new files.

## Source-by-source search notes

| Source | Result |
|---|---|
| Bot attachments path `/cursor/stores/store-53b9a6ba-e4a3-47fe-a32a-a73ca55c3d70/grok-bot/agents/c824872d-d5ff-469c-bbe5-ca5598373b80/attachments/` | Directory did not exist (store was empty). No files. |
| `brando90/trustworthy-theorem-judges` Exp 09 | **Canonical new data**, 250 main scores, live-synced today. |
| `brando90/cert-judge` `data/` and `experiments/human_labels/` | Older labels only; no new rater drop since Exp 67 (11-24). No open issues/PRs. |
| Gmail (`user-Gmail`) | Rating-task emails went out 11-17/11-18 to the 32-person list. Completions/discussion: Sri updated his Sheet 11-24 ~16:56-17:47 PT (and used an agent-built labeling artifact). John Sarracino emailed scoring questions 11-24/11-25 (table still 0/100). Weston Kirk declined 11-20. Leni Aniva first said she would try, then on 11-25 14:26 PT said her advisor told her not to. No new rating CSVs arrived as email attachments; scores are in the Google Sheets. `user-Gmail--science` and `user-Gmail-xai` were not fully paged. |
| Google Drive (`user-Google Drive-xai`) | All rater Sheets are owned by Brando and readable. Most recently modified scored sheets: Sri (11-24 17:43 PT), Vaibhav (11-24 16:35 PT), Nikil (11-24 15:54 PT), Don (11-23 19:06 PT), Amy (11-23 16:56 PT), Rakshit (11-23 00:44 PT). `user-Google-drive` recent files today were corr-vs-CE Exp 35 math notes, not new ratings. |
| Slack (`user-Slack` / ultimatebrandoshq) | No rater-submitted rating files found after 11-01. One 11-20 assistant DM noted Slava and Weston could not rate (pool two short). Stanford (`user-Slack--brando9-stanford-edu`) and Vals (`user-Slack--vals`) were not exhaustively searched. |
| Notion (`user-Notion`) | No new human-rating datasets; older VeriBench notes only. |

## Analysis caveats for any follow-up experiment

- 74% of new scores are 5; T06 is 16/16 fives. Correlation with a judge will be compressed. Use RPS / CE / TVD against the empirical rating distribution, not Spearman as the objective.
- Sri attested "yes" to AI assistance on all 100 rows (he also emailed that he used agents to build a labeling artifact). Amy marked all 100 "partial". Treat as allowed-but-disclosed assistance, not as unassisted expert labels, and keep the attestation column in every analysis.
- None of the 100 new files has a cert-judge score yet (Exp 67). Proxy-vs-target experiments on this set need new judge calls or must stay on the old 59-artifact panel.
- Do not raw-pool old (mean rating ~3.05) and new (mean ~4.57) items; Exp 67 showed a spurious pooled Spearman +0.50 that flips negative under within-set ranks.
