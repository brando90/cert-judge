```lean
import Mathlib.Data.List.Basic

/-- A heap is a list that satisfies the min-heap property: for every node, its value is <= each child's value. -/
def IsHeap {α : Type} [LT α] (l : List α) : Prop :=
  ∀ i : Nat, i < l.length →
    let left := 2 * i + 1
    let right := 2 * i + 2
    (left < l.length → l[i]! ≤ l[left]!) ∧
    (right < l.length → l[i]! ≤ l[right]!)
where
  -- Define ≤ in terms of < for any type with LT
  le (a b : α) := ¬ (b < a)

/-- Sift down operation for a heap. Moves an element down until it satisfies the heap property. -/
def siftdown {α : Type} [LT α] (heap : List α) (startpos pos : Nat) : List α :=
  if h : pos < heap.length then
    let newitem := heap[pos]!
    let rec loop (heap : List α) (pos : Nat) : List α :=
      if pos > startpos then
        let parentpos := (pos - 1) >>> 1
        if h' : parentpos < heap.length then
          let parent := heap[parentpos]!
          if newitem < parent then
            let heap' := heap.set pos parent
            loop heap' parentpos
          else
            heap.set pos newitem
        else
          heap.set pos newitem
      else
        heap.set pos newitem
    loop heap pos
  else
    heap

/-- Sift up operation for a heap. Moves an element up from a position to maintain the heap property. -/
def siftup {α : Type} [LT α] (heap : List α) (pos : Nat) : List α :=
  if h : pos < heap.length then
    let endpos := heap.length
    let startpos := pos
    let newitem := heap[pos]!
    
    let rec bubble (heap : List α) (pos : Nat) : (List α × Nat) :=
      let childpos := 2 * pos + 1
      if childpos < endpos then
        let rightpos := childpos + 1
        let childpos' := 
          if rightpos < endpos ∧ ¬(heap[childpos]! < heap[rightpos]!) then
            rightpos
          else
            childpos
        let heap' := heap.set pos heap[childpos']!
        bubble heap' childpos'
      else
        (heap, pos)
    
    let (heap', finalpos) := bubble heap pos
    siftdown heap'.set finalpos newitem startpos finalpos
  else
    heap

/-- Pop the smallest item off the heap, maintaining the heap invariant. -/
def heappop {α : Type} [LT α] (heap : List α) : (α × List α) :=
  if h : heap.length = 0 then
    panic! "Cannot pop from an empty heap"
  else if h' : heap.length = 1 then
    (heap[0]!, [])
  else
    let lastelt := heap[heap.length - 1]!
    let returnitem := heap[0]!
    let heap' := heap.dropLast
    let heap'' := heap'.set 0 lastelt
    (returnitem, siftup heap'' 0)

/-- Specification: heappop removes and returns the smallest element from a heap
    while maintaining the heap property. -/
def heappop_spec {α : Type} [LT α] [DecidableRel (· < · : α → α → Prop)] 
    (heap : List α) (result : α × List α) : Prop :=
  let (min, heap') := result
  heap.length > 0 ∧
  min = heap.minimum? (by cases heap.length; contradiction; simp) ∧
  heap'.length = heap.length - 1 ∧
  IsHeap heap' ∧
  ∀ x ∈ heap', x ∈ heap ∧
  ∀ x ∈ heap, x = min ∨ x ∈ heap'

/-- Test cases for heappop -/
def heappop_test : IO Unit := do
  -- Basic test
  let h := [1, 3, 2]
  let (popped, h') := heappop h
  assert! popped = 1
  assert! IsHeap h'
  
  -- Edge case: single element heap
  let h := [5]
  let (popped, h') := heappop h
  assert! popped = 5
  assert! h' = []
  
  -- Error case: empty heap
  try
    let _ := heappop ([] : List Nat)
    IO.println "Failed: should have raised error"
  catch _ =>
    pure ()

/-- Correctness theorem: heappop satisfies its specification -/
theorem heappop_correct {α : Type} [LT α] [DecidableRel (· < · : α → α → Prop)]
    (heap : List α) (h : IsHeap heap) (h' : heap.length > 0) :
    heappop_spec heap (heappop heap) := by
  sorry
```
