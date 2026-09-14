# Future Steps and Recommended Next Experiments

## TL;DR

This project is already strong in its core idea: an LLM judge for Lean 4 theorem/specification quality is only useful if it can first be **behaviorally certified** against simple, falsifiable properties like identity and monotonicity. The next stage should focus on turning that core idea into a stronger and more robust evaluation framework.

The highest-leverage future work is:

1. **Cross-judge robustness** to show the conclusions are not specific to one judge model. The current paper/experiments leverage Claude 3.5 as well as GPT 4o-Mini. Be consistent with models and also correlate between different models where applicable.
2. **Adversarial judge-gaming tests** to stress whether the judge can be fooled by style, verbosity, or superficially plausible artifacts.
3. **Uncertainty-aware judging and abstention** so the judge can avoid overconfident failures.
4. **Per-split reliability analysis and stronger statistics** to quantify where the judge is reliable and where it is weak.
5. **Human validation** to connect certification-style behavioral checks to criterion validity with expert raters.

Together, these additions would make the paper stronger scientifically, more convincing to reviewers, and more useful as a general-purpose framework for certifying LLM judges in formal verification.

---

## Project Summary

The current paper argues that LLM-based judges can be useful for evaluating Lean 4 theorem/specification generation **if they are first validated against structured perturbation tests**. The current certification protocol checks whether the judge:

- gives the maximum score to identical artifacts,
- lowers scores as more semantic bugs are introduced, and
- lowers scores as more specifications are removed.

This is a compelling foundation, because it replaces vague claims of “judge quality” with explicit, falsifiable behavioral requirements. The most natural next step is to broaden this certification protocol so that it addresses the strongest likely reviewer questions:

- Does the result hold across different judge models?
- Can the judge be gamed?
- When is the judge uncertain?
- Is the judge equally reliable across all benchmark splits?
- Does the judge agree with human experts?

---

## Recommended Future Work

### 1) Cross-Judge Robustness Matrix

**Why it matters.**
The current evaluation is vulnerable to the critique that the conclusions may depend too heavily on one particular judge model or judge family. A cross-judge robustness experiment would test whether the certification results and downstream system rankings remain stable when the same protocol is run across multiple judge models.

**What to add.**

- `experiments/02_neurips_reviews/exp8_cross_judge_robustness.py`
- `experiments/02_neurips_reviews/utils/judge_registry.py`
- edit `experiments/02_neurips_reviews/run_all_experiments.sh`
- edit `experiments/02_neurips_reviews/SUMMARY.md`

**Outputs to generate.**

- `results/cross_judge/summary.json`
- per-model `summary.csv`
- pass/fail certification breakdown by judge
- score correlations and rank correlations across judges

**Possible paper artifact.**

- Table: **Certification by Judge Model**
- Heatmap: judge model × metric (`identity`, `spearman`, `weak_mono`, `certified`)

**Difficulty.**
Medium.

---

### 2) Adversarial Judge-Gaming Test Suite

**Why it matters.**
The current perturbation ladders mainly test clean degradation under bug injection or missing specifications. A stronger evaluator should also be robust to adversarial candidates that look good stylistically but are semantically weak or misleading.

**What to add.**

- `experiments/02_neurips_reviews/exp10_adversarial_gaming.py`
- `experiments/02_neurips_reviews/utils/adversarial_generator.py`
- optionally reuse `experiments/02_neurips_reviews/utils/sensitivity_sweep.py`

**Attack families to include.**

- verbose but vacuous theorem/spec statements
- redundant theorem splitting
- gold-like formatting with one subtle semantic flaw
- weak theorems that appear comprehensive
- test-overfitted artifacts that do not really capture the intended semantics

**Outputs to generate.**

- `results/adversarial/summary.json`
- attack-wise score inflation / false-positive rate
- rank inversions under adversarial artifacts
- confidence intervals over attack outcomes

**Possible paper artifact.**

- Heatmap: attack family × metric degradation
- Table: worst-case adversarial score inflation

**Difficulty.**
Medium.

---

### 3) Judge Uncertainty + Abstention Policy

**Why it matters.**
A judge is more useful in practice if it can detect when it is uncertain and abstain instead of making brittle or overconfident decisions. This is especially relevant for difficult splits like security or real-code settings.

**What to add.**

- edit `experiments/02_neurips_reviews/utils/judge_caller.py`
- add `experiments/02_neurips_reviews/utils/abstention.py`
- add `experiments/02_neurips_reviews/exp11_uncertainty_abstention.py`

