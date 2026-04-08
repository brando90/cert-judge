import Mathlib.Tactic

namespace VeriBench.Max

/-- Returns the larger of two natural numbers. -/
def prog (a b : Nat) : Nat :=
  if a ≤ b then b else a

/-- Tests for the max function -/
def tests : Bool :=
  -- Basic unit test
  prog 7 3 = 7 &&
  -- Edge unit test
  prog 0 0 = 0

/-- The precondition is that both inputs are natural numbers. -/
def pre (a b : Nat) : Prop := True

/-- The postcondition states that the result is the maximum of the two inputs. -/
def post (a b : Nat) (result : Nat) : Prop :=
  result = max a b

/-- Correctness theorem: prog satisfies its specification. -/
theorem prog_correct (a b : Nat) (h : pre a b) : post a b (prog a b) := by
  unfold post prog
  simp [max_def]
  by_cases h : a ≤ b
  · simp [h]
  · simp [h]
    exact Nat.not_le.mp h

end VeriBench.Max
