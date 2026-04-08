/-
VeriBench: HumanEval/37: sort_even
-/

def sort_even (l : List Int) : List Int :=
  let evens := l.enum.filter (fun (i, _) => i % 2 == 0).map (fun (_, v) => v)
  let odds := l.enum.filter (fun (i, _) => i % 2 == 1).map (fun (_, v) => v)
  let sortedEvens := evens.qsort (fun a b => a ≤ b)
  let zipped := List.zip sortedEvens odds
  let ans := zipped.foldl (fun acc (e, o) => acc ++ [e, o]) []
  if evens.length > odds.length then
    ans ++ [sortedEvens.getLast (evens.head!)]
  else
    ans

def sort_even_spec (l : List Int) : List Int :=
  let evens := l.enum.filter (fun (i, _) => i % 2 == 0).map (fun (_, v) => v)
  let odds := l.enum.filter (fun (i, _) => i % 2 == 1).map (fun (_, v) => v)
  let sortedEvens := evens.qsort (fun a b => a ≤ b)
  let zipped := List.zip sortedEvens odds
  let ans := zipped.foldl (fun acc (e, o) => acc ++ [e, o]) []
  if evens.length > odds.length then
    ans ++ [sortedEvens.getLast (evens.head!)]
  else
    ans

theorem sort_even_correct (l : List Int) : sort_even l = sort_even_spec l := by
  sorry

/-- Tests for sort_even -/
def test_sort_even : IO Unit := do
  let test1 := [1, 2, 3]
  let test2 := [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10]
  let test3 := [5, 8, -12, 4, 23, 2, 3, 11, 12, -10]
  
  assert! (sort_even test1 == [1, 2, 3])
  assert! (sort_even test2 == [-10, 3, -5, 2, -3, 3, 5, 0, 9, 1, 123])
  assert! (sort_even test3 == [-12, 8, 3, 4, 5, 2, 12, 11, 23, -10])
  
  IO.println "All tests passed!"

#eval test_sort_even
