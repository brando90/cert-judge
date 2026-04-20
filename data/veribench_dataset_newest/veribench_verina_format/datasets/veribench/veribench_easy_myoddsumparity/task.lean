-- !benchmark @start import type=solution
import Mathlib
namespace MyOddSumParity
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- Returns the parity (0 or 1) of a natural number -/
def parity (n : Nat) : Nat := n % 2

/-- Sum all numbers in a list -/
def sumList : List Nat → Nat
  | [] => 0
  | x :: xs => x + sumList xs
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def myOddSumParity_precond (xs : List Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def myOddSumParity (xs : List Nat) (h_precond : myOddSumParity_precond (xs)) : Nat :=
  -- !benchmark @start code
  parity (sumList xs)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def myOddSumParity_postcond (xs : List Nat) (result : Nat) (h_precond : myOddSumParity_precond (xs)) :=
  -- !benchmark @start postcond
  (myOddSumParity ([]) (by simp) = 0) ∧
  (result = 0 ∨ result = 1) ∧
  (∀ ys, myOddSumParity (xs ++ ys) (by simp) = (result + myOddSumParity (ys) (by simp)) % 2) ∧
  (∀ x, myOddSumParity ([x]) (by simp) = x % 2)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Empty list property**: Empty list has parity 0. -/
def empty_list_prop : Prop := myOddSumParity [] (by simp) = 0

/-- **Empty list theorem**: Empty list has parity 0. -/
@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

/-- **Binary result property**: Result is always 0 or 1. -/
def binary_result_prop (xs : List Nat) : Prop :=
  myOddSumParity xs (by simp) = 0 ∨ myOddSumParity xs (by simp) = 1

/-- **Binary result theorem**: Result is always 0 or 1. -/
@[simp] theorem binary_result_thm (xs : List Nat) : binary_result_prop xs := by
  sorry

/-- **Additive property**: Parity of concatenated lists equals XOR of individual parities. -/
def additive_prop (xs ys : List Nat) : Prop :=
  myOddSumParity (xs ++ ys) (by simp) =
    (myOddSumParity xs (by simp) + myOddSumParity ys (by simp)) % 2

/-- **Additive theorem**: Parity of concatenated lists equals XOR of individual parities. -/
@[simp] theorem additive_thm (xs ys : List Nat) : additive_prop xs ys := by
  sorry

/-- **Single element property**: Single element list has same parity as the element. -/
def single_element_prop (x : Nat) : Prop := myOddSumParity [x] (by simp) = x % 2

/-- **Single element theorem**: Single element list has same parity as the element. -/
@[simp] theorem single_element_thm (x : Nat) : single_element_prop x := by
  sorry
-- !benchmark @end proof_aux

theorem myOddSumParity_spec_satisfied (xs : List Nat) (h_precond : myOddSumParity_precond (xs)) :
    myOddSumParity_postcond (xs) (myOddSumParity (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof