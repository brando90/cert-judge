-- !benchmark @start import type=solution
import Mathlib
namespace CollectionsChainMap

open Std

abbrev Key := String
abbrev Value := Int

-- !benchmark @end import

-- !benchmark @start solution_aux
abbrev FuncMap := List (Key × Value)

structure FunctionalChainMap where
  maps : List FuncMap
  nonempty : maps ≠ []
deriving Repr, DecidableEq

def mkFunc (maps : List FuncMap) : FunctionalChainMap :=
  if h : maps = [] then
    { maps := [[]], nonempty := by simp }
  else
    { maps := maps, nonempty := h }

def lookup_loop (maps : List FuncMap) (k : Key) : Option Value :=
  match maps with
  | [] => none
  | m :: ms =>
      match m.lookup k with
      | some v => some v
      | none => lookup_loop ms k

def get_func (cm : FunctionalChainMap) (k : Key) : Option Value :=
  lookup_loop cm.maps k

def set_func (cm : FunctionalChainMap) (k : Key) (v : Value) : FunctionalChainMap :=
  match cm.maps with
  | [] => cm
  | m :: ms =>
      let m' := (k, v) :: (m.filter (fun (ki, _) => ki != k))
      { maps := m' :: ms, nonempty := by simp }

structure ImperativeChainMap where
  maps : List (HashMap Key Value)
  nonempty : maps ≠ []
deriving Repr

def mkImp (maps : List (HashMap Key Value)) : ImperativeChainMap :=
  match maps with
  | [] => { maps := [{}], nonempty := by simp }
  | m :: ms => { maps := m :: ms, nonempty := by simp }
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def get_imp_precond (cm : ImperativeChainMap) (k : Key) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def get_imp (cm : ImperativeChainMap) (k : Key) (h_precond : get_imp_precond (cm) (k)) : Option Value :=
  -- !benchmark @start code
  let rec loop : List (HashMap Key Value) → Option Value
    | [] => none
    | m :: ms =>
        match m.get? k with
        | some v => some v
        | none => loop ms
  loop cm.maps
  -- !benchmark @end code

-- !benchmark @start postcond_aux
def shadowing_prop (cm : FunctionalChainMap) (k : Key) : Prop :=
  match cm.maps with
  | [] => True
  | m :: _ =>
      match m.lookup k with
      | some v => get_func cm k = some v
      | none => True

def write_prop (cm : FunctionalChainMap) (k : Key) (v : Value) : Prop :=
  let cm' := set_func cm k v
  (get_func cm' k = some v) ∧ (cm'.maps.tail = cm.maps.tail)

def Post (cm : FunctionalChainMap) (k : Key) (v : Value) : Prop :=
  shadowing_prop cm k ∧ write_prop cm k v
-- !benchmark @end postcond_aux

@[reducible, simp]
def get_imp_postcond (cm : ImperativeChainMap) (k : Key) (result : Option Value)
    (h_precond : get_imp_precond (cm) (k)) : Prop :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
theorem shadowing_thm (cm : FunctionalChainMap) (k : Key) : shadowing_prop cm k := by
  sorry

theorem write_thm (cm : FunctionalChainMap) (k : Key) (v : Value) : write_prop cm k v := by
  sorry

theorem correctness_thm (cm : FunctionalChainMap) (k : Key) (v : Value) :
  Post cm k v := by
  sorry
-- !benchmark @end proof_aux

theorem get_imp_spec_satisfied (cm : ImperativeChainMap) (k : Key) (h_precond : get_imp_precond (cm) (k)) :
    get_imp_postcond (cm) (k) (get_imp (cm) (k) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof