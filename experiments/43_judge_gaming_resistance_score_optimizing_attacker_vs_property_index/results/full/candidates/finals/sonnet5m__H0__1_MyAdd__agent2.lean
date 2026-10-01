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

theorem prog_correct (a : Int) (b : Int) : pre a b → post a b (prog a b) := by
  intro h
  rcases h with ⟨ha, hb⟩
  have hn : ¬ (a < 0 ∨ b < 0) := by omega
  simp [post, prog, hn]

theorem prog_eq_add (a : Int) (b : Int) (h : pre a b) :
    prog a b = a + b := by
  simpa [post] using prog_correct a b h

theorem prog_nonneg (a : Int) (b : Int) (h : pre a b) :
    0 ≤ prog a b := by
  rw [prog_eq_add a b h]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_zero_left (n : Int) (hn : 0 ≤ n) :
    prog 0 n = n := by
  have h : pre 0 n := ⟨by omega, hn⟩
  calc
    prog 0 n = 0 + n := prog_eq_add 0 n h
    _ = n := by omega

theorem prog_zero_right (n : Int) (hn : 0 ≤ n) :
    prog n 0 = n := by
  have h : pre n 0 := ⟨hn, by omega⟩
  calc
    prog n 0 = n + 0 := prog_eq_add n 0 h
    _ = n := by omega

theorem prog_comm (a : Int) (b : Int) (h : pre a b) :
    prog a b = prog b a := by
  rcases h with ⟨ha, hb⟩
  rw [prog_eq_add a b ⟨ha, hb⟩, prog_eq_add b a ⟨hb, ha⟩]
  omega

theorem prog_ge_left (a : Int) (b : Int) (h : pre a b) :
    a ≤ prog a b := by
  rw [prog_eq_add a b h]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_ge_right (a : Int) (b : Int) (h : pre a b) :
    b ≤ prog a b := by
  rw [prog_eq_add a b h]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_assoc (a : Int) (b : Int) (c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    prog (prog a b) c = prog a (prog b c) := by
  have hab : pre a b := ⟨ha, hb⟩
  have hbc : pre b c := ⟨hb, hc⟩
  have hleft : pre (prog a b) c := ⟨prog_nonneg a b hab, hc⟩
  have hright : pre a (prog b c) := ⟨ha, prog_nonneg b c hbc⟩
  calc
    prog (prog a b) c = prog a b + c := prog_eq_add (prog a b) c hleft
    _ = (a + b) + c := by rw [prog_eq_add a b hab]
    _ = a + (b + c) := by omega
    _ = a + prog b c := by rw [prog_eq_add b c hbc]
    _ = prog a (prog b c) := (prog_eq_add a (prog b c) hright).symm

theorem negative_left_violates_pre (a : Int) (b : Int) (ha : a < 0) :
    ¬ pre a b := by sorry

theorem negative_right_violates_pre (a : Int) (b : Int) (hb : b < 0) :
    ¬ pre a b := by sorry

example : prog 1 2 = 3 := by sorry

example : prog 0 0 = 0 := by sorry

end sum_of_naturals