**Uncertainty signals to compute.**

- standard deviation across repeated judge calls
- interquartile range
- vote entropy / score entropy
- optional confidence score checked against observed outcomes

**Outputs to generate.**

- `results/uncertainty_abstention/summary.json`
- risk-coverage curves
- retained-set certification metrics as abstention increases

**Possible paper artifact.**

- Figure: risk-coverage curve
- Table: performance at 0%, 10%, 20%, 30% abstention

**Difficulty.**
Low-Medium.

---

### 4) Per-Split Reliability Analysis + Unified Statistics with Confidence Intervals

**Why it matters.**
The paper’s current claims are strongest at the aggregate level. A more careful analysis should show where the judge is reliable and where it is not, split by split. This makes the results statistically harder to dismiss and provides a clearer picture of failure modes.

**What to add.**

- `experiments/02_neurips_reviews/utils/stats_core.py`
- `experiments/02_neurips_reviews/exp12_split_calibration.py`
- edit `experiments/02_neurips_reviews/utils/make_wandb_report.py`

**Metrics to standardize.**

- Pearson
- Spearman
- Kendall tau
- pairwise ordering accuracy / AUC
- bootstrap confidence intervals
- optional reliability bins / ECE-like measures

**Outputs to generate.**

- `results/split_calibration/summary.json`
- per-split confidence interval tables
- reliability plots by split

**Possible paper artifact.**

- Forest plot: split-level correlations with 95% CIs
- Reliability plot for Easy / CS / HE / Real / Sec

**Difficulty.**
Low-Medium.

---

### 5) Minimal Human-Validation Package

**Why it matters.**
The strongest external-validity addition would be a small but clean human study. Even a modest expert validation set would help bridge the gap between behavioral certification and real criterion validity.

**What to add.**

- `experiments/archive/03_human_validation/annotation_template.csv`
- `experiments/archive/03_human_validation/rubric.md`
- `experiments/archive/03_human_validation/analyze_human_agreement.py`
- optional wrapper: `experiments/02_neurips_reviews/exp9_human_validation_eval.py`

**What to measure.**

- inter-rater reliability among humans
- Spearman / Pearson correlation between judge score and human mean rating
- disagreement cases by split and difficulty
- bootstrap confidence intervals

**Outputs to generate.**

- `results/human_validation/summary.json`
- disagreement lists and human-vs-judge comparison tables

**Possible paper artifact.**

- Scatterplot: human mean vs judge score
- Table: inter-rater reliability + judge-human agreement

**Difficulty.**
Medium overall, though the main dependency is annotation time.

---

## Recommended Execution Order

To maximize impact while staying realistic, the suggested order is:

1. **Cross-judge robustness**
2. **Adversarial judge-gaming**
3. **Uncertainty / abstention**
4. **Per-split reliability analysis + CIs**
5. **Human validation** (start early due to annotation latency)

This ordering prioritizes additions that are fast to implement and most likely to strengthen reviewer confidence right away.

---

## What These Additions Would Strengthen

If completed, these future steps would strengthen the project along five dimensions:

- **Robustness:** the judge is not only monotone under clean perturbations, but stable across judge models and attack styles.
- **Reliability:** the system reports uncertainty instead of hiding it.
- **Statistical rigor:** results are reported with stronger and more complete metrics.
- **Interpretability:** split-wise reliability analysis reveals where the judge works best and where it needs caution.
- **Validity:** human comparison provides evidence that certification aligns with expert assessment.

---

## Closing Summary

The current project already has a strong core idea: **don’t trust an LLM judge by default—certify that it behaves sensibly first**. The most important future work is not to abandon that framing, but to deepen it.

The roadmap above keeps the same philosophy while making the work substantially stronger:

- broaden certification across judges,
- test robustness against gaming,
- expose uncertainty,
- quantify reliability more carefully, and
- connect judge behavior to expert human judgment.

If implemented, these steps would move the project from a promising certification protocol to a much more complete and credible framework for trustworthy LLM-based evaluation in formal verification.

## An aside on TVD-MI

TVD-MI is not the best immediate extension because we know it measures shared information, and not necessarily direct human correlation. The current paper is strongest when it stays focused on certifying a gold-reference-based judge via identity and monotonicity, whereas TVD-MI pushes toward a broader oracle-free or hybrid oversight framework that the draft explicitly describes as future work. That makes it valuable conceptually, but direct human correlation may be a better option.

## Additional questions:

- Methods for `Trace++` and `DSPy ReAct` agent. What is the standard agent/evaluation framework?
