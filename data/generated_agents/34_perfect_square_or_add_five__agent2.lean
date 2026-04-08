import Mathlib.Tactic.Basic
import Mathlib.Data.Nat.Basic
import Mathlib.Data.Nat.Sqrt

namespace PerfectSquareOrAddFive

def is_perfect_square (n : Nat) : Bool :=
  let root := n.sqrt
  root * root == n

def perfect_square_or_add_five (n : Nat) : Nat :=
  if is_perfect_square n then
    n
  else
    n + 5

def pre (n : Nat) : Prop := True

def post (n : Nat) (result : Nat) : Prop :=
  (is_perfect_square n ∧ result = n) ∨
  (¬ is_perfect_square n ∧ result = n + 5)

theorem perfect_square_or_add_five_correct (n : Nat) (h : pre n) :
  post n (perfect_square_or_add_five n) := by
  unfold perfect_square_or_add_five
  unfold post
  by_cases h : is_perfect_square n
  · left
    constructor
    · exact h
    · simp [h]
  · right
    constructor
    · exact h
    · simp [h]
    
-- Tests
example : perfect_square_or_add_five 16 = 16 := by rfl
example : perfect_square_or_add_five 18 = 23 := by rfl
example : perfect_square_or_add_five 0 = 0 := by rfl
example : perfect_square_or_add_five 1 = 1 := by rfl
example : perfect_square_or_add_five 2 = 7 := by rfl
example : perfect_square_or_add_five 4 = 4 := by rfl

end PerfectSquareOrAddFive
