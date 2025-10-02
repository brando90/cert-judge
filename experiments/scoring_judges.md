### **P1: Reflexivity & Consistency**

This property score, $P_1$, quantifies the most fundamental requirement for a trustworthy judge: its ability to correctly identify a perfect match and remain consistent against superficial, meaning-preserving changes.

* **Motivation: The Foundational Sanity Check**
    Before we can trust a judge to score complex, buggy, or incomplete specifications, we must first verify that it can pass the simplest possible test: recognizing that a file is identical to itself. This is the **reflexivity** check. If a judge fails this, its other scores are meaningless. Think of it like calibrating a scale: before you weigh anything, you ensure the scale reads exactly '0' when it's empty. The reflexivity test is our "zero" calibration for the judge. The **consistency** check extends this by ensuring the judge isn't fooled by cosmetic differences, like changes in code formatting or comments.

* **Algorithm**
    1.  **Reflexivity Check:** Select a diverse sample of $N$ gold-standard files $\{X_1, X_2, \dots, X_N\}$ from the VeriBench dataset. For each file $X_i$, run the judge with that file as both the candidate and the gold reference, i.e., `Judge(candidate=X_i, gold=X_i)`.
    2.  **Consistency Check (Optional, but recommended for robustness):** For each file $X_i$ in the sample, create a semantically identical but syntactically different version, $X'_i$, by applying meaning-preserving transformations like code reformatting or comment removal. Run the judge on the pair `Judge(candidate=X'_i, gold=X_i)`.

* **Scoring**
    The final $P_1$ score is calculated from the results of the reflexivity check. The median is used because it is robust to occasional outliers.
    $$
    P_1 := \text{median}(s(X,X))
    $$
    For a perfectly reflexive and consistent judge, the $P_1$ score will be **1.0**.

---

### **P2: Monotonicity to Bugs**

This property score, $P_2$, measures whether the judge's score reliably decreases as the number of semantic bugs in a program increases.

* **Motivation: Sensitivity to Correctness**
    A trustworthy judge must be sensitive to errors. It should reliably score buggier code worse than correct code. This ensures the judge is actually evaluating semantic correctness, not just superficial features like style or length. If a judge scores a file with five bugs higher than a file with one bug, its judgment on correctness is fundamentally flawed.

* **Algorithm**
    1.  **Create Bug Ladders:** For a sample of correct files, create a series of increasingly buggy versions by programmatically injecting $k = 0, 1, 2, \dots, K$ bugs.
    2.  **Run Test:** Run the judge on each perturbed file, comparing it against the original, correct gold file. This creates a dataset of `(number_of_bugs, score)` pairs.
    3.  **Calculate AUC:** For all pairs of submissions $(c_i, c_j)$ where $c_i$ has fewer bugs than $c_j$, calculate the Area Under the Curve ($\text{AUC}_{\text{bugs}}$). This measures the probability that the judge correctly ranks a less buggy file higher than a more buggy one.

* **Scoring**
    The formula rescales the AUC so that random performance (AUC = 0.5) maps to a score of 0, and perfect performance (AUC = 1.0) maps to a score of 1.
    $$
    P_2 := 2 \cdot (\text{AUC}_{\text{bugs}} - 0.5)
    $$
    For a perfectly monotonic judge, the $P_2$ score will be **1.0**.

---

### **P3: Monotonicity to Missing Specs**

This property score, $P_3$, measures whether the judge's score reliably decreases as key components of the formal specification (e.g., theorems, unit tests) are removed.

* **Motivation: Sensitivity to Completeness**
    Formal verification isn't just about the absence of bugs; it's also about the **completeness** of the specification. A program might be correct with respect to the few properties it proves, but it could be missing proofs for critical edge cases. A trustworthy judge must recognize and penalize this lack of thoroughness. This test ensures the judge values completeness.

* **Algorithm**
    1.  **Create Ablation Ladders:** For a sample of complete, gold-standard files, create a series of incomplete versions by removing $m = 0, 1, 2, \dots, M$ theorems or unit tests.
    2.  **Run Test:** Run the judge on each ablated file, comparing it against the original, complete gold file. This creates a dataset of `(number_of_missing_specs, score)` pairs.
    3.  **Calculate AUC:** Similar to P2, calculate the $\text{AUC}_{\text{miss}}$, which measures the probability that the judge ranks a more complete specification higher than a less complete one.

* **Scoring**
    The formula is identical in structure to P2's, rescaling the AUC to the range $[0, 1]$.
    $$
    P_3 := 2 \cdot (\text{AUC}_{\text{miss}} - 0.5)
    $$
    For a judge that perfectly values completeness, the $P_3$ score will be **1.0**.

---

### **P4: Low Variance (Stability/Robustness)**

This property score, $P_4$, measures the consistency of the judge's scores for the same input across multiple repeated runs.

* **Motivation: Reliability of the Instrument**
    An LLM judge, especially with a non-zero temperature, is a non-deterministic instrument. If it gives a score of 9/10 on one run and 4/10 on the next for the exact same input, its score is not a reliable signal but random noise. This property ensures the judge is a stable, dependable tool. A judge must be consistent to be trustworthy, though consistency alone isn't sufficient (a broken clock is consistent but wrong).

* **Algorithm**
    1.  **Select Sample:** Choose a fixed, diverse set of `(candidate, gold)` pairs.
    2.  **Repeat Scoring:** For each pair, call the LLM judge $R$ times (e.g., $R=5$ or $R=10$).
    3.  **Calculate Variance:** For each pair, calculate the variance ($\sigma^2$) of the $R$ scores. Then, compute the average variance across all pairs in your sample.

* **Scoring**
    This formula compares the judge's observed average variance ($\sigma^2$) to a pre-defined maximum acceptable variance, or tolerance ($\tau^2$).
    $$
    P_4 := \text{clip}(1 - \sigma^2 / \tau^2, 0, 1)
    $$
    If the judge is perfectly stable ($\sigma^2 = 0$), its score is $P_4=1$. If its variance equals or exceeds the tolerance ($\sigma^2 \ge \tau^2$), its score is clipped to $P_4=0$.