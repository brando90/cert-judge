-- !benchmark @start import type=solution
import Mathlib
namespace StringConcatenate
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def concatenate_precond (strings : List String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def concatenate (strings : List String) (h_precond : concatenate_precond (strings)) : String :=
  -- !benchmark @start code
  String.join strings
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp] def empty_list_prop : Prop := concatenate [] (by simp) = ""
@[simp] theorem empty_list_thm : empty_list_prop := sorry

@[reducible, simp] def single_element_prop (s : String) : Prop := concatenate [s] (by simp) = s
@[simp] theorem single_element_thm (s : String) : single_element_prop s := sorry

@[reducible, simp]
def associativity_prop (xs ys : List String) : Prop :=
  concatenate (xs ++ ys) (by simp) = concatenate xs (by simp) ++ concatenate ys (by simp)
@[simp] theorem associativity_thm (xs ys : List String) : associativity_prop xs ys := sorry

@[reducible, simp]
def length_prop (strings : List String) : Prop :=
  (concatenate strings (by simp)).length = (strings.map String.length).sum
@[simp] theorem length_thm (strings : List String) : length_prop strings := sorry

@[reducible, simp]
def empty_strings_prop (strings : List String) : Prop :=
  concatenate (strings.filter (· ≠ "")) (by simp) = concatenate strings (by simp)
@[simp] theorem empty_strings_thm (strings : List String) : empty_strings_prop strings := sorry

@[reducible, simp]
def concatenate_postcond (strings : List String) (result : String)
    (h_precond : concatenate_precond (strings)) : Prop :=
  -- !benchmark @start postcond
  (result = concatenate (strings) h_precond) ∧
    (empty_list_prop) ∧
    (∀ s, single_element_prop s) ∧
    (∀ xs ys, associativity_prop xs ys) ∧
    (length_prop strings) ∧
    (empty_strings_prop strings)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem concatenate_spec_satisfied (strings : List String) (h_precond : concatenate_precond (strings)) :
    concatenate_postcond (strings) (concatenate (strings) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof