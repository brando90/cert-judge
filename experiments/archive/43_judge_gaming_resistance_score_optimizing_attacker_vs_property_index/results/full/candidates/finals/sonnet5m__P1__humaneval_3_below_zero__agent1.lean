import Mathlib
import Lean.Data.Array

namespace BelowZero

/--
You're given a list of deposit and withdrawal operations on a bank account that starts with
zero balance. Your task is to detect if at any point the balance of account falls below zero, and
at that point function should return true. Otherwise it should return false.
-/
def belowZero (operations : List Int) : Bool :=
  let rec loop (balance : Int) (ops : List Int) : Bool :=
    match ops with
    | [] => false
    | op :: rest =>
      let newBalance := balance + op
      if newBalance < 0 then
        true
      else
        loop newBalance rest
  loop 0 operations

/-- The balance after each operation, starting from an initial balance. -/
def prefixBalances : Int → List Int → List Int
  | _, [] => []
  | balance, op :: rest =>
      let nextBalance := balance + op
      nextBalance :: prefixBalances nextBalance rest

/-- An executable specification: some balance after an operation is negative. -/
def belowZeroSpec (operations : List Int) : Bool :=
  (prefixBalances 0 operations).any (fun balance => decide (balance < 0))

/-- The balance after the first `n` operations. -/
def prefixBalance (operations : List Int) (n : Nat) : Int :=
  (operations.take n).sum

/--
The mathematical specification: for some prefix of the operations, the account
balance is strictly negative.
-/
def belowZeroSemantic (operations : List Int) : Prop :=
  ∃ n : Nat, n ≤ operations.length ∧ prefixBalance operations n < 0

/-- The executable specification agrees with the prefix-sum specification. -/
theorem belowZeroSpec_iff_semantic (operations : List Int) :
    belowZeroSpec operations = true ↔ belowZeroSemantic operations := by
  sorry

/-- Precondition: None. -/
def belowZeroPre (_operations : List Int) : Prop := True

/--
Postcondition: the result is true exactly when some prefix of the operations
has a negative balance.
-/
def belowZeroPost (operations : List Int) (result : Bool) : Prop :=
  result = true ↔ belowZeroSemantic operations

theorem belowZeroCorrect (operations : List Int) (h : belowZeroPre operations) :
    belowZeroPost operations (belowZero operations) := by
  sorry

/-- A false result means that every prefix balance is nonnegative. -/
theorem belowZero_false_iff (operations : List Int) :
    belowZero operations = false ↔
      ∀ n : Nat, n ≤ operations.length → 0 ≤ prefixBalance operations n := by
  sorry

/-- Prefixes of a concatenation either go negative in the first list or later. -/
theorem belowZeroSemantic_append (first second : List Int) :
    belowZeroSemantic (first ++ second) ↔
      belowZeroSemantic first ∨
        ∃ n : Nat, n ≤ second.length ∧
          first.sum + prefixBalance second n < 0 := by
  sorry

/-- Tests for belowZero -/
def tests : IO Unit := do
  IO.println s!"Test 1: {belowZero []}"
  IO.println s!"Test 2: {belowZero [1, 2, -3, 1, 2, -3]}"
  IO.println s!"Test 3: {belowZero [1, 2, -4, 5, 6]}"
  IO.println s!"Test 4: {belowZero [1, -1, 2, -2, 5, -5, 4, -4]}"
  IO.println s!"Test 5: {belowZero [1, -1, 2, -2, 5, -5, 4, -5]}"
  IO.println s!"Test 6: {belowZero [1, -2, 2, -2, 5, -5, 4, -4]}"

  assert! belowZero [] == false
  assert! belowZero [1, 2, -3, 1, 2, -3] == false
  assert! belowZero [1, 2, -4, 5, 6] == true
  assert! belowZero [1, -1, 2, -2, 5, -5, 4, -4] == false
  assert! belowZero [1, -1, 2, -2, 5, -5, 4, -5] == true
  assert! belowZero [1, -2, 2, -2, 5, -5, 4, -4] == true

  IO.println "All tests passed!"

end BelowZero
