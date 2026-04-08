import Std.Data.List.Basic

/--
  Merges two sorted lists into a single sorted list.
-/
def merge (left right : List Int) : List Int :=
  match left, right with
  | [], r => r
  | l, [] => l
  | l::ls, r::rs =>
    if l ≤ r then
      l :: merge ls (r::rs)
    else
      r :: merge (l::ls) rs

/--
  Sorts a list using the merge sort algorithm.
  It divides the array into halves, recursively sorts them, and then merges 
  the sorted halves back together.
-/
def mergeSort (arr : List Int) : List Int :=
  match arr with
  | [] => []
  | [x] => [x]
  | _ =>
    let mid := arr.length / 2
    let left := mergeSort (arr.take mid)
    let right := mergeSort (arr.drop mid)
    merge left right

/--
  Predicate that checks if a list is sorted in non-decreasing order.
-/
def isSorted (arr : List Int) : Prop :=
  match arr with
  | [] => True
  | [_] => True
  | x::y::xs => x ≤ y ∧ isSorted (y::xs)

/--
  Predicate that checks if two lists are permutations of each other.
-/
def isPermutation (arr1 arr2 : List Int) : Prop :=
  ∀ x, arr1.count x = arr2.count x

/--
  Precondition for merge sort - the input must be a list of integers.
  For Lean, this is automatically satisfied by the type system.
-/
def pre (arr : List Int) : Prop := True

/--
  Postcondition for merge sort - the output must be sorted and a permutation of the input.
-/
def post (arr result : List Int) : Prop :=
  isSorted result ∧ isPermutation arr result

/--
  Correctness theorem for merge sort.
-/
theorem mergeSortCorrect (arr : List Int) : pre arr → post arr (mergeSort arr) := by
  sorry

/--
  Test cases for merge sort.
-/
def testMergeSort : IO Unit := do
  -- Basic functionality tests
  assert! (mergeSort [3, 1, 2] == [1, 2, 3])
  assert! (mergeSort [1, 2, 3] == [1, 2, 3])
  assert! (mergeSort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (mergeSort ([] : List Int) == [])
  assert! (mergeSort [1] == [1])
  
  -- Larger arrays
  assert! (mergeSort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (mergeSort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (mergeSort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (mergeSort [2, 1] == [1, 2])
  assert! (mergeSort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (mergeSort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (mergeSort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (mergeSort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (mergeSort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (mergeSort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  
  -- Larger test case
  let largeArr := [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42]
  let expected := [11, 12, 22, 25, 34, 42, 50, 64, 76, 88, 90]
  assert! (mergeSort largeArr == expected)
  
  IO.println "All tests passed."

/--
  Helper lemmas about merge and mergeSort.
-/
theorem mergeSorted {l r : List Int} : isSorted l → isSorted r → isSorted (merge l r) := by
  sorry

theorem mergePermutation {l r : List Int} : 
  isPermutation (l ++ r) (merge l r) := by
  sorry
