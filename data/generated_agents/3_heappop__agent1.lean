```lean
import VeriBench.Prelude

def isHeap (heap : List α) [LT α] : Bool :=
  let rec check (i : Nat) : Bool :=
    if h : i < heap.length then
      let leftChild := 2 * i + 1
      let rightChild := 2 * i + 2
      let leftOk := if leftChild < heap.length then
                     heap[i]! ≤ heap[leftChild]!
                   else true
      let rightOk := if rightChild < heap.length then
                      heap[i]! ≤ heap[rightChild]!
                    else true
      leftOk && rightOk && check (i + 1)
    else
      true
  check 0

def _siftdown [LT α] [DecidableRel (α := α) (· < ·)] (heap : List α) (startpos : Nat) (pos : Nat) : List α :=
  if pos ≥ heap.length then heap else
  let newitem := heap[pos]!
  let rec loop (heap : List α) (pos : Nat) : List α :=
    if pos > startpos then
      let parentpos := (pos - 1) >>> 1
      let parent := heap[parentpos]!
      if newitem < parent then
        let heap := heap.set pos parent
        loop heap parentpos
      else
        heap.set pos newitem
    else
      heap.set pos newitem
  loop heap pos

def _siftup [LT α] [DecidableRel (α := α) (· < ·)] (heap : List α) (pos : Nat) : List α :=
  if pos ≥ heap.length then heap else
  let endpos := heap.length
  let startpos := pos
  let newitem := heap[pos]!
  let rec loop (heap : List α) (pos : Nat) (childpos : Nat) : List α :=
    if childpos < endpos then
      let rightpos := childpos + 1
      let childpos := if rightpos < endpos && !(heap[childpos]! < heap[rightpos]!) then
                       rightpos
                     else
                       childpos
      let heap := heap.set pos heap[childpos]!
      let pos := childpos
      let childpos := 2 * pos + 1
      loop heap pos childpos
    else
      let heap := heap.set pos newitem
      _siftdown heap startpos pos
  loop heap pos (2 * pos + 1)

/--
  Pop the smallest item off the heap, maintaining the heap invariant.
-/
def heappop [LT α] [DecidableRel (α := α) (· < ·)] (heap : List α) : α × List α :=
  if heap.isEmpty then
    panic! "heappop: empty heap"
  else if heap.length == 1 then
    (heap[0]!, [])
  else
    let lastelt := heap[heap.length - 1]!
    let returnitem := heap[0]!
    let heap := heap.dropLast
    let heap := heap.set 0 lastelt
    let heap := _siftup heap 0
    (returnitem, heap)

-- Tests
def _check_invariant [LT α] [DecidableRel (α := α) (· < ·)] (heap : List α) : Bool :=
  isHeap heap

def test_heappop : IO Bool := do
  -- Basic unit tests
  let mut h := [3, 1, 2]
  h := h.sort -- simulate heapify
  if !_check_invariant h then
    return false
  let (popped, h) := heappop h
  if !_check_invariant h then
    return false
  if popped != 1 then
    return false

  -- Edge unit test: pop single-element heap
  let mut h := [5]
  let (popped, h) := heappop h
  if popped != 5 || !h.isEmpty then
    return false

  -- Error behavior: should panic on empty heap
  try
    let _ := heappop ([] : List Nat)
    return false
  catch _ =>
    pure ()

  return true

-- Specification
def isHeapProperty [LT α] (heap : List α) : Prop :=
  ∀ i j, i < heap.length → j < heap.length → 2 * i + 1 = j ∨ 2 * i + 2 = j → heap[i]! ≤ heap[j]!

theorem heappop_spec [LT α] [DecidableRel (α := α) (· < ·)] [DecidableRel (α := α) (· ≤ ·)]
  (heap : List α) (h : heap.length > 0) (h_heap : isHeapProperty heap) :
  let (min, heap') := heappop heap
  (∀ i, i < heap.length → min ≤ heap[i]!) ∧ 
  (heap'.length = heap.length - 1) ∧
  (isHeapProperty heap') := by
  sorry
```
