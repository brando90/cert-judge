import Mathlib.Data.Real.Basic
import Mathlib.Data.List.MinMax

namespace VeriBench.HumanEval21

/-- 
Given list of numbers (of at least two elements), apply a linear transform to that list,
such that the smallest number will become 0 and the largest will become 1
-/
def rescaleToUnit (numbers : List Float) : List Float :=
  if h : numbers.length ≥ 2 then
    let minNumber := numbers.minimum?.getD 0
    let maxNumber := numbers.maximum?.getD 0
    if minNumber = maxNumber then
      List.replicate numbers.length 0
    else
      numbers.map (fun x => (x - minNumber) / (maxNumber - minNumber))
  else
    numbers

def test1 : rescaleToUnit [2.0, 49.9] = [0.0, 1.0] := by rfl
def test2 : rescaleToUnit [100.0, 49.9] = [1.0, 0.0] := by rfl
def test3 : rescaleToUnit [1.0, 2.0, 3.0, 4.0, 5.0] = [0.0, 0.25, 0.5, 0.75, 1.0] := by rfl
def test4 : rescaleToUnit [2.0, 1.0, 5.0, 3.0, 4.0] = [0.25, 0.0, 1.0, 0.5, 0.75] := by rfl
def test5 : rescaleToUnit [12.0, 11.0, 15.0, 13.0, 14.0] = [0.25, 0.0, 1.0, 0.5, 0.75] := by rfl

/-- Precondition: The input list should have at least two elements -/
def rescaleToUnit_pre (numbers : List Float) : Prop :=
  numbers.length ≥ 2

/-- 
Postcondition: 
1. The output list has the same length as the input list
2. If all elements in the input list are the same, the output list contains all zeros
3. Otherwise, the minimum value in the output is 0 and the maximum is 1
4. The relative ordering of elements is preserved
-/
def rescaleToUnit_post (numbers : List Float) (result : List Float) : Prop :=
  result.length = numbers.length ∧
  (∀ i j, i < numbers.length → j < numbers.length → 
    numbers.get ⟨i, by exact Nat.lt_of_lt_of_le i.2 (by simp [rescaleToUnit_pre numbers])⟩ ≤ 
    numbers.get ⟨j, by exact Nat.lt_of_lt_of_le j.2 (by simp [rescaleToUnit_pre numbers])⟩ → 
    result.get ⟨i, by exact Nat.lt_of_lt_of_le i.2 (by simp [rescaleToUnit_pre numbers])⟩ ≤ 
    result.get ⟨j, by exact Nat.lt_of_lt_of_le j.2 (by simp [rescaleToUnit_pre numbers])⟩) ∧
  (let minNumber := numbers.minimum?.getD 0
   let maxNumber := numbers.maximum?.getD 0
   if minNumber = maxNumber then
     result = List.replicate numbers.length 0
   else
     (∃ i < numbers.length, result.get ⟨i, by exact Nat.lt_of_lt_of_le i.2 (by simp [rescaleToUnit_pre numbers])⟩ = 0) ∧
     (∃ i < numbers.length, result.get ⟨i, by exact Nat.lt_of_lt_of_le i.2 (by simp [rescaleToUnit_pre numbers])⟩ = 1))

/-- Correctness theorem for the rescaleToUnit function -/
theorem rescaleToUnit_correct (numbers : List Float) :
  rescaleToUnit_pre numbers → rescaleToUnit_post numbers (rescaleToUnit numbers) := by
  sorry

end VeriBench.HumanEval21
