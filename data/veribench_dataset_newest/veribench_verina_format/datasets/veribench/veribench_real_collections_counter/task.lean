-- !benchmark @start import type=solution
import Mathlib
namespace CollectionsCounter

open Std
-- !benchmark @end import

-- !benchmark @start solution_aux

-- Key type for the counter (Char for simplicity in benchmark)
abbrev Key := Char

structure FunctionalCounter where
  data : List (Key × Int)
deriving Repr, Inhabited, DecidableEq

def emptyFunc : FunctionalCounter := ⟨[]⟩

def get_func (c : FunctionalCounter) (k : Key) : Int :=
  match c.data.lookup k with
  | some v => v
  | none => 0

def update_one_func (c : FunctionalCounter) (k : Key) (delta : Int) : FunctionalCounter :=
  let current := get_func c k
  let newData := c.data.filter (fun (key, _) => key != k)
  ⟨(k, current + delta) :: newData⟩

def update_func (c : FunctionalCounter) (s : List Key) : FunctionalCounter :=
  s.foldl (fun acc k => update_one_func acc k 1) c

def subtract_func (c : FunctionalCounter) (s : List Key) : FunctionalCounter :=
  s.foldl (fun acc k => update_one_func acc k (-1)) c

structure ImperativeCounter where
  data : HashMap Key Int
deriving Repr, Inhabited

def emptyImp : ImperativeCounter := ⟨{}⟩

def get_imp (c : ImperativeCounter) (k : Key) : Int :=
  (c.data.get? k).getD 0

def subtract_imp (c : ImperativeCounter) (s : List Key) : ImperativeCounter :=
  Id.run do
    let mut counts := c.data
    for k in s do
      let current := (counts.get? k).getD 0
      counts := counts.insert k (current - 1)
    return ⟨counts⟩

def elements_imp (c : ImperativeCounter) : List Key :=
  let entries := c.data.toList
  let flat :=
    entries.flatMap (fun (k, count) =>
      if count > 0 then List.replicate (Int.toNat count) k else [])
  flat.mergeSort (· < ·)

/-- Counting Property: Single update increments count by 1 -/
def count_prop (c : FunctionalCounter) (k : Key) : Prop :=
  get_func (update_one_func c k 1) k = get_func c k + 1

theorem count_thm (c : FunctionalCounter) (k : Key) : count_prop c k := by
  simp [count_prop, update_one_func, get_func]
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def update_imp_precond (c : ImperativeCounter) (s : List Key) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def update_imp (c : ImperativeCounter) (s : List Key) (h_precond : update_imp_precond (c) (s)) : ImperativeCounter :=
  -- !benchmark @start code
  Id.run do
    let mut counts := c.data
    for k in s do
      let current := (counts.get? k).getD 0
      counts := counts.insert k (current + 1)
    return ⟨counts⟩
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def update_imp_postcond (c : ImperativeCounter) (s : List Key) (result : ImperativeCounter)
    (h_precond : update_imp_precond (c) (s)) :=
  -- !benchmark @start postcond
  True
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

-- !benchmark @end proof_aux


theorem update_imp_spec_satisfied (c : ImperativeCounter) (s : List Key) (h_precond : update_imp_precond (c) (s)) :
    update_imp_postcond (c) (s) (update_imp (c) (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof