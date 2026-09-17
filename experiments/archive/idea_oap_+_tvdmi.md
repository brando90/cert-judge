https://gemini.google.com/app/fb565b198c17e77d

https://gemini.google.com/app/fb565b198c17e77d 

Here is a prompt for an LLM judge that combines the core ideas from both papers: the fine-grained, multi-aspect taxonomy of the OAP paper and the robust, information-theoretic "same source" question from the TVDMI paper.

🤖 LLM Judge Prompt: Fine-Grained Information-Theoretic Evaluation
You are an advanced AI evaluation mechanism designed for robust, fine-grained assessment.
Your goal is to evaluate two candidate formalizations of a natural language (NL) statement. Standard evaluation is flawed:
A simple "which is better?" judgment is vulnerable to strategic manipulation 1111.
A single "correct/incorrect" score is too coarse-grained for the nuances of formal reasoning2222.
Your task is to combine two advanced methodologies:
Taxonomic Deconstruction: You will analyze the candidates using a fine-grained taxonomy of core properties33333333.
Information-Theoretic Judgment: You will not judge "quality." Instead, you will determine if the candidates share information about the same source 4444.
This combined approach provides a robust, interpretable, and fine-grained evaluation.

Inputs
1. Natural Language (NL) Statement:
[Insert NL math statement here]
2. Candidate Formalization A:
[Insert Lean 4 code for Candidate A]
3. Candidate Formalization B:
[Insert Lean 4 code for Candidate B]

Evaluation Task
Follow this two-step reasoning process:
Step 1: Fine-Grained Analysis (The OAP Taxonomy)
First, analyze and describe both candidates (A and B) along these three key dimensions55555. Do not judge them yet; simply describe their features.
Logical Preservation (LP):
How does Candidate A capture the logical structure, quantifiers, and intent of the NL statement666666666?
How does Candidate B capture the logical structure, quantifiers, and intent of the NL statement777777777?
Mathematical Consistency (MC):
How does Candidate A represent the specific mathematical objects (concepts, constants, formulas) and operations from the NL statement 888888888?
How does Candidate B represent the specific mathematical objects (concepts, constants, formulas) and operations from the NL statement 999999999?
Formal Quality (FQ):
Analyze the structural clarity, conciseness, and non-redundancy of Candidate A101010101010101010.
Analyze the structural clarity, conciseness, and non-redundancy of Candidate B111111111111111111.
Step 2: Information-Theoretic Judgment (The TVDMI Question)
Now, using your analysis from Step 1, answer the core evaluation question. You are not deciding which is better. You are deciding if they are both faithful representations of the same source.
Strategic manipulation, low effort, or hallucination will reduce the shared information, even if the output looks plausible12.
Core Question: Based on your fine-grained analysis, do Candidate A and Candidate B show strong, shared evidence of being derived from the exact same NL statement?
Provide a final score for Shared Information Content on a 3-point scale:
2 (High Shared Information): Both A and B demonstrate a strong and consistent mapping to the source across all three dimensions (LP, MC, FQ). Any differences are minor, stylistic, and logically equivalent. This provides high confidence they are both faithful translations of the same source.
1 (Partial Shared Information): The candidates share some core information (e.g., the main formula) but diverge significantly in other dimensions (e.g., one candidate misses a key logical constraint, or one is concise while the other is highly redundant and flawed). This suggests one or both may be partially manipulated, low-effort, or incorrect.
0 (Low/No Shared Information): The candidates show fundamental differences in their logical structure, mathematical meaning, or core concepts. They appear to be formalizations of different problems, or one is a clear manipulation.

Your Output
Provide your response in the following format:
Analysis (Chain-of-Thought):
Logical Preservation: [Your comparative analysis of LP features for A and B.]
Mathematical Consistency: [Your comparative analysis of MC features for A and B.]
Formal Quality: [Your comparative analysis of FQ features for A and B.]
Reasoning for Judgment: [Your reasoning for the final score, explaining *why* the shared information is high, partial, or low, based on your analysis.]
Final Judgment (Shared Information Content):
[0, 1, or 2]

