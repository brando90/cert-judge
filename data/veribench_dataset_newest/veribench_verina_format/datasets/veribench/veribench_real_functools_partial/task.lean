-- !benchmark @start import type=solution
import Mathlib
namespace FunctoolsPartial

open Std
-- !benchmark @end import

-- !benchmark @start solution_aux

/-- Basic positional argument token (value or placeholder). -/
inductive BaseArg
| value (v : Int)
| placeholder
deriving Repr, BEq

instance (n : Nat) : OfNat BaseArg n where
  ofNat := BaseArg.value (Int.ofNat n)

def Placeholder : BaseArg := BaseArg.placeholder

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def apply_imp_precond (func : Int → Int → Int → Int) (slots : List BaseArg)
    (baseKw : HashMap String Int) (pos : List Int) (kw : HashMap String Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

/-- State for argument processing loop. -/
structure ArgState where
  remainingArgs : List Int
  resultArgs : Array Int
deriving Repr

def fillSlots_imp (slots : List BaseArg) (args : List Int) : List Int × List Int :=
  Id.run do
    let mut state : ArgState := { remainingArgs := args, resultArgs := #[] }

    for slot in slots do
      match slot with
      | BaseArg.value v =>
          state := { state with resultArgs := state.resultArgs.push v }
      | BaseArg.placeholder =>
          match state.remainingArgs with
          | [] =>
              state := { state with resultArgs := state.resultArgs.push 0 }
          | h :: t =>
              state := { state with remainingArgs := t, resultArgs := state.resultArgs.push h }

    (state.resultArgs.toList, state.remainingArgs)

def mergeKw_imp (base override : HashMap String Int) : HashMap String Int :=
  Id.run do
    let mut acc := base
    for (k, v) in override do
      acc := acc.insert k v
    acc

def testFunc (a b : Int) (c : Int) : Int :=
  a * 100 + b * 10 + c

def getIdx (xs : List Int) (idx : Nat) (default : Int) : Int :=
  (xs[idx]?).getD default

-- !benchmark @end code_aux

def apply_imp (func : Int → Int → Int → Int) (slots : List BaseArg) (baseKw : HashMap String Int)
    (pos : List Int) (kw : HashMap String Int)
    (h_precond : apply_imp_precond (func) (slots) (baseKw) (pos) (kw)) : Int :=
  -- !benchmark @start code
  let (filled, leftover) := fillSlots_imp slots pos
  let finalArgs := filled ++ leftover
  let merged := mergeKw_imp baseKw kw
  let a := (merged.get? "a").getD (getIdx finalArgs 0 0)
  let b := (merged.get? "b").getD (getIdx finalArgs 1 0)
  let c := (merged.get? "c").getD (getIdx finalArgs 2 10)
  func a b c
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def apply_imp_postcond (func : Int → Int → Int → Int) (slots : List BaseArg)
    (baseKw : HashMap String Int) (pos : List Int) (kw : HashMap String Int)
    (result : Int)
    (h_precond : apply_imp_precond (func) (slots) (baseKw) (pos) (kw)) :=
  -- !benchmark @start postcond
  result = apply_imp (func) (slots) (baseKw) (pos) (kw) h_precond
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

def positional_prop (a b c : Int) : Prop :=
  (apply_imp (testFunc) ([BaseArg.value a, BaseArg.value b]) ({}) ([c]) ({}) (by simp))
    = testFunc a b c

theorem positional_thm (a b c : Int) : positional_prop a b c := by
  sorry

-- !benchmark @end proof_aux

theorem apply_imp_spec_satisfied (func : Int → Int → Int → Int) (slots : List BaseArg)
    (baseKw : HashMap String Int) (pos : List Int) (kw : HashMap String Int)
    (h_precond : apply_imp_precond (func) (slots) (baseKw) (pos) (kw)) :
    apply_imp_postcond (func) (slots) (baseKw) (pos) (kw)
      (apply_imp (func) (slots) (baseKw) (pos) (kw) h_precond) h_precond := by
  -- !benchmark @start proof
  simp [apply_imp_postcond]
  -- !benchmark @end proof

end FunctoolsPartial