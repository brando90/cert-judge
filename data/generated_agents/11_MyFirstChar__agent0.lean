import Lean
import Std.Data.List.Basic
import Mathlib.Data.String.Basic

namespace VeriBench

/-- Return the first character of a non-empty string. -/
def first_char (s : String) : Option Char :=
  if s.length > 0 then
    some s.get 0
  else
    none

/-- True iff the input is a non-empty string. -/
def pre (s : String) : Prop :=
  s.length > 0

/-- First character of a non-empty string. -/
def post (s : String) (result : Char) : Prop :=
  result = s.get 0

theorem first_char_correct (s : String) (h : pre s) : 
  match first_char s with
  | some c => post s c
  | none => False
  end := by
  unfold first_char
  unfold pre at h
  simp [h]
  unfold post
  simp
  sorry

def test : IO Unit := do
  -- Basic test
  assert! (first_char "hello" == some 'h')
  
  -- Edge case test
  assert! (first_char "A" == some 'A')
  
  -- Empty string
  assert! (first_char "" == none)
  
  IO.println "All tests passed!"

end VeriBench
