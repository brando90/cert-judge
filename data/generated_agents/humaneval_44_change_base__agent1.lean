import Mathlib.Data.Nat.Basic
import Mathlib.Data.String.Basic

/--
  Change numerical base of input number x to base.
  Return string representation after the conversion.
  Base numbers are less than 10.
-/
def change_base (x : Nat) (base : Nat) : String :=
  if x = 0 then
    "0"
  else
    let rec aux (n : Nat) (acc : String) : String :=
      if n = 0 then
        acc
      else
        aux (n / base) (toString (n % base) ++ acc)
    aux x ""

/-- Specification for change_base -/
def change_base_spec (x : Nat) (base : Nat) : String :=
  if x = 0 then
    "0"
  else
    let rec aux (n : Nat) (acc : String) : String :=
      if n = 0 then
        acc
      else
        aux (n / base) (toString (n % base) ++ acc)
    aux x ""

theorem change_base_correct (x : Nat) (base : Nat) (h : base > 1) :
  change_base x base = change_base_spec x base := by
  sorry

#eval change_base 8 3 -- "22"
#eval change_base 9 3 -- "100"
#eval change_base 234 2 -- "11101010"
#eval change_base 16 2 -- "10000"
#eval change_base 8 2 -- "1000"
#eval change_base 7 2 -- "111"

example : change_base 8 3 = "22" := rfl
example : change_base 9 3 = "100" := rfl
example : change_base 234 2 = "11101010" := rfl
example : change_base 16 2 = "10000" := rfl
example : change_base 8 2 = "1000" := rfl
example : change_base 7 2 = "111" := rfl

theorem change_base_identity (x base : Nat) (h1 : x > 0) (h2 : base > x) :
  change_base x base = toString x := by
  sorry
