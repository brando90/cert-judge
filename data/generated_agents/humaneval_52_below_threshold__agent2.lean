```lean
import Lean
import Std.Data.List.Basic

/-- Return True if all numbers in the list l are below threshold t. -/
def below_threshold (l : List Int) (t : Int) : Bool :=
  match l with
  | [] => true
  | e :: rest =>
    if e >= t then
      false
    else
      below_threshold rest t

/-- All elements in the list are below the threshold -/
def belowThresholdProp (l : List Int) (t : Int) : Prop :=
  ∀ e ∈ l, e < t

theorem below_threshold_correct (l : List Int) (t : Int) :
  below_threshold l t = true ↔ belowThresholdProp l t := by
  sorry

-- Tests
#eval below_threshold [1, 2, 4, 10] 100 -- true
#eval below_threshold [1, 20, 4, 10] 5 -- false
#eval below_threshold [1, 20, 4, 10] 21 -- true
#eval below_threshold [1, 20, 4, 10] 22 -- true
#eval below_threshold [1, 8, 4, 10] 11 -- true
#eval below_threshold [1, 8, 4, 10] 10 -- false

example : below_threshold [1, 2, 4, 10] 100 = true := by rfl
example : below_threshold [1, 20, 4, 10] 5 = false := by rfl
example : below_threshold [1, 20, 4, 10] 21 = true := by rfl
example : below_threshold [1, 20, 4, 10] 22 = true := by rfl
example : below_threshold [1, 8, 4, 10] 11 = true := by rfl
example : below_threshold [1, 8, 4, 10] 10 = false := by rfl
```
