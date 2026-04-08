/-
# Intersperse

This function inserts a number 'delimeter' between every two consecutive elements of input list `numbers'.
-/

import Lean.Data.HashMap
import Mathlib.Data.List.Basic

def intersperse (numbers : List Int) (delimeter : Int) : List Int :=
  match numbers with
  | [] => []
  | [x] => [x]
  | x :: xs => x :: delimeter :: intersperse xs delimeter

theorem intersperse_nil (delimeter : Int) :
  intersperse [] delimeter = [] := rfl

theorem intersperse_singleton (x delimeter : Int) :
  intersperse [x] delimeter = [x] := rfl

theorem intersperse_cons (x : Int) (xs : List Int) (delimeter : Int) :
  intersperse (x :: xs) delimeter = 
    match xs with
    | [] => [x]
    | _ => x :: delimeter :: intersperse xs delimeter
  := by
  cases xs <;> rfl

/--
Specification for the intersperse function.
-/
def intersperse_spec (numbers : List Int) (delimeter : Int) : List Int :=
  if numbers.isEmpty then
    []
  else
    let result := []
    let result := numbers.take (numbers.length - 1)
                  |> List.foldl (fun acc n => acc ++ [n, delimeter]) []
    result ++ [numbers.getLast (by simp [numbers.isEmpty])]

theorem intersperse_eq_spec (numbers : List Int) (delimeter : Int) :
  intersperse numbers delimeter = intersperse_spec numbers delimeter := by
  sorry

def test_intersperse : IO Unit := do
  assert! (intersperse ([] : List Int) 7 == [])
  assert! (intersperse [5, 6, 3, 2] 8 == [5, 8, 6, 8, 3, 8, 2])
  assert! (intersperse [2, 2, 2] 2 == [2, 2, 2, 2, 2])
  IO.println "All tests passed!"

def main : IO Unit :=
  test_intersperse
