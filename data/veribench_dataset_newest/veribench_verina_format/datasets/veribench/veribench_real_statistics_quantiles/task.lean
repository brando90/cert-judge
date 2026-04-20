-- !benchmark @start import type=solution
import Mathlib
namespace StatisticsQuantiles
-- !benchmark @end import

-- !benchmark @start solution_aux
inductive QuantilesError where
  | statisticsError (msg : String)
  | valueError (msg : String)
  deriving DecidableEq, Repr

instance (ε α : Type) [DecidableEq ε] [DecidableEq α] : DecidableEq (Except ε α) := by
  intro x y
  cases x with
  | error e =>
    cases y with
    | error e' =>
      match decEq e e' with
      | isTrue h =>
        exact isTrue (by cases h; rfl)
      | isFalse h =>
        exact isFalse (by
          intro h'
          cases h'
          exact h rfl)
    | ok a =>
      exact isFalse (by intro h; cases h)
  | ok a =>
    cases y with
    | error e' =>
      exact isFalse (by intro h; cases h)
    | ok a' =>
      match decEq a a' with
      | isTrue h =>
        exact isTrue (by cases h; rfl)
      | isFalse h =>
        exact isFalse (by
          intro h'
          cases h'
          exact h rfl)

structure Rat where
  num : Int
  den : Nat
  deriving DecidableEq

instance : Repr Rat where
  reprPrec r _ := s!"{r.num}/{r.den}"

namespace Rat

def normalize (r : Rat) : Rat :=
  if r.den = 0 then
    { num := 0, den := 1 }
  else
    let g := Nat.gcd r.num.natAbs r.den
    let num' := r.num / Int.ofNat g
    let den' := r.den / g
    { num := num', den := den' }

def mkRat (num : Int) (den : Nat) : Rat :=
  normalize { num := num, den := den }

def ofInt (z : Int) : Rat := { num := z, den := 1 }

def ofNat (n : Nat) : Rat := { num := Int.ofNat n, den := 1 }

instance : OfNat Rat n := ⟨ofNat n⟩

instance : Neg Rat := ⟨fun a => { num := -a.num, den := a.den }⟩

def add (a b : Rat) : Rat :=
  normalize
    { num := a.num * Int.ofNat b.den + b.num * Int.ofNat a.den
      den := a.den * b.den }

def sub (a b : Rat) : Rat := add a (-b)

def mul (a b : Rat) : Rat :=
  normalize { num := a.num * b.num, den := a.den * b.den }

def divNat (a : Rat) (n : Nat) : Rat :=
  if n = 0 then { num := 0, den := 1 }
  else normalize { num := a.num, den := a.den * n }

instance : HAdd Rat Rat Rat := ⟨add⟩
instance : HSub Rat Rat Rat := ⟨sub⟩
instance : HMul Rat Rat Rat := ⟨mul⟩
instance : HDiv Rat Nat Rat := ⟨divNat⟩

def leBool (a b : Rat) : Bool :=
  decide (a.num * Int.ofNat b.den ≤ b.num * Int.ofNat a.den)

end Rat

open Rat

def rat (num : Int) (den : Nat) : Rat := Rat.mkRat num den

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def benchmark_quantiles_precond (data : List Rat) (n : Nat) (method : String) : Prop :=
  -- !benchmark @start precond
  data.length ≥ 2 ∧ 1 ≤ n ∧ (method = "inclusive" ∨ method = "exclusive")
  -- !benchmark @end precond


-- !benchmark @start code_aux
def nthOrZero (xs : List Rat) (idx : Nat) : Rat :=
  (xs[idx]?).getD 0

def quantiles (data : List Rat) (n : Nat := 4) (method : String := "exclusive") :
    Except QuantilesError (List Rat) :=
  if n == 0 then
    Except.error (QuantilesError.statisticsError "n must be at least 1")
  else
    let sorted := data.mergeSort Rat.leBool
    let ld := sorted.length
    if ld < 2 then
      Except.error (QuantilesError.statisticsError "must have at least two data points")
    else if method == "inclusive" then
      let m := ld - 1
      let indices := (List.range (n - 1)).map (fun k => k + 1)
      Except.ok <|
        indices.map (fun i =>
          let prod := i * m
          let j := prod / n
          let delta := prod % n
          let left := nthOrZero sorted j
          let right := nthOrZero sorted (j + 1)
          ((left * Rat.ofNat (n - delta)) + (right * Rat.ofNat delta)) / n
        )
    else if method == "exclusive" then
      let m := ld + 1
      let indices := (List.range (n - 1)).map (fun k => k + 1)
      Except.ok <|
        indices.map (fun i =>
          let prod := i * m
          let j0 := prod / n
          let j := if j0 < 1 then 1 else if j0 > ld - 1 then ld - 1 else j0
          let deltaInt : Int := (Int.ofNat prod) - (Int.ofNat (j * n))
          let left := nthOrZero sorted (j - 1)
          let right := nthOrZero sorted j
          ((left * Rat.ofInt (Int.ofNat n - deltaInt)) + (right * Rat.ofInt deltaInt)) / n
        )
    else
      Except.error (QuantilesError.valueError s!"Unknown method: {method}")
-- !benchmark @end code_aux


def benchmark_quantiles (data : List Rat) (n : Nat) (method : String)
    (h_precond : benchmark_quantiles_precond (data) (n) (method)) : Except QuantilesError (List Rat) :=
  -- !benchmark @start code
  let validMethod := method == "inclusive" || method == "exclusive"
  if (data.length < 2) || (n == 0) || (!validMethod) then
    Except.error
      (QuantilesError.statisticsError
        "benchmark_quantiles requires at least 2 data points, n >= 1, and valid method")
  else
    quantiles data n method
  -- !benchmark @end code


-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux


@[reducible, simp]
def benchmark_quantiles_postcond (data : List Rat) (n : Nat) (method : String)
    (result : Except QuantilesError (List Rat))
    (h_precond : benchmark_quantiles_precond (data) (n) (method)) : Prop :=
  -- !benchmark @start postcond
  (Pre := benchmark_quantiles_precond data n method) →
    (∃ xs, benchmark_quantiles data n method (by sorry) = Except.ok xs ∧ xs.length = n - 1) ∧
    (∀ perm, List.Perm perm data →
      benchmark_quantiles perm n method (by sorry) = benchmark_quantiles data n method (by sorry)) ∧
    (∀ c,
      benchmark_quantiles (data.map (fun x => x + c)) n method (by sorry) =
        (benchmark_quantiles data n method (by sorry)).map (fun xs => xs.map (fun x => x + c)))
  -- !benchmark @end postcond


-- !benchmark @start proof_aux
-- !benchmark @end proof_aux


theorem benchmark_quantiles_spec_satisfied (data : List Rat) (n : Nat) (method : String)
    (h_precond : benchmark_quantiles_precond (data) (n) (method)) :
    benchmark_quantiles_postcond (data) (n) (method)
      (benchmark_quantiles (data) (n) (method) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof