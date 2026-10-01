import VeriBench

/-
Return the sum of two natural numbers (non-negative integers).

Edge cases:
- 0 + n = n
- The function raises ValueError if a or b is not a natural number.
-/

namespace sum_of_naturals

def pre (a : Int) (b : Int) : Prop :=
  a ≥ 0 ∧ b ≥ 0

def post (a : Int) (b : Int) (result : Int) : Prop :=
  result = a + b

def prog (a : Int) (b : Int) : Int :=
  if a < 0 ∨ b < 0 then
    panic! s!"Inputs must be non-negative integers (got a={a}, b={b})"
  else
    a + b

theorem pre_iff_nonnegative (a b : Int) :
    pre a b ↔ 0 ≤ a ∧ 0 ≤ b := Iff.rfl

theorem prog_eq_add_of_pre (a b : Int) (h : pre a b) :
    prog a b = a + b := by sorry

theorem prog_correct (a : Int) (b : Int) : pre a b → post a b (prog a b) := by
  intro h
  unfold post
  exact prog_eq_add_of_pre a b h

theorem prog_nonnegative (a b : Int) (h : pre a b) :
    0 ≤ prog a b := by sorry

theorem prog_zero_left (b : Int) (hb : 0 ≤ b) :
    prog 0 b = b := by sorry

theorem prog_zero_right (a : Int) (ha : 0 ≤ a) :
    prog a 0 = a := by sorry

theorem prog_comm (a b : Int) (h : pre a b) :
    prog a b = prog b a := by sorry

theorem prog_basic_test : prog 1 2 = 3 := by sorry

theorem prog_zero_test : prog 0 0 = 0 := by sorry

end sum_of_naturals
