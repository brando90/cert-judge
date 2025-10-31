from typing import Any, Dict


def diff_test_lean4(agent_lean4_file: str, gold_lean4: str) -> Dict[str, Any]:
    """ 
    main hypothesised challenge: some thms are computable ("convertible to tests eg pbts") while others are not.

    proposed algorithm to run differential testing for two lean files:
    1. i. first run a ATP on it (eg lean-smt, clark's lean-auto or something (hard to use), aesop, leanhammer, grind, ring_nf, linarith, anything else?)
        1.ii. if succeeds then the theorems is true.  

    Q: how do I convert a general property/theorem to a runnable test? 

    diff testing option 2:
    1. run the ATP btw agent vs gold lean4 theorems O(n * m)

    just prove it with your llm. 
    """
    res: Dict = {
        "diff": True, # default to yes diff is safer to say they aren't the same
    }
    # 
    return res
