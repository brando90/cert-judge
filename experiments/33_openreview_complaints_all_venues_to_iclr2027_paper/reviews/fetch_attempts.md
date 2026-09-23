# fetch_attempts.md — every attempt to retrieve OpenReview content (09-22-2026)

**TLDR:** The OpenReview search API is reachable anonymously and located every version of the paper, but forum, note and reply endpoints (API v1, API v2, the HTML forum page, and WebFetch) all return OpenReview's "Challenge verification required" / "Verifying your browser" wall, which needs a logged-in browser. Brando's Gmail (the account the agent can read) holds no OpenReview mail at all, and no DL4C review text exists on disk. Result: DL4C (`gGR1gE7x3a`) reviews and the verbatim TMLR desk-reject note are missing; everything else is captured from files already in the repo. Nothing was fabricated.

| # | Time (PDT) | Target | Method | Outcome |
|---|---|---|---|---|
| 1 | 14:59 | `api2.openreview.net/notes/search?term=CertJudge` | curl, anonymous | OK: 1 hit, forum `xmHP3UhGQ8` (ICML 2026 AI4Math Poster) |
| 2 | 14:59 | `…/notes/search?term=Falsifiable Properties LLM judge Lean` | curl, anonymous | OK: forum `gGR1gE7x3a` (ICML 2026 DL4C Poster) found; no other venue for this paper among 20 hits |
| 3 | 14:59 | `…/notes/search?term=Certifying the Judge` / `Trusting the Formal Judge` | curl, anonymous | 0 hits (search index ignores quoted phrases) |
| 4 | 15:00 | `api2.openreview.net/notes?forum=<id>` for `xmHP3UhGQ8`, `9WAWDdwqpC`, `WKVtlskjeQ` | curl, anonymous | 403 `ChallengeRequiredError` (browser challenge) |
| 5 | 15:00 | `…/notes?content.venueid=ICML.cc/2026/Workshop/DL4C` (also AI4Math, MATH-AI 2025) and `…/invitations?prefix=…DL4C` | curl, anonymous | 403 `ChallengeRequiredError` |
| 6 | 15:03 | `api2.openreview.net/notes?forum=gGR1gE7x3a`, `notes?id=`, `notes?replyto=`, API v1 `api.openreview.net/notes?forum=` | curl, anonymous | 403 `ChallengeRequiredError` on all four |
| 7 | 15:05 | `https://openreview.net/forum?id=gGR1gE7x3a` | curl with browser user agent | 4.8 KB page titled "Verifying your browser \| OpenReview"; no note content |
| 8 | 15:05 | same URL | WebFetch tool | Same verification page: "Have an OpenReview account? Sign in to skip this check." |
| 9 | 15:06 | `…/notes/search?term=gGR1gE7x3a&source=all|reply|forum` and `term=Certifying the Judge Falsifiable&source=reply|forum` | curl, anonymous | `source=all` returns only the submission note (invitations `…/DL4C/-/Submission`, `…/Submission105/-/Revision`); reply sources return 0 |
| 10 | 15:04 | Gmail search `openreview DL4C ("Certifying the Judge" OR review OR decision OR metareview)` | Gmail MCP (brandojazz@gmail.com) | 0 threads |
| 11 | 15:04 | Gmail search `from:openreview.net (… titles …)` and `from:openreview.net newer_than:400d` | Gmail MCP | 0 threads: this mailbox receives no OpenReview notifications (they go to another address) |
| 12 | 15:06 | Local disk: `~/cert-judge-autojudge-human-corr-val-test`, `~/Downloads`, `~/Desktop`, `find ~ -maxdepth 3 -iname '*openreview*' -o -iname '*dl4c*'` | shell | Only the submitted PDFs (`105_Certifying_the_Judge_Falsi.pdf`, `109_CertJudge_Evaluating_Lean_.pdf`) and the VeriBench paper's own DL4C folders; no cert-judge DL4C review text anywhere |
| 13 | 15:05 | git history: `git log --all -i --grep=review`, `git grep DL4C` | shell | No commit or file carries DL4C review text; `18_icml_2026_reviews/pre_prompt.md` is the only ICML capture (AI4Math) |

## Captured without fetching (already in the repo)

- NeurIPS 2025 MATH-AI (`9WAWDdwqpC`): `experiments/archive/02_neurips_reviews/or_neurips_2025_math_ai_workshop/or_reviews.md` → copied to `neurips2025_mathai_9WAWDdwqpC.md`.
- ICML 2026 AI4Math (`xmHP3UhGQ8`): `experiments/18_icml_2026_reviews/pre_prompt.md` → copied to `icml2026_ai4math_xmHP3UhGQ8.md`.
- TMLR desk reject (`WKVtlskjeQ`): paraphrase and quoted fragments in `experiments/archive/21_tmlr_submission/` → `tmlr2026_desk_reject_WKVtlskjeQ.md`.

## Not found (searched, absent)

- No NeurIPS 2026 main-track or ICLR 2026 submission of this paper: the `paper_latex/archive/NeurIPS_2026` tree was ported into the ICML 2026 workshop format on 05-15-2026 (commit `b1a81d9`) and the OpenReview search shows only the two ICML 2026 workshop forums.

## What Brando must supply

1. The DL4C review text (paste into `icml2026_dl4c_gGR1gE7x3a.md`).
2. Optionally the verbatim TMLR EiC note (paste into `tmlr2026_desk_reject_WKVtlskjeQ.md`).
