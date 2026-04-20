-- !benchmark @start import type=solution
import Mathlib
namespace HtmlEscape

open Std
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def escape_imp_precond (s : String) (quote : Bool) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/-- Helper: Map a char to its HTML entity string -/
def encodeChar (quote : Bool) (c : Char) : String :=
  match c with
  | '&' => "&amp;"
  | '<' => "&lt;"
  | '>' => "&gt;"
  | '"' => if quote then "&quot;" else "\""
  | '\'' => if quote then "&#x27;" else "'"
  | _ => String.singleton c
-- !benchmark @end code_aux

def escape_imp (s : String) (quote : Bool) (h_precond : escape_imp_precond (s) (quote)) : String :=
  -- !benchmark @start code
  Id.run do
    let mut res := ""
    for c in s.data do
      res := res ++ encodeChar quote c
    return res
  -- !benchmark @end code

-- !benchmark @start postcond_aux
/-- Property: Replacement Correctness (for the functional implementation) -/
def replacement_prop (s : String) (quote : Bool) : Prop :=
  escape_func s quote = s.foldl (fun acc c => acc ++ encodeChar quote c) ""

/-- Property: Ordering (for the functional implementation) -/
def ordering_prop (s : String) : Prop :=
  escape_func ("&" ++ s) true = "&amp;" ++ escape_func s true
-- !benchmark @end postcond_aux

@[reducible, simp]
def escape_imp_postcond (s : String) (quote : Bool) (result : String) (h_precond : escape_imp_precond (s) (quote)) :=
  -- !benchmark @start postcond
  replacement_prop s quote ∧ ordering_prop s
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- Functional implementation (needed for postcondition properties)
def escape_func (s : String) (quote : Bool) : String :=
  s.foldl (fun acc c => acc ++ encodeChar quote c) ""

theorem replacement_thm (s : String) (quote : Bool) : replacement_prop s quote := by
  rfl

theorem ordering_thm (s : String) : ordering_prop s := by
  sorry
-- !benchmark @end proof_aux

theorem escape_imp_spec_satisfied (s : String) (quote : Bool) (h_precond : escape_imp_precond (s) (quote)) :
    escape_imp_postcond (s) (quote) (escape_imp (s) (quote) h_precond) h_precond := by
  -- !benchmark @start proof
  exact ⟨replacement_thm s quote, ordering_thm s⟩
  -- !benchmark @end proof