import Mathlib

namespace HeapsortProblems

/-!
## Helpers
-/


def mySwap (arr : Array Nat) (i j : Nat) : Array Nat :=
  if hi : i < arr.size then
    if hj : j < arr.size then
      let vi := arr[i]
      let vj := arr[j]
      (arr.set i vj).set j vi (by simp [Array.size_set]; exact hj)
    else arr
  else arr

/-!
## Binary Heap Primitives (0-based)
-/


def parent (i : Nat) : Nat := (i - 1) / 2


def left (i : Nat) : Nat := 2 * i + 1


def right (i : Nat) : Nat := 2 * i + 2


def maxHeapify (arr : Array Nat) (i : Nat) (heapSize : Nat) : Array Nat :=
  let rec loop (arr : Array Nat) (idx : Nat) (fuel : Nat) : Array Nat :=
    match fuel with
    | 0 => arr
    | fuel' + 1 =>
      let l := left idx
      let r := right idx
      let largest1 := if l < heapSize && l < arr.size && arr[l]! > arr[idx]! then l else idx
      let largest := if r < heapSize && r < arr.size && arr[r]! > arr[largest1]! then r else largest1
      if largest != idx then
        loop (mySwap arr idx largest) largest fuel'
      else
        arr
  loop arr i heapSize


def buildMaxHeap (arr : Array Nat) : Array Nat :=
  Id.run do
    let n := arr.size
    if n == 0 then return arr
    let mut result := arr
    let mut i := n / 2
    while i > 0 do
      i := i - 1
      result := maxHeapify result i n
    return result

/-!
## Problem 6-1: Building a Heap Using Insertion

BUILD-MAX-HEAP'(A):
  A.heap-size = 1
  for i = 1 to A.length - 1
      MAX-HEAP-INSERT(A, A[i])
-/


def siftUp (arr : Array Nat) (i : Nat) : Array Nat :=
  let rec loop (arr : Array Nat) (idx : Nat) (fuel : Nat) : Array Nat :=
    match fuel with
    | 0 => arr
    | fuel' + 1 =>
      if idx > 0 && idx < arr.size && parent idx < arr.size && arr[parent idx]! < arr[idx]! then
        loop (mySwap arr idx (parent idx)) (parent idx) fuel'
      else
        arr
  loop arr i i


def heapIncreaseKey (arr : Array Nat) (i : Nat) (key : Nat) : Array Nat :=
  let arr' := arr.set! i key
  siftUp arr' i


def maxHeapInsert (arr : Array Nat) (key : Nat) (heapSize : Nat) : Array Nat × Nat :=
  let arr' := if heapSize < arr.size then arr.set! heapSize 0 else arr.push 0
  let newSize := heapSize + 1
  let arr'' := heapIncreaseKey arr' (newSize - 1) key
  (arr'', newSize)


def buildMaxHeapPrime (arr : Array Nat) : Array Nat :=
  Id.run do
    if arr.size == 0 then return arr
    let mut result := arr
    let mut heapSize := 1
    for i in [1:arr.size] do
      let val := arr[i]!
      let (newArr, newSize) := maxHeapInsert result val heapSize
      result := newArr
      heapSize := newSize
    return result

/-!
## Problem 6-2: d-ary Heaps

A d-ary heap is a generalization of a binary heap where each node has d children.
Height is Θ(log_d n).
-/


def dAryParent (i : Nat) (d : Nat) : Nat := (i - 1) / d


def dAryChild (i : Nat) (j : Nat) (d : Nat) : Nat := d * i + j + 1


def dAryFindLargestChild (arr : Array Nat) (i : Nat) (heapSize d : Nat) : Nat :=
  Id.run do
    let mut largest := i
    for j in List.range d do
      let c := dAryChild i j d
      if c < heapSize && c < arr.size && arr[c]! > arr[largest]! then
        largest := c
    return largest


