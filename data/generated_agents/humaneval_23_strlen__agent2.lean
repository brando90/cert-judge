import Lean
import Mathlib.Data.String.Basic

/-!
# Strlen

Return the length of a given string.
-/

/--
Returns the length of the given string.
-/
def strlen (s : String) : Nat :=
  s.length

/--
Specification for `strlen`: returns the length of the given string.
-/
def strlenSpec (s : String) : Nat :=
  s.length

theorem strlen_correct (s : String) : strlen s = strlenSpec s := by
  unfold strlen
  unfold strlenSpec
  simp
  sorry

/-!
## Tests
-/

#eval strlen "" -- 0
#eval strlen "x" -- 1
#eval strlen "asdasnakj" -- 9

example : strlen "" = 0 := by rfl
example : strlen "x" = 1 := by rfl
example : strlen "asdasnakj" = 9 := by rfl
