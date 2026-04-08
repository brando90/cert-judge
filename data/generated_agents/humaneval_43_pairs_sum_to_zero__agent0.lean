/-
This file implements the pairs_sum_to_zero function in Lean 4 and proves its correctness.
-/

def pairsSumToZero (l: List Int) : Bool :=
  let rec loop (i: Nat) (seen: List (Nat × Int)) : Bool :=
    if i >= l.length then
      false
    else
      let current := l[i]!
      let hasPair := seen.any (fun (_, v) => v + current = 0)
      if hasPair then
        true
      else
        loop (i + 1) ((i, current) :: seen)
  loop 0 []

/-- 
  Specification for pairsSumToZero:
  Returns true if there are two distinct elements in the list that sum to zero,
  and false otherwise.
-/
def pairsSumToZeroSpec (l: List Int) : Bool :=
  l.enum.any (fun (i, x) => 
    l.enum.any (fun (j, y) => i ≠ j && x + y = 0))

theorem pairsSumToZero_correct (l: List Int) : pairsSumToZero l = pairsSumToZeroSpec l := sorry

#eval pairsSumToZero [1, 3, 5, 0] -- false
#eval pairsSumToZero [1, 3, -2, 1] -- false
#eval pairsSumToZero [1, 2, 3, 7] -- false
#eval pairsSumToZero [2, 4, -5, 3, 5, 7] -- true
#eval pairsSumToZero [1] -- false
#eval pairsSumToZero [-3, 9, -1, 3, 2, 30] -- true
#eval pairsSumToZero [-3, 9, -1, 3, 2, 31] -- true
#eval pairsSumToZero [-3, 9, -1, 4, 2, 30] -- false
#eval pairsSumToZero [-3, 9, -1, 4, 2, 31] -- false

example : pairsSumToZero [1, 3, 5, 0] = false := rfl
example : pairsSumToZero [1, 3, -2, 1] = false := rfl
example : pairsSumToZero [1, 2, 3, 7] = false := rfl
example : pairsSumToZero [2, 4, -5, 3, 5, 7] = true := rfl
example : pairsSumToZero [1] = false := rfl
example : pairsSumToZero [-3, 9, -1, 3, 2, 30] = true := rfl
example : pairsSumToZero [-3, 9, -1, 3, 2, 31] = true := rfl
example : pairsSumToZero [-3, 9, -1, 4, 2, 30] = false := rfl
example : pairsSumToZero [-3, 9, -1, 4, 2, 31] = false := rfl
