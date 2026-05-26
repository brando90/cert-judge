# AutoMetrics Summary And Cert-Judge Contrast
**TLDR:** AutoMetrics learns task-specific automatic evaluators from sparse human feedback by generating/retrieving metrics and fitting a regression to predict human labels. Cert-judge shares the goal of amortizing human validation, but certifies judge configurations through falsifiable Lean-aware properties rather than learning a new per-task metric from labels.

## Paper Metadata

- Paper: "AutoMetrics: Approximate Human Judgements with Automatically Generated Evaluators"
- Authors: Michael J. Ryan, Yanzhe Zhang, Amol Salunkhe, Yi Chu, Di Xu, Diyi Yang
- Source: [arXiv:2512.17267](https://arxiv.org/abs/2512.17267), submitted 2025-12-19
- Reported code release: [SALT-NLP/autometrics](https://github.com/SALT-NLP/autometrics)

## One-Paragraph Summary

AutoMetrics addresses evaluation for open-ended AI applications where human feedback is scarce and rubrics are underspecified.
Given a task description and fewer than 100 human feedback points, it generates candidate LLM-as-a-judge metrics, retrieves relevant existing metrics from a curated MetricBank of 48 NLP metrics, and fits a Partial Least Squares regression to combine the selected metrics into a predictor of human judgments.
The paper evaluates five tasks spanning simplification, dialogue helpfulness, product descriptions, code completion, and travel planning, reporting Kendall tau improvements over LLM-judge and other baselines, with the largest stated gain of 33.4% on EvalGen.
It also evaluates construct validity through sensitivity to quality-degrading perturbations and stability under quality-preserving perturbations, then uses AutoMetrics as an optimization reward in a tau-bench airline-agent case study.

## Key Method Points

- Generate: create task-specific LLM-judge criteria, rubric metrics, few-shot metrics, and prompt-optimized metrics.
- Retrieve: use MetricBank plus generated metrics, filtering candidates with a ColBERT + LLM retrieval process over metric cards.
- Regress: normalize metric outputs and fit PLS to select and weight metrics that predict human labels.
- Report: expose metric weights, correlations, examples, and caveats so practitioners can inspect the induced evaluator.
- Robustness: test whether the induced metric penalizes degraded outputs and remains stable under meaning-preserving edits.

## Main Empirical Claims Relevant To Us

- AutoMetrics improves Kendall tau against human ratings across five reported tasks, with the largest abstract/table claim being a 33.4% gain over LLM-as-a-judge on EvalGen.
- The authors report that performance tends to saturate around 80--100 feedback examples in their data-efficiency sweeps.
- In low-resource out-of-distribution settings, generated-only metrics can outperform using the full MetricBank because regression over many weak predictors can create spurious correlations.
- In the tau-bench case study, AutoMetrics is used as a proxy reward and is reported to match or exceed a verifiable reward in downstream optimization after 2000 GEPA rollouts.

## Limitations The Paper Acknowledges

- Metrics are partly model-coupled: generating metrics with one model and executing them with another can reduce performance.
- The learned evaluator only generalizes as far as the human data is representative.
- The high-p, low-n regression setting can produce spurious correlations, so the system warns when correlation significance is weak.
- The paper does not include a formal practitioner user study.

## Similarities To Cert-Judge

- Both papers treat human feedback as scarce and expensive, then try to amortize it.
- Both work in the LLM-as-a-judge space rather than relying only on static surface metrics.
- Both use validity language: criterion validity through human agreement and construct validity through perturbation behavior.
- AutoMetrics' sensitivity/stability tests are conceptually close to cert-judge's perturbation-based properties, especially monotonicity under degradations and stability under irrelevant changes.

## Differences From Cert-Judge

- AutoMetrics learns a metric for each open-ended application; cert-judge certifies whether a chosen judge configuration is reliable for Lean 4 theorem/specification scoring.
- AutoMetrics optimizes for human-label prediction using regression over generated and retrieved metrics; cert-judge scores behavioral properties such as identity, bug monotonicity, specification monotonicity, and repeat/prompt stability.
- AutoMetrics targets subjective and user-facing tasks such as travel planning or product descriptions; cert-judge targets formal-verification artifacts where gold Lean files, proof checking, bug ladders, and specification-ablation ladders give structured failure modes.
- AutoMetrics' labels are the training signal for the evaluator; cert-judge uses human labels as validation/calibration evidence that property scores predict human alignment across judge configurations.
- AutoMetrics answers "which metric should I use for this task?"; cert-judge answers "is this judge reliable enough to use for theorem-quality scoring?"

## Paper-Facing Takeaway

AutoMetrics is a complementary adaptive-evaluation system.
It is closest to cert-judge in its motivation, low-data human grounding, and sensitivity/stability validation, but the two systems amortize human effort along different axes.
AutoMetrics amortizes within a task by learning a metric from sparse labels.
Cert-judge amortizes across judge configurations by validating falsifiable properties that can be computed without collecting fresh labels for every new model, prompt, repeat count, or aggregation rule.
