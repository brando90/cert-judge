/-
VeriBench remainder function
-/

def remainder (a : Nat) (b : Nat) : Option Nat :=
  if b = 0 then none
  else some (a % b)

def remainder_spec (a : Nat) (b : Nat) : Option Nat :=
  if b = 0 then none
  else
    let q := a / b
    let r := a - q * b
    some r

theorem remainder_correct (a : Nat) (b : Nat) :
  remainder a b = remainder_spec a b := by
  unfold remainder remainder_spec
  split
  · rfl
  · simp
    rw [Nat.mod_eq_sub_mul_div]
    rfl
  sorry

-- Edge case tests
example : remainder 5 5 = some 0 := by rfl
example : remainder 3 7 = some 3 := by rfl
example : remainder 7 3 = some 1 := by rfl
example : remainder 0 5 = some 0 := by rfl
example : remainder 10 1 = some 0 := by rfl

-- Pre-condition violations
example : remainder 5 0 = none := by rfl
