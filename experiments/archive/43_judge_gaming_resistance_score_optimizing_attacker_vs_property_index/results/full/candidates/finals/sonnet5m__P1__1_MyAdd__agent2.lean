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

theorem not_pre_iff_negative (a b : Int) :
    ¬ pre a b ↔ a < 0 ∨ b < 0 := by
  unfold pre
  omega

theorem prog_of_pre (a b : Int) (h : pre a b) :
    prog a b = a + b := by
  rcases h with ⟨ha, hb⟩
  have hcond : ¬ (a < 0 ∨ b < 0) := by omega
  simp [prog, hcond]

theorem prog_correct (a : Int) (b : Int) :
    pre a b → post a b (prog a b) := by
  intro h
  unfold post
  rw [prog_of_pre a b h]

theorem prog_nonnegative (a b : Int) (h : pre a b) :
    0 ≤ prog a b := by
  rw [prog_of_pre a b h]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_zero_left (b : Int) (hb : 0 ≤ b) :
    prog 0 b = b := by
  have h : pre 0 b := by
    unfold pre
    omega
  rw [prog_of_pre 0 b h]
  simp

theorem prog_zero_right (a : Int) (ha : 0 ≤ a) :
    prog a 0 = a := by
  have h : pre a 0 := by
    unfold pre
    omega
  rw [prog_of_pre a 0 h]
  simp

theorem prog_comm (a b : Int) (h : pre a b) :
    prog a b = prog b a := by
  rw [prog_of_pre a b h, prog_of_pre b a (And.symm h)]
  exact Int.add_comm a b

theorem prog_one_two : prog 1 2 = 3 := by sorry

theorem prog_zero_zero : prog 0 0 = 0 := by sorry

theorem prog_le_left (a b : Int) (h : pre a b) :
    a ≤ prog a b := by
  rw [prog_of_pre a b h]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_le_right (a b : Int) (h : pre a b) :
    b ≤ prog a b := by
  rw [prog_of_pre a b h]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_strict_mono_right (a b c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hbc : b < c) :
    prog a b < prog a c := by
  have hab : pre a b := ⟨ha, hb⟩
  have hac : pre a c := ⟨ha, by omega⟩
  rw [prog_of_pre a b hab, prog_of_pre a c hac]
  omega

theorem prog_monotone_right (a b c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) (hbc : b ≤ c) :
    prog a b ≤ prog a c := by
  have hab : pre a b := ⟨ha, hb⟩
  have hac : pre a c := ⟨ha, hc⟩
  rw [prog_of_pre a b hab, prog_of_pre a c hac]
  omega

theorem prog_strict_mono_left (a b c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) (hac : a < c) :
    prog a b < prog c b := by
  have hab : pre a b := ⟨ha, hb⟩
  have hcb : pre c b := ⟨hc, hb⟩
  rw [prog_of_pre a b hab, prog_of_pre c b hcb]
  omega

theorem prog_monotone_left (a b c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) (hac : a ≤ c) :
    prog a b ≤ prog c b := by
  have hab : pre a b := ⟨ha, hb⟩
  have hcb : pre c b := ⟨hc, hb⟩
  rw [prog_of_pre a b hab, prog_of_pre c b hcb]
  omega

theorem prog_order_iff_right (a b c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    prog a b ≤ prog a c ↔ b ≤ c := by
  have hab : pre a b := ⟨ha, hb⟩
  have hac : pre a c := ⟨ha, hc⟩
  rw [prog_of_pre a b hab, prog_of_pre a c hac]
  omega

theorem prog_order_iff_left (a b c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    prog a b ≤ prog c b ↔ a ≤ c := by
  have hab : pre a b := ⟨ha, hb⟩
  have hcb : pre c b := ⟨hc, hb⟩
  rw [prog_of_pre a b hab, prog_of_pre c b hcb]
  omega

theorem prog_pos_iff (a b : Int) (h : pre a b) :
    0 < prog a b ↔ 0 < a ∨ 0 < b := by
  rw [prog_of_pre a b h]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_zero_iff (a b : Int) (h : pre a b) :
    prog a b = 0 ↔ a = 0 ∧ b = 0 := by
  rw [prog_of_pre a b h]
  rcases h with ⟨ha, hb⟩
  omega

theorem prog_cancel_left (a b c : Int)
    (hab : pre a b) (hac : pre a c)
    (h : prog a b = prog a c) :
    b = c := by
  rw [prog_of_pre a b hab, prog_of_pre a c hac] at h
  omega

theorem prog_associative (a b c : Int)
    (ha : 0 ≤ a) (hb : 0 ≤ b) (hc : 0 ≤ c) :
    prog (prog a b) c = prog a (prog b c) := by
  have hab : pre a b := ⟨ha, hb⟩
  have hbc : pre b c := ⟨hb, hc⟩
  have hleft : pre (prog a b) c := by
    rw [prog_of_pre a b hab]
    constructor <;> omega
  have hright : pre a (prog b c) := by
    rw [prog_of_pre b c hbc]
    constructor <;> omega
  rw [prog_of_pre (prog a b) c hleft,
      prog_of_pre a (prog b c) hright,
      prog_of_pre a b hab,
      prog_of_pre b c hbc]
  exact Int.add_assoc a b c

theorem prog_post_iff (a b result : Int) (h : pre a b) :
    post a b result ↔ result = prog a b := by
  unfold post
  rw [prog_of_pre a b h]

theorem post_unique (a b x y : Int)
    (hx : post a b x) (hy : post a b y) :
    x = y := by
  unfold post at hx hy
  exact hx.trans hy.symm

end sum_of_naturals
