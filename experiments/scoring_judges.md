# Implementation Specification for Judge Certification Properties

This document provides a detailed, step-by-step guide for implementing the seven certification properties used to calculate the Judge Trust Index (JTI).

---
### **P1: Reflexivity & Consistency**

This property score, $P_1$, quantifies the most fundamental requirement for a trustworthy judge: its ability to correctly identify a perfect match.

* **Motivation:** A judge that fails to recognize that a file is identical to itself is fundamentally broken. This is the "zero calibration" for the judge. We use the **mean** to be highly sensitive to any failure, as any deviation from a perfect score on this simple test is a critical signal.

* **Algorithm:**
    1.  **Select Sample:** Choose a diverse sample of $N$ gold-standard files $\{X_1, \dots, X_N\}$ from the VeriBench dataset.
    2.  **Run Reflexivity Check:** For each file $X_i$, run the judge with that file as both the candidate and the gold reference: `score_i = Judge(candidate=X_i, gold=X_i)`.
    3.  **Collect Scores:** Store the list of $N$ raw scores.

* **Scoring:**
    The $P_1$ score is the mean of the normalized scores.
    $$
    P_1 := \text{mean}\left(\frac{\text{scores}}{\text{max\_score}}\right)
    $$

* **Pros & Cons:**
    * **Pro:** It's a simple, non-negotiable sanity check. A low P1 score is an unambiguous signal that the judge is flawed.
    * **Pro:** Using the `mean` makes the metric highly sensitive to any failure, which is appropriate for such a fundamental test.
    * **Con:** It only tests the most trivial case (a perfect match). A judge can pass this test perfectly but still fail at evaluating nuanced, imperfect submissions.

---
### **P2: Monotonicity to Bugs**

This property score, $P_2$, measures whether the judge's score reliably decreases as the number of semantic bugs in a program increases.

* **Motivation:** A trustworthy judge must be sensitive to errors. This ensures the judge is evaluating semantic correctness, not superficial features.

* **Algorithm:**
    1.  **Create Bug Ladders:** Programmatically inject $k = 0, 1, \dots, K$ cumulative bugs into a sample of correct files.
    2.  **Run Test:** Run the judge on each perturbed file, comparing it against its original gold file.
    3.  **Calculate AUC:** Calculate the Area Under the Curve ($\text{AUC}_{\text{bugs}}$) for the task of ranking less-buggy files over more-buggy files.

* **Scoring:**
    $$
    P_2 := 2 \cdot (\text{AUC}_{\text{bugs}} - 0.5)
    $$

* **Pros & Cons:**
    * **Pro:** Directly tests the judge's sensitivity to **correctness**, a core requirement for an evaluator.
    * **Pro:** Using AUC provides a robust, scale-invariant measure of ranking quality.
    * **Con:** The quality of this test depends on the realism of the injected bugs. If the bugs are too simplistic, the test may not reflect the judge's performance on real-world errors.

---
### **P3: Monotonicity to Missing Specs**

This property score, $P_3$, measures whether the judge's score reliably decreases as key components of the formal specification are removed.

* **Motivation:** A trustworthy judge must value **completeness**. This property ensures the judge penalizes submissions for missing important theorems or tests.

* **Algorithm:**
    1.  **Create Ablation Ladders:** Create versions of complete, gold-standard files with $m = 0, 1, \dots, M$ theorems or tests removed.
    2.  **Run Test:** Run the judge on each ablated file, comparing it against the original gold file.
    3.  **Calculate AUC:** Calculate the $\text{AUC}_{\text{miss}}$, measuring the probability that the judge ranks a more complete specification higher.

* **Scoring:**
    $$
    P_3 := 2 \cdot (\text{AUC}_{\text{miss}} - 0.5)
    $$

* **Pros & Cons:**
    * **Pro:** Directly tests the judge's sensitivity to **completeness**, which is critical for formal verification.
    * **Con:** It assumes that removing any theorem makes a specification strictly "worse," which may not be true for redundant or trivial theorems.
    * **Con:** Like all properties, it measures completeness relative to the gold standard, not in an absolute sense.

---
### **P4: Low Variance (Stability)**

This property score, $P_4$, measures the consistency of the judge's scores for the same input across multiple repeated runs.

