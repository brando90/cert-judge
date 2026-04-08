```lean
import Lean.Data.HashMap
import Mathlib.Tactic.LibrarySearch
import Mathlib.Tactic.Ring
import Std.Data.List.Basic
import Std.Data.Nat.Basic
open Lean Std

/-- For a given string, flip lowercase characters to uppercase and uppercase to lowercase. -/
def flipCase (string : String) : String :=
  String.mk (string.data.map (fun c =>
    if c.isLower then c.toUpper
    else if c.isUpper then c.toLower
    else c
  ))

/-- Test cases for `flipCase` -/
def flipCaseTests : List (String × String) := [
  ("", ""),
  ("Hello!", "hELLO!"),
  ("These violent delights have violent ends", "tHESE VIOLENT DELIGHTS HAVE VIOLENT ENDS")
]

/-- Run test cases for `flipCase` -/
#eval flipCaseTests.all (fun (input, expected) => flipCase input == expected)

/-- Specification for `flipCase` -/
def flipCaseSpec (s : String) : String :=
  String.mk (s.data.map (fun c =>
    if c.isLower then c.toUpper
    else if c.isUpper then c.toLower
    else c
  ))

theorem flipCase_spec (s : String) : flipCase s = flipCaseSpec s := by
  rfl

/-- Correctness: `flipCase` preserves string length -/
theorem flipCase_preserves_length (s : String) : (flipCase s).length = s.length := by
  simp [flipCase]
  rw [String.length, String.length]
  simp [List.length_map]

/-- Correctness: `flipCase` applied twice gives the original string -/
theorem flipCase_involutive (s : String) : flipCase (flipCase s) = s := by
  sorry
```
