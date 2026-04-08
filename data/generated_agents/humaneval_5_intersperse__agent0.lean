import VeriBench

namespace Intersperse

/-
  Insert a number 'delimeter' between every two consecutive elements of input list `numbers`
-/
def intersperse (numbers : List Int) (delimeter : Int) : List Int :=
  match numbers with
  | [] => []
  | [n] => [n]
  | n :: ns => n :: delimeter :: intersperse ns delimeter

/-- Specification of the intersperse function -/
def spec (numbers : List Int) (delimeter : Int) : List Int :=
  if numbers.isEmpty then
    []
  else
    let result := []
    let result := numbers.foldl (fun acc n => 
      if acc.isEmpty then [n]
      else acc ++ [delimeter, n]
    ) []
    result

/-- Precondition: always true -/
def pre (_numbers : List Int) (_delimeter : Int) : Prop := True

/-- Postcondition: The result should be as specified -/
def post (numbers : List Int) (delimeter : Int) (result : List Int) : Prop :=
  result = spec numbers delimeter

theorem intersperse_correct (numbers : List Int) (delimeter : Int)
  (h₁ : pre numbers delimeter) :
  post numbers delimeter (intersperse numbers delimeter) := by
  sorry

/-- Tests for the intersperse function -/
def tests : IO Unit := do
  VeriBench.check (intersperse [] 7) []
  VeriBench.check (intersperse [5, 6, 3, 2] 8) [5, 8, 6, 8, 3, 8, 2]
  VeriBench.check (intersperse [2, 2, 2] 2) [2, 2, 2, 2, 2]
  VeriBench.check (intersperse [1, 2, 3] 4) [1, 4, 2, 4, 3]

end Intersperse
