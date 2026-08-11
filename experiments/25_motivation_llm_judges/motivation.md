# Motivation for Cert-Judge
ref: /Users/sanmikoyejo-mba-1/cert-judge/experiments/20/motivation.md

Q1: why LLM judges for this task -- evaluating if the AI entity generated the "correct" specs for our benchmark/task?



---

Q2: When are LLM judges needed in general?
- when the response is open ended (ie "anything") so it's like a set inclusion. Given the output, is it in the set of accepted answers? 
    this can be done with
    - i. (in benchmarks/evals) llm_judge(x, y_hat, y*) ie given the gold reference, can it help us know if y_hat is a valid response (eg in the set of valid responses)
    - ii. (in benchmarks/evals AND the wild) ll_judge(x, y_hat, rubric/rules) ie givent he models prediction y_hat to the prompt x (note this doesn't necesserily need to be given to the model but likely helps obviously this would need to be checked), 

PS: I'm defining "the wild" (though it would be good/better to find the accepted terminology for this/"proper") for what is done in "practice/wild" -- ie a user is generating a lot of shit from an AI and it just wants to know it's all actually correct ie it's not a benchmark, its a user actually using it and wanting to know if the output is trustworthy eg (making it up) by running another "certified" LLM that validates the output -- I think this is what people really mean with scalable oversight.