def dAryMaxHeapify (arr : Array Nat) (i : Nat) (heapSize d : Nat) : Array Nat :=
  let rec loop (arr : Array Nat) (idx : Nat) (fuel : Nat) : Array Nat :=
    match fuel with
    | 0 => arr
    | fuel' + 1 =>
      let largest := dAryFindLargestChild arr idx heapSize d
      if largest != idx then
        loop (mySwap arr idx largest) largest fuel'
      else
        arr
  loop arr i heapSize


def dAryExtractMax (arr : Array Nat) (heapSize d : Nat) : Nat × Array Nat × Nat :=
  if heapSize == 0 then (0, arr, 0)
  else
    let maxVal := arr[0]!
    let arr' := arr.set! 0 arr[heapSize - 1]!
    let newSize := heapSize - 1
    let arr'' := dAryMaxHeapify arr' 0 newSize d
    (maxVal, arr'', newSize)


def dArySiftUp (arr : Array Nat) (i d : Nat) : Array Nat :=
  let rec loop (arr : Array Nat) (idx : Nat) (fuel : Nat) : Array Nat :=
    match fuel with
    | 0 => arr
    | fuel' + 1 =>
      if idx > 0 && idx < arr.size && dAryParent idx d < arr.size && arr[dAryParent idx d]! < arr[idx]! then
        loop (mySwap arr idx (dAryParent idx d)) (dAryParent idx d) fuel'
      else
        arr
  loop arr i i


def dAryIncreaseKey (arr : Array Nat) (i : Nat) (key : Nat) (d : Nat) : Array Nat :=
  let arr' := arr.set! i key
  dArySiftUp arr' i d


def dAryInsert (arr : Array Nat) (key : Nat) (heapSize d : Nat) : Array Nat × Nat :=
  let arr' := if heapSize < arr.size then arr.set! heapSize 0 else arr.push 0
  let newSize := heapSize + 1
  let arr'' := dAryIncreaseKey arr' (newSize - 1) key d
  (arr'', newSize)


def buildDAryMaxHeap (arr : Array Nat) (d : Nat) : Array Nat :=
  Id.run do
    let n := arr.size
    if n == 0 then return arr
    let mut result := arr
    let mut i := n / d
    while i > 0 do
      i := i - 1
      result := dAryMaxHeapify result i n d
    return result

/-!
## Problem 6-3: Young Tableaux (Simplified)

An m x n Young tableau is an m x n matrix where each row is sorted left-to-right
and each column is sorted top-to-bottom. We use a sentinel value (1000000) for
empty/infinity entries.

Represented as a flattened `Array Nat` with `rows * cols` elements.
-/


def sentinel : Nat := 1000000


def youngGet (tab : Array Nat) (cols : Nat) (row col : Nat) : Nat :=
  tab[row * cols + col]!


def youngSet (tab : Array Nat) (cols : Nat) (row col : Nat) (val : Nat) : Array Nat :=
  tab.set! (row * cols + col) val


def youngifyDown (tab : Array Nat) (rows cols : Nat) (r c : Nat) : Array Nat :=
  let rec loop (tab : Array Nat) (row col : Nat) (fuel : Nat) : Array Nat :=
    match fuel with
    | 0 => tab
    | fuel' + 1 =>
      let curr := youngGet tab cols row col
      let belowVal := if row + 1 < rows then youngGet tab cols (row + 1) col else curr + 1
      let rightVal := if col + 1 < cols then youngGet tab cols row (col + 1) else curr + 1
      if belowVal < curr && belowVal <= rightVal then
        let tab' := youngSet (youngSet tab cols row col belowVal) cols (row + 1) col curr
        loop tab' (row + 1) col fuel'
      else if rightVal < curr then
        let tab' := youngSet (youngSet tab cols row col rightVal) cols row (col + 1) curr
        loop tab' row (col + 1) fuel'
      else
        tab
  loop tab r c (rows * cols)


def youngExtractMin (tab : Array Nat) (rows cols : Nat) : Nat × Array Nat :=
  let minVal := youngGet tab cols 0 0
  let tab' := youngSet tab cols 0 0 sentinel
  let tab'' := youngifyDown tab' rows cols 0 0
  (minVal, tab'')


