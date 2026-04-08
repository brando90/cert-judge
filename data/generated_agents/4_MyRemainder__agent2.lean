import Mathlib.Data.Int.Basic

/-
Return the remainder when non-negative integer a is divided by positive integer b.

Edge cases:
- remainder(a, a) = 0 for any positive a
- remainder(a, b) = a when a < b
- The function raises ValueError if a is negative or b is not positive.
-/

def pre (a : Int) (b : Int) : Prop :=
  a ≥ 0 ∧ b > 0

def prog (a : Int) (b : Int) : Int :=
  if h : pre a b then
    a % b
  else
    panic! s!"Require a ≥ 0 and b > 0 (got a={a}, b={b})"

def post (a : Int) (b : Int) (result : Int) : Prop :=
  pre a b →
  (result ≥ 0 ∧ result < b ∧ ∃ q : Int, a = q * b + result)

theorem prog_correct (a : Int) (b : Int) : post a b (prog a b) := by
  intro h
  unfold prog
  simp [h]
  unfold post
  intro _
  have rem_bounds : 0 ≤ a % b ∧ a % b < b := by
    apply Int.mod_nonneg_lt_modulus
    exact h.right
  have div_eq : a = (a / b) * b + (a % b) := by
    exact Int.div_add_mod a b
  exists a / b
  exact ⟨rem_bounds.left, rem_bounds.right, div_eq⟩
  sorry

-- Tests
example : prog 7 3 = 1 := by rfl
example : prog 3 7 = 3 := by rfl
example : prog 10 5 = 0 := by rfl
example : prog 10 10 = 0 := by rfl

-- Edge cases
example : ∀ a : Int, a > 0 → prog a a = 0 := by
  intro a ha
  simp [prog, pre, ha, Int.le_of_lt ha]
  apply Int.mod_self
  sorry

example : ∀ a b : Int, 0 ≤ a → 0 < b → a < b → prog a b = a := by
  intro a b ha hb hab
  simp [prog, pre, ha, hb]
  apply Int.mod_eq_of_lt
  exact ⟨Int.le_of_lt hb, hab⟩
  sorry
