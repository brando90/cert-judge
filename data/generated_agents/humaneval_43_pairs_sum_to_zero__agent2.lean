/--
  Implementation of pairs_sum_to_zero function that checks if there are two distinct elements in the list that sum to zero.
-/
def pairsSumToZero (l : List Int) : Bool :=
  let rec loop (i : Nat) : Bool :=
    if i >= l.length then
      false
    else
      let l1 := l[i]!
      let rec innerLoop (j : Nat) : Bool :=
        if j >= l.length then
          false
        else if l1 + l[j]! == 0 then
          true
        else
          innerLoop (j + 1)
      
      if innerLoop (i + 1) then
        true
      else
        loop (i + 1)
  
  loop 0

/--
  Specification for pairsSumToZero:
  Returns true if there are two distinct elements in the list that sum to zero, and false otherwise.
-/
def pairsSumToZeroSpec (l : List Int) : Bool :=
  l.anyPairs (fun x y => x + y == 0)

/--
  Tests for pairsSumToZero function
-/
def pairsSumToZeroTest : IO Unit := do
  assert! (pairsSumToZero [1, 3, 5, 0] == false)
  assert! (pairsSumToZero [1, 3, -2, 1] == false)
  assert! (pairsSumToZero [1, 2, 3, 7] == false)
  assert! (pairsSumToZero [2, 4, -5, 3, 5, 7] == true)
  assert! (pairsSumToZero [1] == false)
  assert! (pairsSumToZero [-3, 9, -1, 3, 2, 30] == true)
  assert! (pairsSumToZero [-3, 9, -1, 3, 2, 31] == true)
  assert! (pairsSumToZero [-3, 9, -1, 4, 2, 30] == false)
  assert! (pairsSumToZero [-3, 9, -1, 4, 2, 31] == false)
  IO.println "All tests passed!"

/--
  Theorem stating that our implementation satisfies the specification.
-/
theorem pairsSumToZero_correct (l : List Int) : pairsSumToZero l = pairsSumToZeroSpec l := by
  sorry
