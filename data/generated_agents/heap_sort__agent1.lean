import VeriBench.Common
import Std.Data.List.Basic

namespace HeapSort

def heapify (arr : List Int) (n : Nat) (i : Nat) : List Int :=
  let largest := i  -- Initialize largest as root
  let left := 2 * i + 1  -- Left child
  let right := 2 * i + 2  -- Right child
  
  -- If left child exists and is greater than root
  let largest := if left < n && arr.get? left |>.getD 0 > arr.get? largest |>.getD 0 then 
                  left 
                else 
                  largest
  
  -- If right child exists and is greater than largest so far
  let largest := if right < n && arr.get? right |>.getD 0 > arr.get? largest |>.getD 0 then 
                  right 
                else 
                  largest
  
  -- If largest is not root, swap and continue heapifying
  if largest != i then
    let arr := arr.set i (arr.get? largest |>.getD 0)
    let arr := arr.set largest (arr.get? i |>.getD 0)
    heapify arr n largest
  else
    arr

def buildMaxHeap (arr : List Int) : List Int :=
  let n := arr.length
  let rec helper (arr : List Int) (i : Int) : List Int :=
    if i < 0 then arr
    else helper (heapify arr n i.toNat) (i - 1)
  helper arr ((n / 2 - 1).toInt)

def extractElements (arr : List Int) : List Int :=
  let rec helper (arr : List Int) (i : Nat) : List Int :=
    if i == 0 then arr
    else
      let arr := arr.set 0 (arr.get? i |>.getD 0) |> (λ a => a.set i (arr.get? 0 |>.getD 0))
      let arr := heapify arr i 0
      helper arr (i - 1)
  helper arr (arr.length - 1)

def pre (arr : List Int) : Bool := true

def post (arr : List Int) (result : List Int) : Bool :=
  result.length == arr.length && 
  List.Perm arr result && 
  List.Sorted (· ≤ ·) result

def heapSort (arr : List Int) : List Int :=
  if arr.length ≤ 1 then arr
  else
    let result := buildMaxHeap arr
    extractElements result

theorem heapSortCorrect (arr : List Int) : post arr (heapSort arr) := sorry

def test1 : heapSort [3, 1, 2] = [1, 2, 3] := by rfl
def test2 : heapSort [] = [] := by rfl
def test3 : heapSort [1] = [1] := by rfl
def test4 : heapSort [5, 2, 4, 6, 1, 3] = [1, 2, 3, 4, 5, 6] := by rfl
def test5 : heapSort [9, 8, 7, 6, 5, 4, 3, 2, 1] = [1, 2, 3, 4, 5, 6, 7, 8, 9] := by rfl
def test6 : heapSort [2, 1] = [1, 2] := by rfl
def test7 : heapSort [3, 1, 4, 1, 2, 3] = [1, 1, 2, 3, 3, 4] := by rfl
def test8 : heapSort [5, 5, 5, 5, 5] = [5, 5, 5, 5, 5] := by rfl
def test9 : heapSort [3, 7, 1, 9, 2, 8, 4, 6, 5] = [1, 2, 3, 4, 5, 6, 7, 8, 9] := by rfl

end HeapSort
