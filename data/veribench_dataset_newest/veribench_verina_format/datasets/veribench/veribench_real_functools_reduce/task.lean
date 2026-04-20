-- !benchmark @start import type=solution
import Mathlib
namespace FunctoolsReduce
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def reduce_imp_precond {α : Type} (f : α → α → α) (xs : List α) (init? : Option α) : Prop :=
  -- !benchmark @start precond
  match init? with
  | some _ => True
  | none => xs ≠ []
  -- !benchmark @end precond

-- !benchmark @start code_aux
/--
Functional Reduce.
Uses `List.foldl` directly. Returns `Option α` to handle the empty/no-init case safely.
-/
def reduce_func {α : Type} (f : α → α → α) (xs : List α) (init? : Option α) : Option α :=
  match init? with
  | some init => some (xs.foldl f init)
  | none =>
    match xs with
    | [] => none
    | head :: tail => some (tail.foldl f head)
-- !benchmark @end code_aux

/--
Imperative Reduce.
Uses a stateful loop to accumulate values, matching Python's implementation.
-/
def reduce_imp {α : Type} (f : α → α → α) (xs : List α) (init? : Option α)
    (h_precond : reduce_imp_precond (f := f) (xs := xs) (init? := init?)) : Option α :=
  -- !benchmark @start code
  Id.run do
    let mut acc := init?
    let mut items := xs

    if acc.isNone then
      match items with
      | [] => return none
      | h :: t =>
          acc := some h
          items := t

    for x in items do
      match acc with
      | some val => acc := some (f val x)
      | none => return none

    return acc
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def reduce_imp_postcond {α : Type} (f : α → α → α) (xs : List α) (init? : Option α)
    (result : Option α) (h_precond : reduce_imp_precond (f := f) (xs := xs) (init? := init?)) : Prop :=
  -- !benchmark @start postcond
  result = reduce_func f xs init?
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem reduce_imp_spec_satisfied {α : Type} (f : α → α → α) (xs : List α) (init? : Option α)
    (h_precond : reduce_imp_precond (f := f) (xs := xs) (init? := init?)) :
    reduce_imp_postcond (f := f) (xs := xs) (init? := init?)
      (reduce_imp (f := f) (xs := xs) (init? := init?) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof