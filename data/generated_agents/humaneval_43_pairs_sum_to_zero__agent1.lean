/-
Implementation of HumanEval/43: pairs_sum_to_zero
-/

def pairsSumToZero (l : List Int) : Bool :=
  let rec checkPairs (i : Nat) (j : Nat) : Bool :=
    if i >= l.length then
      false
    else if j >= l.length then
      checkPairs (i + 1) (i + 2)
    else if l[i]! + l[j]! == 0 then
      true
    else
      checkPairs i (j + 1)
  checkPairs 0 1

/-
Tests
-/

#eval pairsSumToZero [1, 3, 5, 0] -- false
#eval pairsSumToZero [1, 3, -2, 1] -- false
#eval pairsSumToZero [1, 2, 3, 7] -- false
#eval pairsSumToZero [2, 4, -5, 3, 5, 7] -- true
#eval pairsSumToZero [1] -- false
#eval pairsSumToZero [-3, 9, -1, 3, 2, 30] -- true
#eval pairsSumToZero [-3, 9, -1, 3, 2, 31] -- true
#eval pairsSumToZero [-3, 9, -1, 4, 2, 30] -- false
#eval pairsSumToZero [-3, 9, -1, 4, 2, 31] -- false

/-
Specification
-/

def pairsSumToZeroSpec (l : List Int) : Bool :=
  l.enum.any fun (i, x) => 
    l.enum.any fun (j, y) => 
      i != j && x + y == 0

theorem pairsSumToZeroCorrect (l : List Int) : 
  pairsSumToZero l = pairsSumToZeroSpec l := by
  sorry
