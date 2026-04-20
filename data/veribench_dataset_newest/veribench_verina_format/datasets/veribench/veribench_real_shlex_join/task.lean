-- !benchmark @start import type=solution
import Mathlib
namespace ShlexJoin

open Std
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def join_imp_precond (xs : List String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
def isSafeChar (c : Char) : Bool :=
  c.isAlphanum ||
  c == '_' || c == '@' || c == '%' || c == '+' ||
  c == '=' || c == ':' || c == '.' || c == '/' || c == '-'

def hasUnsafe (s : String) : Bool :=
  s.any (fun c => !isSafeChar c)

def escapeQuotes (s : String) : String :=
  s.replace "'" "'\"'\"'"

def quote_func (s : String) : String :=
  if s.isEmpty then
    "''"
  else if !hasUnsafe s then
    s
  else
    "'" ++ escapeQuotes s ++ "'"

def join_func (xs : List String) : String :=
  let quoted := xs.map quote_func
  String.intercalate " " quoted

def quote_imp (s : String) : String :=
  Id.run do
    if s.isEmpty then return "''"
    if !hasUnsafe s then return s

    let mut res := "'"
    for c in s.data do
      if c == '\'' then res := res ++ "'\"'\"'"
      else res := res.push c
    res ++ "'"
-- !benchmark @end code_aux

def join_imp (xs : List String) (h_precond : join_imp_precond (xs)) : String :=
  -- !benchmark @start code
  Id.run do
    let mut res := ""
    let mut first := true

    for s in xs do
      let q := quote_imp s
      if first then
        res := q
        first := false
      else
        res := res ++ " " ++ q

    return res
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def join_imp_postcond (xs : List String) (result : String) (h_precond : join_imp_precond (xs)) :=
  -- !benchmark @start postcond
  result = join_func xs
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem join_imp_spec_satisfied (xs : List String) (h_precond : join_imp_precond (xs)) :
    join_imp_postcond (xs) (join_imp (xs) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof