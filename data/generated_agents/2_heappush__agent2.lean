```lean
import Mathlib.Data.List.Basic
import Mathlib.Tactic.LibrarySearch
import Mathlib.Data.Nat.Basic
import Mathlib.Data.Real.Basic

namespace VeriBench

/-
  Implementation of heap push operation from Python's heapq module.
  A heap is a list that satisfies the min-heap property: for every node i,
  the value at i is less than or equal to the values at its children 2*i+1 and 2*i+2.
-/

def siftdown {α : Type} [Ord α] (heap : List α) (startpos : Nat) (pos : Nat) : List α :=
  if h : pos < heap.length then
    let newitem := heap.get ⟨pos, h⟩
    let rec loop (heap : List α) (pos : Nat) : List α :=
      if pos > startpos then
        let parentpos := (pos - 1) >>> 1
        if h' : parentpos < heap.length then
          let parent := heap.get ⟨parentpos, h'⟩
          if newitem < parent then
            let heap' := heap.set ⟨pos, by
              have : pos < heap.length := by assumption
              exact this⟩ parent
            loop heap' parentpos
          else
            heap.set ⟨pos, by
              have : pos < heap.length := by assumption
              exact this⟩ newitem
        else
          heap.set ⟨pos, by
            have : pos < heap.length := by assumption
            exact this⟩ newitem
      else
        heap.set ⟨pos, by
          have : pos < heap.length := by assumption
          exact this⟩ newitem
    loop heap pos
  else
    heap

/-- Push an item onto a heap, maintaining the heap invariant. -/
def heappush {α : Type} [Ord α] (heap : List α) (item : α) : List α :=
  let heap' := heap.concat item
  siftdown heap' 0 (heap'.length - 1)

/-- Checks if a list satisfies the min-heap invariant. -/
def isHeap {α : Type} [Ord α] (heap : List α) : Bool :=
  heap.enum.all fun (pos, item) =>
    if pos = 0 then true
    else
      let parentpos := (pos - 1) >>> 1
      if h : parentpos < heap.length then
        let parent := heap.get ⟨parentpos, h⟩
        parent ≤ item
      else
        true

/-- Specification: heappush adds an item to the heap while maintaining the heap invariant. -/
def heappushSpec {α : Type} [Ord α] (heap : List α) (item : α) (result : List α) : Prop :=
  -- The result should be a permutation of the original heap with the item added
  result.perm (item :: heap) ∧
  -- The result should satisfy the heap invariant
  isHeap result = true

/-- Test cases for heappush -/
def heappushTests : List (List Int × Int × List Int) := [
  -- Basic test case
  ([], 3, [3]),
  -- Push multiple items
  ([3], 1, [1, 3]),
  ([1, 3], 2, [1, 3, 2]),
  -- Edge case: push onto empty heap
  ([], 5, [5]),
  -- Push equal elements
  ([5], 5, [5, 5])
]

theorem heappushCorrect {α : Type} [Ord α] (heap : List α) (item : α) :
  heappushSpec heap item (heappush heap item) := by
  sorry

/-- Run tests for heappush -/
def runHeappushTests : Bool :=
  heappushTests.all fun (input, item, expected) =>
    let result := heappush input item
    result = expected && isHeap result

#eval runHeappushTests

end VeriBench
```
