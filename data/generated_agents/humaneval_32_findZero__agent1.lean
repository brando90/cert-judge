import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic

def poly (xs : List Float) (x : Float) : Float :=
  let rec loop (i : Nat) (acc : Float) (p : Float) :=
    match i with
    | 0 => acc
    | i+1 =>
      match xs.get? i with
      | none => acc
      | some c => loop i (acc + c * p) (p * x)
  loop xs.length 0.0 1.0

def pre (xs : List Float) (a : Float) (b : Float) (fuel : Nat) : Prop :=
  xs.length > 0 ∧ a < b ∧ poly xs a * poly xs b ≤ 0

def find_zero (xs : List Float) (a : Float) (b : Float) (fuel : Nat) : Float :=
  if h : pre xs a b fuel then
    let rec loop (left right : Float) (i : Nat) : Float :=
      if i = 0 then
        (left + right) / 2.0
      else
        let mid := (left + right) / 2.0
        let f_mid := poly xs mid
        if Float.abs f_mid < 1e-10 then
          mid
        else if poly xs left * f_mid ≤ 0 then
          loop left mid (i - 1)
        else
          loop mid right (i - 1)
    loop a b fuel
  else
    0.0  -- Arbitrary value for non-conforming inputs

def post (xs : List Float) (a : Float) (b : Float) (fuel : Nat) (result : Float) : Prop :=
  pre xs a b fuel →
  (a ≤ result ∧ result ≤ b) ∧ 
  (Float.abs (poly xs result) < 1e-2 ∨ 
   (∀ x, a ≤ x ∧ x ≤ b → Float.abs (poly xs x) ≥ Float.abs (poly xs result)))

theorem find_zero_correct (xs : List Float) (a b : Float) (fuel : Nat) :
  post xs a b fuel (find_zero xs a b fuel) :=
sorry

-- Tests
def test_find_zero : Bool :=
  let r1 := find_zero [1.0, 2.0] (-1.0) 0.0 100
  let r2 := find_zero [-6.0, 11.0, -6.0, 1.0] 0.0 2.0 100
  let r3 := find_zero [0.0, 1.0] (-1.0) 1.0 100
  let r4 := find_zero [4.0, -4.0, 1.0] 1.0 3.0 100
  
  Float.abs (r1 + 0.5) < 1e-2 &&
  Float.abs (r2 - 1.0) < 1e-2 &&
  Float.abs (r3 - 0.0) < 1e-2 &&
  Float.abs (r4 - 2.0) < 1e-2

#eval test_find_zero
