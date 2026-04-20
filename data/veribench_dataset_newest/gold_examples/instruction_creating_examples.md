# VeriBench Lean-4 Data Point Instructions
	
   1.	Copy the skeleton below 
Replace names, types, and bodies, but **must keep** every section header, blank line, and /-- … -/ docstring.
If a def, example, or theorem is missing its docstring, the parser won't get the docstring (strict requirement).
	2.	Sections (please stay in this order)
Implementation header · namespace · functional def (with ## Examples) · # Tests · # Tests: Edge Cases · # Theorems · imperative def (with its own docstring) · # Imperative Tests · # Imperative Tests: Edge Cases · equivalence theorem · end.
	3.	Use #eval … -- expected: …, leave proofs as sorry, add @[simp] where helpful.

There are three gold references here: `~/veribench/veribench_dataset/lean_src/veribench/gold_examples that I think are consistent`.

Here is one gold reference:
```lean
/-!
# Implementation

## Custom Addition

Defines a wrapper `myAdd` for `Nat.add`, introduces an infix `++`,
and states basic algebraic properties.
-/

namespace MyAdd

/--
Implementation of `myAdd`.

`myAdd a b` returns the natural-number sum of `a` and `b`.

## Examples

#eval myAdd 1 2 -- expected: 3
#eval myAdd 0 0 -- expected: 0
-/
def myAdd : Nat → Nat → Nat := Nat.add

infixl:65 " ++ " => myAdd    -- left-associative, precedence 65

/-!
# Tests
-/

/-- expected: 3 -/
example : myAdd 1 2 = 3 := by native_decide
#eval myAdd 1 2 -- expected: 3

/-!
# Tests: Edge Cases
-/

/-- expected: 0 -/
example : myAdd 0 0 = 0 := by native_decide
#eval myAdd 0 0 -- expected: 0

/-!
# Theorems
-/

/-- **Right-identity**: adding zero on the right leaves a natural number unchanged. -/
@[simp] theorem add_right_identity (n : Nat) : myAdd n 0 = n := sorry

/-- **Left-identity**: adding zero on the left leaves a natural number unchanged. -/
@[simp] theorem add_left_identity (n : Nat) : myAdd 0 n = n := sorry

/-- **Commutativity**: the order of the addends does not affect the sum. -/
@[simp] theorem add_commutativity (m n : Nat) : myAdd m n = myAdd n m := sorry

/-- **Associativity**: regrouping additions does not change the result. -/
@[simp] theorem add_associativity (a b c : Nat) :
  (a ++ b) ++ c = a ++ (b ++ c) := sorry

/-- **Right-distributivity**: `(a + b) + c = a + (b + c)`. -/
@[simp] theorem add_right_distrib (a b c : Nat) :
  myAdd (myAdd a b) c = myAdd a (myAdd b c) := sorry

/-- **Left-distributivity**: `a + (b + c) = (a + b) + (a + c)`. -/
@[simp] theorem add_left_distrib (a b c : Nat) :
  myAdd a (myAdd b c) = myAdd (myAdd a b) (myAdd a c) := sorry

/--
`myAddImp a b` computes the same sum using a mutable accumulator.
-/
def myAddImp (a b : Nat) : Nat :=
  Id.run do
    let mut acc : Nat := a
    for _ in [0 : b] do
      acc := acc.succ
    return acc

/-!
# Imperative Tests
-/

/-- expected: 3 -/
example : myAddImp 1 2 = 3 := by native_decide
#eval myAddImp 1 2 -- expected: 3

/-!
# Imperative Tests: Edge Cases
-/

/-- expected: 0 -/
example : myAddImp 0 0 = 0 := by native_decide
#eval myAddImp 0 0 -- expected: 0

/-- **Equivalence**: functional and imperative addition coincide. -/
theorem myAdd_equivalence (a b : Nat) :
  myAdd a b = myAddImp a b := sorry

end MyAdd
```
Use this blueprint for every VeriBench Lean task.
Nothing extra, nothing missing.