* **Motivation:** This property ensures the judge is a reliable and repeatable instrument, producing a dependable signal rather than random noise.

* **Algorithm:**
    1.  **Select Sample:** Choose a fixed, diverse set of `(candidate, gold)` pairs.
    2.  **Repeat Scoring:** For each pair, call the LLM judge $R$ times (e.g., $R=5$ or $R=10$).
    3.  **Calculate Variance:** Compute the average variance ($\sigma^2$) of the scores across all pairs.

* **Scoring:**
    $$
    P_4 := \text{clip}(1 - \sigma^2 / \tau^2, 0, 1)
    $$

* **Pros & Cons:**
    * **Pro:** Directly measures the reliability of the judge's score, which is essential for any scientific measurement.
    * **Con:** It only measures consistency, not correctness. A judge can be perfectly stable but consistently wrong.
    * **Con:** It increases computational cost, as it requires running the judge multiple times on each sample.

---
### **P5: Gaming & Tamper Resistance**

This property score, $P_5$, measures the judge's robustness against adversarial, meaning-preserving changes designed to manipulate evaluation scores.

* **Motivation:** A judge might overfit to superficial syntactic patterns. This test ensures the judge scores based on semantic substance, not easily gameable stylistic features.

* **Algorithm:**
    1.  **Create Tampered Versions:** For a sample of gold-standard files, create "tampered" versions using techniques like format standardization or pattern injection.
    2.  **Run Test:** Score both the original and tampered versions against the gold reference.
    3.  **Calculate Average Difference:** Compute the average absolute difference between the scores of original and tampered files.

* **Scoring:**
    $$
    P_5 := \text{clip}\left(1 - \frac{\text{average\_difference}}{\text{tolerance}}, 0, 1\right)
    $$

* **Pros & Cons:**
    * **Pro:** Directly tests for a known failure mode of LLM judges, ensuring robustness against bad-faith actors.
    * **Con:** The test is limited to a predefined set of tampering techniques and does not guarantee robustness against novel attacks.

---
### **P6: Correlation with Human Scores**

This property score, $P_6$, provides **external validity** by measuring how well the judge's scores align with the judgments of human experts.

* **Motivation:** A high correlation provides strong evidence that the judge is a credible proxy for human evaluation, capturing the nuanced aspects of quality that experts value.

* **Algorithm:**
    1.  **Collect Human Ratings:** Have human experts rate a diverse sample of candidates on the same scale as the LLM judge.
    2.  **Run LLM Judge:** Have the LLM judge score the same set of candidates.
    3.  **Calculate Correlation:** Compute the Spearman's rank correlation ($\rho$) between the human and LLM scores.

* **Scoring:**
    $$
    P_6 := \frac{\rho + 1}{2}
    $$

* **Pros & Cons:**
    * **Pro:** This is the gold standard for validating a proxy metric, ensuring it aligns with the ultimate ground truth: expert human judgment.
    * **Con:** This is by far the most expensive, time-consuming, and difficult property to measure, as it requires access to domain experts.
    * **Con:** Human scores can also be subjective and noisy.

---
### **P7: Correlation with Prover Success**

This property score, $P_7$, provides **criterion validity** by measuring how well the judge's scores predict a hard, objective outcome.

* **Motivation:** This test grounds the judge's abstract "quality" score in the practical reality of formal verification. A high correlation proves that a high score is a meaningful predictor of success.

* **Algorithm:**
    1.  **Generate a Dataset:** Create a large set of candidate specifications.
    2.  **Run Prover:** For each candidate, get a proof success rate from an automated theorem prover.
    3.  **Run LLM Judge:** Score the same set of candidates for quality.
    4.  **Calculate Correlation:** Compute the Spearman's rank correlation ($\rho$) between the judge's scores and the prover success rates.

* **Scoring:**
    $$
    P_7 := \frac{\rho + 1}{2}
    $$

* **Pros & Cons:**
    * **Pro:** Validates the judge against a completely objective, machine-checked outcome, removing human subjectivity.
    * **Con:** Proof success can be a noisy signal; a failure might mean a theorem is hard, not wrong.
    * **Con:** A judge could learn to reward simple, easy-to-prove theorems over more complex but important ones, which could artificially inflate this correlation.