import Std.Data.List.Basic
import Std.Data.List.Lemmas

/--
  Heap sort for a list of integers.
  Edge cases:
  - Empty or single-element list returns copy.
-/
def heapSort (arr : List Int) : List Int :=
  if arr.length ≤ 1 then 
    arr
  else
    let rec heapify (arr : List Int) (n : Nat) (i : Nat) : List Int :=
      let largest := i
      let left := 2 * i + 1
      let right := 2 * i + 2
      
      let largest := 
        if left < n && arr.get? left |>.map (· > arr.get! largest) |>.getD false then
          left
        else
          largest
          
      let largest :=
        if right < n && arr.get? right |>.map (· > arr.get! largest) |>.getD false then
          right
        else
          largest
          
      if largest != i then
        let arr := arr.set! i (arr.get! largest) |>.set! largest (arr.get! i)
        heapify arr n largest
      else
        arr
        
    let rec buildMaxHeap (arr : List Int) : List Int :=
      let n := arr.length
      let rec loop (arr : List Int) (i : Int) : List Int :=
        if i < 0 then
          arr
        else
          let arr := heapify arr n i.toNat
          loop arr (i - 1)
      loop arr ((n / 2 - 1).toInt)
      
    let result := arr
    let n := result.length
    
    let result := buildMaxHeap result
    
    let rec extractElements (result : List Int) (i : Nat) : List Int :=
      if i == 0 then
        result
      else
        let result := result.set! 0 (result.get! i) |>.set! i (result.get! 0)
        let result := heapify result i 0
        extractElements result (i - 1)
        
    extractElements result (n - 1)

/-- Precondition: input must be a list of integers -/
def heapSortPre (arr : List Int) : Prop := True

/-- Postcondition: output is a sorted permutation of the input -/
def heapSortPost (arr : List Int) (result : List Int) : Prop :=
  List.Sorted (· ≤ ·) result ∧ result.Perm arr

theorem heapSortCorrect (arr : List Int) (h : heapSortPre arr) : 
  heapSortPost arr (heapSort arr) := by
  sorry

/-! ## Tests -/

def test1 : IO Unit := do
  let result := heapSort [3, 1, 2]
  IO.println s!"Test 1: {result}"
  assert! result == [1, 2, 3]

def test2 : IO Unit := do
  let result := heapSort []
  IO.println s!"Test 2: {result}"
  assert! result == []

def test3 : IO Unit := do
  let result := heapSort [1]
  IO.println s!"Test 3: {result}"
  assert! result == [1]

def test4 : IO Unit := do
  let result := heapSort [5, 2, 4, 6, 1, 3]
  IO.println s!"Test 4: {result}"
  assert! result == [1, 2, 3, 4, 5, 6]

def test5 : IO Unit := do
  let result := heapSort [9, 8, 7, 6, 5, 4, 3, 2, 1]
  IO.println s!"Test 5: {result}"
  assert! result == [1, 2, 3, 4, 5, 6, 7, 8, 9]

def test6 : IO Unit := do
  let result := heapSort [3, 1, 4, 1, 2, 3]
  IO.println s!"Test 6: {result}"
  assert! result == [1, 1, 2, 3, 3, 4]

def runTests : IO Unit := do
  test1
  test2
  test3
  test4
  test5
  test6
  IO.println "All tests passed!"

#eval runTests