def youngBubbleUp (tab : Array Nat) (cols : Nat) (r c : Nat) : Array Nat :=
  let rec loop (tab : Array Nat) (row col : Nat) (fuel : Nat) : Array Nat :=
    match fuel with
    | 0 => tab
    | fuel' + 1 =>
      let curr := youngGet tab cols row col
      let aboveVal := if row > 0 then youngGet tab cols (row - 1) col else 0
      let leftVal := if col > 0 then youngGet tab cols row (col - 1) else 0
      if row > 0 && aboveVal > curr && aboveVal >= leftVal then
        let tab' := youngSet (youngSet tab cols row col aboveVal) cols (row - 1) col curr
        loop tab' (row - 1) col fuel'
      else if col > 0 && leftVal > curr then
        let tab' := youngSet (youngSet tab cols row col leftVal) cols row (col - 1) curr
        loop tab' row (col - 1) fuel'
      else
        tab
  loop tab r c (r * cols + c + 1)


def youngInsert (tab : Array Nat) (key : Nat) (rows cols : Nat) : Array Nat :=
  let r := rows - 1
  let c := cols - 1
  let tab' := youngSet tab cols r c key
  youngBubbleUp tab' cols r c


def youngSearch (tab : Array Nat) (key : Nat) (rows cols : Nat) : Bool :=
  Id.run do
    if cols == 0 || rows == 0 then return false
    let mut r := 0
    let mut c := cols - 1
    while r < rows && c < cols do
      let val := youngGet tab cols r c
      if val == key then return true
      else if val > key then
        if c == 0 then return false
        c := c - 1
      else
        r := r + 1
    return false

/-!
## Verification Helpers
-/


def isMaxHeap (arr : Array Nat) (heapSize : Nat) : Bool :=
  Id.run do
    for i in List.range heapSize do
      let l := left i
      let r := right i
      if l < heapSize && l < arr.size && arr[l]! > arr[i]! then return false
      if r < heapSize && r < arr.size && arr[r]! > arr[i]! then return false
    return true


def isDaryMaxHeap (arr : Array Nat) (heapSize d : Nat) : Bool :=
  Id.run do
    for i in List.range heapSize do
      for j in List.range d do
        let c := dAryChild i j d
        if c < heapSize && c < arr.size && arr[c]! > arr[i]! then return false
    return true


def isYoungTableau (tab : Array Nat) (rows cols : Nat) : Bool :=
  Id.run do
    for r in List.range rows do
      for c in List.range cols do
        if c + 1 < cols then
          if youngGet tab cols r c > youngGet tab cols r (c + 1) then return false
        if r + 1 < rows then
          if youngGet tab cols r c > youngGet tab cols (r + 1) c then return false
    return true



/-!
# Tests
-/

