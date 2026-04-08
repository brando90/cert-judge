import Mathlib.Data.List.Basic
import Mathlib.Data.List.Indexes
import Mathlib.Tactic

namespace VeriBench

/-!
# Heap operations (heappop)

This module implements the heap operations from Python's `heapq` module.
-/

/-- Implementation of the `_siftdown` function from Python's `heapq` module. -/
def _siftdown (heap : List α) (startpos : Nat) (pos : Nat) [LT α] : List α :=
  if h : pos < heap.length then
    let newitem := heap[pos]
    let rec loop (heap : List α) (pos : Nat) : List α :=
      if pos > startpos then
        let parentpos := (pos - 1) >>> 1
        if h' : parentpos < heap.length then
          let parent := heap[parentpos]
          if newitem < parent then
            let heap := heap.set pos parent
            loop heap parentpos
          else
            heap.set pos newitem
        else
          heap.set pos newitem
      else
        heap.set pos newitem
    loop heap pos
  else
    heap

/-- Implementation of the `_siftup` function from Python's `heapq` module. -/
def _siftup (heap : List α) (pos : Nat) [LT α] : List α :=
  if h : pos < heap.length then
    let endpos := heap.length
    let startpos := pos
    let newitem := heap[pos]
    
    let rec bubbleUp (heap : List α) (pos : Nat) : List α × Nat :=
      let childpos := 2 * pos + 1
      if childpos < endpos then
        let rightpos := childpos + 1
        let childpos :=
          if rightpos < endpos ∧ ¬(heap[childpos] < heap[rightpos]) then
            rightpos
          else
            childpos
        let heap := heap.set pos heap[childpos]
        bubbleUp heap childpos
      else
        (heap, pos)
    
    let (heap, finalPos) := bubbleUp heap pos
    let heap := heap.set finalPos newitem
    _siftdown heap startpos finalPos
  else
    heap

/-- 
Pop the smallest item off the heap, maintaining the heap invariant.
Returns the popped item and the updated heap.
-/
def heappop (heap : List α) [LT α] : Option (α × List α) :=
  match heap with
  | [] => none
  | [x] => some (x, [])
  | x::xs =>
    let lastelt := heap.getLast (by simp)
    let returnitem := heap.head!
    let heap := xs.set 0 lastelt
    let heap := _siftup heap 0
    some (returnitem, heap)

/--
A heap is a list that satisfies the heap property:
for every position i > 0, the parent at position (i-1)/2 is less than or equal to the element at position i.
-/
def IsHeap (heap : List α) [LT α] : Prop :=
  ∀ i, i > 0 → i < heap.length → ¬(heap[(i-1)/2] < heap[i]) → heap[(i-1)/2] = heap[i]

/--
The `_siftdown` operation maintains the heap property.
-/
theorem _siftdown_preserves_heap (heap : List α) (startpos pos : Nat) [LT α] [DecidableRel (· < · : α → α → Prop)]
    (h_heap : IsHeap heap) (h_valid : pos < heap.length) :
    IsHeap (_siftdown heap startpos pos) := by
  sorry

/--
The `_siftup` operation maintains the heap property.
-/
theorem _siftup_preserves_heap (heap : List α) (pos : Nat) [LT α] [DecidableRel (· < · : α → α → Prop)]
    (h_heap : IsHeap heap) (h_valid : pos < heap.length) :
    IsHeap (_siftup heap pos) := by
  sorry

/--
`heappop` returns the smallest element in the heap and maintains the heap property.
-/
theorem heappop_correct (heap : List α) [LT α] [DecidableRel (· < · : α → α → Prop)]
    (h_heap : IsHeap heap) (h_nonempty : heap ≠ []) :
    let result := heappop heap
    result.isSome ∧
    let (popped, newHeap) := result.get
    (∀ x ∈ newHeap, popped ≤ x) ∧
    IsHeap newHeap := by
  sorry

/-- Test cases for the `heappop` function. -/
def test_heappop : IO Unit := do
  -- Basic test
  let h := [1, 3, 2]
  match heappop h with
  | some (popped, newHeap) => 
    IO.println s!"Popped: {popped}, New heap: {newHeap}"
    if popped ≠ 1 then
      throw (IO.userError "Expected popped value to be 1")
  | none => 
    throw (IO.userError "Expected some result but got none")

  -- Single element heap
  let h := [5]
  match heappop h with
  | some (popped, newHeap) => 
    IO.println s!"Popped from single-element heap: {popped}, New heap: {newHeap}"
    if popped ≠ 5 || newHeap ≠ [] then
      throw (IO.userError "Expected popped value to be 5 and empty heap")
  | none => 
    throw (IO.userError "Expected some result but got none")

  -- Empty heap
  let h : List Nat := []
  if (heappop h).isSome then
    throw (IO.userError "Expected none result for empty heap but got some")

  IO.println "All tests passed!"

end VeriBench
