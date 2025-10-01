/-!
# VeriBench – Gold Example: Verified Addition

File order:

1. Implementation
2. Unit tests (positive, edge, positive/negative test suite)
3. Pre‑condition prop
4. Exhaustive property prop and their theorems
5. Post‑condition prop (same order as property props)
6. Correctness theorem `Pre → Post`
7. Imperative implementation, tests, and equivalence theorem

All real proofs are left as `sorry` for the learner / model.

# Implementation

## Custom Addition

Defines a wrapper `myAdd` for `Nat.add`, introduces an infix `++`,
and states basic algebraic properties.-/

namespace MyAdd

/--
**Implementation of `myAdd`.**

`myAdd a b` returns the natural‑number sum of `a` and `b`.

## Examples

#eval myAdd 1 2 -- expected: 3
-/
def myAdd : Nat → Nat → Nat := Nat.add
infixl:65 " ++ " => myAdd    -- left‑associative, precedence 65

/-!
# Tests
-/

/-- expected: 3 -/
example : myAdd 1 2 = 3 := by native_decide
#eval myAdd 1 2 -- expected: 3

end MyAdd
