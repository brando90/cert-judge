import Std

namespace OddSumParity

/-- Check if a number is odd -/
def isOdd (n : Int) : Bool := n % 2 = 1

/-- Precondition: Check if input is a non-empty list of odd integers -/
def pre (xs : List Int) : Bool := 
  xs ≠ [] ∧ xs.all isOdd

/-- Return the parity (0 or 1) of the sum of all elements in a list of odd integers -/
def prog (xs : List Int) : Int :=
  if pre xs then
    xs.foldl (· + ·) 0 % 2
  else
    panic! "Require non-empty list of odd integers"

/-- Test the function with a basic case -/
#eval prog [1, 3, 5] -- Expected: 1

/-- Test the function with a single element -/
#eval prog [1] -- Expected: 1

/-- Specification: The parity of a sum of odd numbers depends only on the count -/
def post (xs : List Int) (result : Int) : Prop :=
  result = if xs.length % 2 = 1 then 1 else 0

/-- Lemma: The sum of an odd number of odd integers has odd parity -/
lemma odd_count_odd_sum_has_odd_parity (xs : List Int) (h : pre xs) (h2 : xs.length % 2 = 1) : 
  xs.foldl (· + ·) 0 % 2 = 1 := sorry

/-- Lemma: The sum of an even number of odd integers has even parity -/
lemma even_count_odd_sum_has_even_parity (xs : List Int) (h : pre xs) (h2 : xs.length % 2 = 0) : 
  xs.foldl (· + ·) 0 % 2 = 0 := sorry

/-- Correctness theorem: prog satisfies the specification when precondition holds -/
theorem prog_correct (xs : List Int) (h : pre xs) : post xs (prog xs) := by
  unfold prog post
  simp [h]
  by_cases h2 : xs.length % 2 = 1
  · exact odd_count_odd_sum_has_odd_parity xs h h2
  · have h3 : xs.length % 2 = 0 := by
      have : xs.length % 2 = 0 ∨ xs.length % 2 = 1 := by sorry
      tauto
    exact even_count_odd_sum_has_even_parity xs h h3

end OddSumParity
