import Mathlib.Tactic.LibrarySearch
import Mathlib.Data.Int.Sqrt

/--
Return the number itself if it is a perfect square;
otherwise, return the number plus 5.
-/
def perfectSquareOrAddFive (n : Int) : Int :=
  if n < 0 then
    panic! "Input must be a non-negative integer"
  else
    let root := Int.sqrt n
    if root * root = n then n else n + 5

/-- The precondition for perfectSquareOrAddFive -/
def pre (n : Int) : Prop :=
  n ≥ 0

/-- The postcondition for perfectSquareOrAddFive -/
def post (n : Int) (result : Int) : Prop :=
  (∃ k : Int, k ≥ 0 ∧ n = k * k ∧ result = n) ∨
  (¬∃ k : Int, k ≥ 0 ∧ n = k * k) ∧ result = n + 5

/-- Correctness theorem for perfectSquareOrAddFive -/
theorem perfectSquareOrAddFive_correct (n : Int) :
  pre n → post n (perfectSquareOrAddFive n) := by
  intro h
  unfold perfectSquareOrAddFive pre post
  simp [h]
  let root := Int.sqrt n
  by_cases h_perfect : root * root = n
  · left
    exists root
    constructor
    · exact Int.sqrt_nonneg n
    · constructor
      · exact h_perfect
      · rfl
  · right
    constructor
    · intro h_contra
      cases h_contra with
      | intro k hk =>
        have ⟨hk_nonneg, hk_square, _⟩ := hk
        have h_root_max := Int.sqrt_le n k hk_nonneg hk_square
        have h_root_min := Int.le_sqrt_of_sq_le n k hk_nonneg hk_square
        have h_root_eq : root = k := by
          apply le_antisymm <;> assumption
        rw [h_root_eq] at h_perfect
        contradiction
    · rfl

/-- Tests for perfectSquareOrAddFive -/
def tests : Bool :=
  -- Basic test
  perfectSquareOrAddFive 16 = 16 &&
  -- Non-perfect square
  perfectSquareOrAddFive 18 = 23 &&
  -- Edge cases
  perfectSquareOrAddFive 0 = 0 &&
  perfectSquareOrAddFive 1 = 1 &&
  perfectSquareOrAddFive 2 = 7

#eval tests
