import Mathlib.Data.List.Basic
import Mathlib.Data.List.Perm
import Mathlib.Tactic

namespace QuickSort

def pre (arr : List Int) : Prop := True

def partition (arr : List Int) (low high : Nat) : Nat × List Int :=
  if h : high < arr.length then
    let pivot := arr[high]
    let rec partitionLoop (arr : List Int) (i j : Nat) : Nat × List Int :=
      if j < high then
        if h' : j < arr.length ∧ i < arr.length then
          if arr[j] <= pivot then
            let arr' := arr.swap i j
            partitionLoop arr' (i + 1) (j + 1)
          else
            partitionLoop arr i (j + 1)
        else
          (i, arr)
      else
        let arr' := arr.swap (i + 1) high
        (i + 1, arr')

    partitionLoop arr low low
  else
    (low, arr)

partial def quickSortHelper (arr : List Int) (low high : Nat) : List Int :=
  if low < high then
    let (pivotIdx, arr') := partition arr low high
    if pivotIdx > 0 then
      let arr'' := quickSortHelper arr' low (pivotIdx - 1)
      quickSortHelper arr'' (pivotIdx + 1) high
    else
      quickSortHelper arr' (pivotIdx + 1) high
  else
    arr

def quickSort (arr : List Int) : List Int :=
  if arr.length <= 1 then
    arr
  else
    quickSortHelper arr 0 (arr.length - 1)

def post (arr result : List Int) : Prop :=
  result.Sorted (· ≤ ·) ∧ result.Perm arr

theorem quickSort_correct (arr : List Int) (h : pre arr) : post arr (quickSort arr) := by
  sorry

-- Tests
def test_quickSort : IO Unit := do
  let test1 := quickSort [3, 1, 2]
  IO.println s!"Test 1: {test1 == [1, 2, 3]}"
  
  let test2 := quickSort []
  IO.println s!"Test 2: {test2 == []}"
  
  let test3 := quickSort [1]
  IO.println s!"Test 3: {test3 == [1]}"
  
  let test4 := quickSort [5, 2, 4, 6, 1, 3]
  IO.println s!"Test 4: {test4 == [1, 2, 3, 4, 5, 6]}"
  
  let test5 := quickSort [9, 8, 7, 6, 5, 4, 3, 2, 1]
  IO.println s!"Test 5: {test5 == [1, 2, 3, 4, 5, 6, 7, 8, 9]}"
  
  let test6 := quickSort [2, 1]
  IO.println s!"Test 6: {test6 == [1, 2]}"
  
  let test7 := quickSort [3, 1, 4, 1, 2, 3]
  IO.println s!"Test 7: {test7 == [1, 1, 2, 3, 3, 4]}"
  
  let test8 := quickSort [5, 5, 5, 5, 5]
  IO.println s!"Test 8: {test8 == [5, 5, 5, 5, 5]}"

#eval test_quickSort

end QuickSort
