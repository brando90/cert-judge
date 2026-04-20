-- !benchmark @start import type=solution
import Mathlib
namespace Palindrome
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def is_palindrome_precond (text : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def is_palindrome (text : String) (h_precond : is_palindrome_precond (text)) : Bool :=
  -- !benchmark @start code
  let len := text.length
  let indices := List.range len
  indices.all (fun i =>
    let pos1 := String.Pos.mk i
    let pos2 := String.Pos.mk (len - 1 - i)
    text.get! pos1 = text.get! pos2)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

-- !benchmark @start proof_aux
def empty_string_prop : Prop := is_palindrome "" (by simp) = true
@[simp] theorem empty_string_thm : empty_string_prop := by sorry

def single_char_prop (c : Char) : Prop := is_palindrome (String.mk [c]) (by simp) = true
@[simp] theorem single_char_thm (c : Char) : single_char_prop c := by sorry

def reflection_prop (s : String) : Prop :=
  is_palindrome s (by simp) = is_palindrome (String.mk (s.data.reverse)) (by simp)
@[simp] theorem reflection_thm (s : String) : reflection_prop s := by sorry

def concatenation_prop (s : String) (c : Char) : Prop :=
  is_palindrome s (by simp) = true → is_palindrome (String.mk [c] ++ s ++ String.mk [c]) (by simp) = true
@[simp] theorem concatenation_thm (s : String) (c : Char) : concatenation_prop s c := by sorry
-- !benchmark @end proof_aux

@[reducible, simp]
def is_palindrome_postcond (text : String) (result : Bool) (h_precond : is_palindrome_precond (text)) : Prop :=
  -- !benchmark @start postcond
  result = is_palindrome text h_precond ∧
    (empty_string_prop) ∧
    (∀ c, single_char_prop c) ∧
    (reflection_prop text) ∧
    (∀ c, concatenation_prop text c)
  -- !benchmark @end postcond

theorem is_palindrome_spec_satisfied (text : String) (h_precond : is_palindrome_precond (text)) :
    is_palindrome_postcond (text) (is_palindrome (text) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof