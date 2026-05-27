# Scratch Notes: Ethan Autojudge Metric Prompt
**TLDR:** Brando suggested trying an autojudge metric-selection experiment that uses all available human judgments while avoiding overfitting. The key instruction is to select or tune on a validation split, then report correlation to human judgments only on a held-out test split.

## Message to Ethan

```text
Ethan Hersch — 11:36 AM
ok currently using all 5 human annotators we can get like 0.51 correlation
Vs .7+ from before
So might have to do some aggregation
Brando — 11:40 AM
not enough details for me to comment. Did you aggregate the individual grades and then treated that as the "ethan pass3" and then did the same analysis you previously did? That should "work" (higher corr) if our assumption that ur grades are similar to the mean grade holds
Ethan Hersch — 11:57 AM
yeha this was able to get 0.54 corr
Brando — 12:10 PM
there is no free lunch -- the reviewers will complain we only have 1 human (but good correlation). Or bad correlation but an excellent number of humans. Seems this paper autogenerates llm judges: https://arxiv.org/abs/2512.17267 . Ask codex to implement it for you and see if that gets a better judge with the val-test set split (sanmi was very concerned about this so make sure we do have that fixed; no overfitting and no p-hacking). We are in a good direction!

My suggestion:

copy paste this comment to codex.
tell it to use all human judgements for the correlations (5) + your pass1 + pass 2
tell it to split it in val vs test. I know we dicusssed the details of how to do this split. But just put in the prompt whatever decision we agreed last time or whatever u think is reasonable. Not freeze.
then do the autojudge metric algorithm to auto select a (not p-hacked judge) ie do training on train split then hyperparms if there are any chosen on var then report the test set correlation to humans.

I think that should be an excellent test to try 🙂

PS: use this msg/our conv to create the needed codex prompt 😉
```

## Instruction for Ethan

Put the Codex prompt and any implementation/results for this test in this folder:

```text
experiments/17_autojudge_human_corr_val_test/
```
