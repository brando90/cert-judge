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

theorem pre_iff_no_negative_input (a b : Int) :
    pre a b ↔ ¬ (a < 0 ∨ b < 0) := by
  unfold pre
  omega

theorem prog_correct (a : Int) (b : Int) : pre a b → post a b (prog a b) := by
  intro h
  have hbad : ¬ (a < 0 ∨ b < 0) := by
    rcases h with ⟨ha, hb⟩
    omega
  simp [prog, post, hbad]

theorem prog_zero_left (b : Int) (hb : 0 ≤ b) :
    prog 0 b = b := by
  have h := prog_correct 0 b ⟨by omega, hb⟩
  simpa [post] using h

theorem prog_zero_right (a : Int) (ha : 0 ≤ a) :
    prog a 0 = a := by
  have h := prog_correct a 0 ⟨ha, by omega⟩
  simpa [post] using h

theorem prog_zero_zero : prog 0 0 = 0 := by
  simpa using prog_zero_left 0 (by omega)

theorem prog_one_two : prog 1 2 = 3 := by sorry

theorem prog_nonnegative (a b : Int) (h : pre a b) :
    0 ≤ prog a b := by
  have hp := prog_correct a b h
  change prog a b = a + b at hp
  rw [hp]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_ge_left (a b : Int) (h : pre a b) :
    a ≤ prog a b := by
  have hp := prog_correct a b h
  change prog a b = a + b at hp
  rw [hp]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_ge_right (a b : Int) (h : pre a b) :
    b ≤ prog a b := by
  have hp := prog_correct a b h
  change prog a b = a + b at hp
  rw [hp]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_comm (a b : Int) (h : pre a b) :
    prog a b = prog b a := by
  have hab := prog_correct a b h
  have hba := prog_correct b a ⟨h.2, h.1⟩
  change prog a b = a + b at hab
  change prog b a = b + a at hba
  calc
    prog a b = a + b := hab
    _ = b + a := Int.add_comm a b
    _ = prog b a := hba.symm

theorem prog_monotone_left (a₁ a₂ b : Int)
    (ha₁ : 0 ≤ a₁) (ha₂ : a₁ ≤ a₂) (hb : 0 ≤ b) :
    prog a₁ b ≤ prog a₂ b := by
  have hp₁ := prog_correct a₁ b ⟨ha₁, hb⟩
  have hp₂ := prog_correct a₂ b ⟨by omega, hb⟩
  change prog a₁ b = a₁ + b at hp₁
  change prog a₂ b = a₂ + b at hp₂
  rw [hp₁, hp₂]
  omega

theorem not_pre_of_negative_left (a b : Int) (ha : a < 0) :
    ¬ pre a b := by
  intro h
  rcases h with ⟨h₁, _⟩
  omega

theorem not_pre_of_negative_right (a b : Int) (hb : b < 0) :
    ¬ pre a b := by
  intro h
  rcases h with ⟨_, h₂⟩
  omega

/-- On inputs satisfying the precondition, the program returns their sum. -/
theorem prog_eq_add (a b : Int) (h : pre a b) :
    prog a b = a + b := by
  have hp := prog_correct a b h
  change prog a b = a + b at hp
  exact hp

/-- The basic unit test from the task. -/
theorem test_one_two : prog 1 2 = 3 := by sorry

/-- The zero edge-case test from the task. -/
theorem test_zero_zero : prog 0 0 = 0 := by sorry

/-- A valid zero-left input leaves the other input unchanged. -/
theorem test_zero_left (b : Int) (hb : 0 ≤ b) :
    prog 0 b = b := prog_zero_left b hb

/-- A negative left input violates the input precondition. -/
theorem negative_left_is_invalid (b : Int) :
    0 > -1 → ¬ pre (-1) b := by
  intro h
  exact not_pre_of_negative_left (-1) b (by omega)

/-- A negative right input violates the input precondition. -/
theorem negative_right_is_invalid (a : Int) :
    0 > -2 → ¬ pre a (-2) := by
  intro h
  exact not_pre_of_negative_right a (-2) (by omega)

/-- Addition of three valid inputs is associative when computed by the program. -/
theorem prog_assoc (a b c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    prog (prog a b) c = prog a (prog b c) := by
  have hab : prog a b = a + b := prog_eq_add a b ⟨ha, hb⟩
  have hbc : prog b c = b + c := prog_eq_add b c ⟨hb, hc⟩
  rw [hab, hbc]
  have hleft : prog (a + b) c = (a + b) + c :=
    prog_eq_add (a + b) c ⟨by omega, hc⟩
  have hright : prog a (b + c) = a + (b + c) :=
    prog_eq_add a (b + c) ⟨ha, by omega⟩
  rw [hleft, hright]
  omega

end sum_of_naturals
