import Mathlib.Data.Nat.Basic

/-- 
  Return the product of three natural numbers.
-/

def product (a b c : Nat) : Nat :=
  a * b * c

/-- 
  Tests for the product function.
-/

def test : Bool :=
  product 2 3 4 = 24 && 
  product 0 5 6 = 0 &&
  product 1 1 1 = 1

#eval test -- Should return true

/--
  Specification for the product function.
-/

def spec (a b c : Nat) : Nat :=
  a * b * c

/--
  Proof that the implementation satisfies the specification.
-/

theorem product_correct (a b c : Nat) : product a b c = spec a b c := by
  unfold product spec
  rfl
  sorry
