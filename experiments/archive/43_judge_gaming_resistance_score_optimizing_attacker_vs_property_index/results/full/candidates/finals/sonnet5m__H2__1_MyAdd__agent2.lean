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

theorem prog_eq_add (a : Int) (b : Int) (h : pre a b) :
    prog a b = a + b := by
  unfold pre at h
  unfold prog
  have hcond : ¬ (a < 0 ∨ b < 0) := by omega
  simp [hcond]

theorem prog_correct (a : Int) (b : Int) : pre a b → post a b (prog a b) := by
  intro h
  unfold post
  exact prog_eq_add a b h

theorem prog_zero_left (b : Int) (hb : 0 ≤ b) :
    prog 0 b = b := by
  rw [prog_eq_add 0 b ⟨by omega, hb⟩]
  simp

theorem prog_zero_right (a : Int) (ha : 0 ≤ a) :
    prog a 0 = a := by
  rw [prog_eq_add a 0 ⟨ha, by omega⟩]
  simp

theorem prog_nonnegative (a : Int) (b : Int) (h : pre a b) :
    0 ≤ prog a b := by
  rw [prog_eq_add a b h]
  unfold pre at h
  omega

theorem prog_comm (a : Int) (b : Int) (h : pre a b) :
    prog a b = prog b a := by
  rw [prog_eq_add a b h, prog_eq_add b a ⟨h.2, h.1⟩]
  exact Int.add_comm a b

theorem prog_assoc (a b c : Int) (h : pre a b) (hc : 0 ≤ c) :
    prog (prog a b) c = prog a (prog b c) := by
  have hbc : pre b c := ⟨h.2, hc⟩
  have hleft : pre (prog a b) c :=
    ⟨prog_nonnegative a b h, hc⟩
  have hright : pre a (prog b c) :=
    ⟨h.1, prog_nonnegative b c hbc⟩
  calc
    prog (prog a b) c = (a + b) + c := by
      rw [prog_eq_add (prog a b) c hleft, prog_eq_add a b h]
    _ = a + (b + c) := by omega
    _ = prog a (prog b c) := by
      rw [prog_eq_add a (prog b c) hright, prog_eq_add b c hbc]

theorem prog_monotone (a b a' b' : Int)
    (h : pre a b) (h' : pre a' b')
    (haa : a ≤ a') (hbb : b ≤ b') :
    prog a b ≤ prog a' b' := by
  rw [prog_eq_add a b h, prog_eq_add a' b' h']
  omega

theorem test_one_two : prog 1 2 = 3 := by sorry

theorem test_zero_zero : prog 0 0 = 0 := by sorry

theorem test_zero_left (b : Int) (hb : 0 ≤ b) : prog 0 b = b :=
  prog_zero_left b hb

theorem test_zero_right (a : Int) (ha : 0 ≤ a) : prog a 0 = a :=
  prog_zero_right a ha

end sum_of_naturals