/-- buildMaxHeap produces a valid max-heap. -/
example : isMaxHeap (buildMaxHeap #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7]) 10 = true := by native_decide
#eval isMaxHeap (buildMaxHeap #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7]) 10 -- expected: true

/-- buildMaxHeapPrime produces a valid max-heap. -/
example : isMaxHeap (buildMaxHeapPrime #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7]) 10 = true := by native_decide
#eval isMaxHeap (buildMaxHeapPrime #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7]) 10 -- expected: true

/-- Problem 6-1(a): buildMaxHeap and buildMaxHeapPrime can produce different heaps. -/
example : buildMaxHeap #[1, 2, 3, 4, 5, 6] ≠ buildMaxHeapPrime #[1, 2, 3, 4, 5, 6] := by native_decide
#eval (buildMaxHeap #[1, 2, 3, 4, 5, 6], buildMaxHeapPrime #[1, 2, 3, 4, 5, 6])

/-- d-ary parent of root's first child (d=3) is root. -/
example : dAryParent 1 3 = 0 := by native_decide
#eval dAryParent 1 3 -- expected: 0

/-- d-ary child index function (d=3). -/
example : dAryChild 0 0 3 = 1 := by native_decide
example : dAryChild 0 1 3 = 2 := by native_decide
example : dAryChild 0 2 3 = 3 := by native_decide
#eval dAryChild 0 0 3 -- expected: 1
#eval dAryChild 0 1 3 -- expected: 2
#eval dAryChild 0 2 3 -- expected: 3

/-- Build d-ary max-heap (d=3) produces valid heap. -/
example : isDaryMaxHeap (buildDAryMaxHeap #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7] 3) 10 3 = true := by native_decide
#eval isDaryMaxHeap (buildDAryMaxHeap #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7] 3) 10 3 -- expected: true

/-- d-ary extract max returns the maximum element. -/
example : (dAryExtractMax (buildDAryMaxHeap #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7] 3) 10 3).1 = 16 := by native_decide
#eval (dAryExtractMax (buildDAryMaxHeap #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7] 3) 10 3).1 -- expected: 16

/-- Young tableau: isYoungTableau check on valid tableau. -/
example : isYoungTableau #[1, 3, 5, 2, 4, 6] 2 3 = true := by native_decide
#eval isYoungTableau #[1, 3, 5, 2, 4, 6] 2 3 -- expected: true

/-- Young search finds element present. -/
example : youngSearch #[1, 3, 5, 2, 4, 6] 4 2 3 = true := by native_decide
#eval youngSearch #[1, 3, 5, 2, 4, 6] 4 2 3 -- expected: true

/-- Young search returns false for absent element. -/
example : youngSearch #[1, 3, 5, 2, 4, 6] 7 2 3 = false := by native_decide
#eval youngSearch #[1, 3, 5, 2, 4, 6] 7 2 3 -- expected: false

/-!
# Tests: Edge Cases
-/

/-- Empty array: buildMaxHeap. -/
example : buildMaxHeap #[] = #[] := by native_decide
#eval buildMaxHeap #[] -- expected: #[]

/-- Single element: buildMaxHeap. -/
example : isMaxHeap (buildMaxHeap #[42]) 1 = true := by native_decide
#eval isMaxHeap (buildMaxHeap #[42]) 1 -- expected: true

/-- Single element: buildMaxHeapPrime. -/
example : isMaxHeap (buildMaxHeapPrime #[42]) 1 = true := by native_decide
#eval isMaxHeap (buildMaxHeapPrime #[42]) 1 -- expected: true

/-- Empty array: buildMaxHeapPrime. -/
example : buildMaxHeapPrime #[] = #[] := by native_decide
#eval buildMaxHeapPrime #[] -- expected: #[]

/-- d-ary heap with d=1 (unary, i.e., sorted descending). -/
example : isDaryMaxHeap (buildDAryMaxHeap #[3, 1, 2] 1) 3 1 = true := by native_decide
#eval isDaryMaxHeap (buildDAryMaxHeap #[3, 1, 2] 1) 3 1 -- expected: true

/-- d-ary extract max from single element heap. -/
example : (dAryExtractMax #[5] 1 3).1 = 5 := by native_decide
#eval (dAryExtractMax #[5] 1 3).1 -- expected: 5

/-- d-ary extract max from empty heap returns 0. -/
example : (dAryExtractMax #[] 0 3).1 = 0 := by native_decide
#eval (dAryExtractMax #[] 0 3).1 -- expected: 0

/-- Young extract min from a 2x2 tableau. -/
example : (youngExtractMin #[1, 3, 2, 4] 2 2).1 = 1 := by native_decide
#eval (youngExtractMin #[1, 3, 2, 4] 2 2).1 -- expected: 1

/-- Young extract min leaves a valid tableau. -/
example : isYoungTableau (youngExtractMin #[1, 3, 2, 4] 2 2).2 2 2 = true := by native_decide
#eval isYoungTableau (youngExtractMin #[1, 3, 2, 4] 2 2).2 2 2 -- expected: true

/-- Young search on 1x1 tableau finds element. -/
example : youngSearch #[5] 5 1 1 = true := by native_decide
#eval youngSearch #[5] 5 1 1 -- expected: true

/-- Young search on 1x1 tableau: not found. -/
example : youngSearch #[5] 3 1 1 = false := by native_decide
#eval youngSearch #[5] 3 1 1 -- expected: false

/-- Young extract min from 2x3 tableau. -/
example : (youngExtractMin #[1, 3, 5, 2, 4, 6] 2 3).1 = 1 := by native_decide
#eval (youngExtractMin #[1, 3, 5, 2, 4, 6] 2 3).1 -- expected: 1

/-- Young extract min from 2x3 preserves tableau. -/
example : isYoungTableau (youngExtractMin #[1, 3, 5, 2, 4, 6] 2 3).2 2 3 = true := by native_decide
#eval isYoungTableau (youngExtractMin #[1, 3, 5, 2, 4, 6] 2 3).2 2 3 -- expected: true

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: buildMaxHeap on CLRS example. -/
example : isMaxHeap (buildMaxHeap #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7]) 10 = true := by native_decide

/-- positive: buildMaxHeapPrime on CLRS example. -/
example : isMaxHeap (buildMaxHeapPrime #[4, 1, 3, 2, 16, 9, 10, 14, 8, 7]) 10 = true := by native_decide

/-- positive: d-ary insert then extract max gives the inserted value when it is max. -/
example :
  let heap := buildDAryMaxHeap #[1, 2, 3] 3
  let (heap', sz') := dAryInsert heap 100 3 3
  (dAryExtractMax heap' sz' 3).1 = 100 := by native_decide

/-- positive: Young tableau sort via repeated extract-min gives sorted order. -/
example :
  let t0 := #[1, 3, 2, 4]
  let (v1, t1) := youngExtractMin t0 2 2
  let (v2, _) := youngExtractMin t1 2 2
  v1 ≤ v2 := by native_decide

/-- negative: buildMaxHeap and buildMaxHeapPrime are not always equal. -/
example : ¬ (buildMaxHeap #[1, 2, 3, 4, 5, 6] = buildMaxHeapPrime #[1, 2, 3, 4, 5, 6]) := by native_decide

/-- negative: non-heap array is not a valid max-heap. -/
example : isMaxHeap #[1, 10, 3] 3 = false := by native_decide

/-- negative: Young search for absent element in 3x3 tableau. -/
example : youngSearch #[1, 2, 4, 3, 5, 7, 6, 8, 9] 10 3 3 = false := by native_decide

/-!
# Tests: Properties
-/

/-- Build and check: various sizes produce valid heaps (binary). -/
example : isMaxHeap (buildMaxHeap #[5, 3, 8, 1]) 4 = true := by native_decide
example : isMaxHeap (buildMaxHeap #[10, 20, 30, 40, 50]) 5 = true := by native_decide
example : isMaxHeap (buildMaxHeapPrime #[5, 3, 8, 1]) 4 = true := by native_decide
example : isMaxHeap (buildMaxHeapPrime #[10, 20, 30, 40, 50]) 5 = true := by native_decide

/-- d-ary parent-child relationship: parent of child is original node. -/
example : dAryParent (dAryChild 2 1 4) 4 = 2 := by native_decide
example : dAryParent (dAryChild 0 0 3) 3 = 0 := by native_decide

/-- Young tableau insert into all-sentinel tableau gives valid result. -/
example :
  let tab := #[sentinel, sentinel, sentinel, sentinel]
  let tab' := youngInsert tab 5 2 2
  isYoungTableau tab' 2 2 = true := by native_decide

/-- Young search finds elements in a valid 3x3 tableau. -/
example : youngSearch #[1, 2, 4, 3, 5, 7, 6, 8, 9] 5 3 3 = true := by native_decide
example : youngSearch #[1, 2, 4, 3, 5, 7, 6, 8, 9] 1 3 3 = true := by native_decide
example : youngSearch #[1, 2, 4, 3, 5, 7, 6, 8, 9] 9 3 3 = true := by native_decide



end HeapsortProblems
