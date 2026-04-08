```lean
/--
  Implementation of heappush, which pushes an item onto a heap and maintains the heap invariant.
  The heap is represented as a list where for each node at index i:
  - Its left child is at index 2i + 1
  - Its right child is at index 2i + 2
  - Its parent is at index (i - 1) / 2 (integer division)
  The heap property ensures that for each node, its value is less than or equal to its children's values.
-/

def siftdown (heap : List α) (startpos : Nat) (pos : Nat) [Ord α] : List α :=
  if pos ≤ startpos then heap
  else
    let newitem := heap[pos]!
    let rec loop (heap : List α) (pos : Nat) : List α :=
      if pos > startpos then
        let parentpos := (pos - 1) >>> 1
        let parent := heap[parentpos]!
        if newitem < parent then
          let heap := heap.set! pos parent
          loop heap parentpos
        else
          heap.set! pos newitem
      else
        heap.set! pos newitem
    loop heap pos

def heappush (heap : List α) (item : α) [Ord α] : List α :=
  let heap := heap ++ [item]
  siftdown heap 0 (heap.length - 1)

/--
  Check if a list satisfies the heap invariant: for each node, its value is less than or equal to its children's values.
-/
def isHeap (heap : List α) [Ord α] : Bool :=
  let rec checkPos (pos : Nat) : Bool :=
    if pos ≥ heap.length then
      true
    else
      let leftChild := 2 * pos + 1
      let rightChild := 2 * pos + 2
      let leftValid := leftChild >= heap.length || heap[pos]! ≤ heap[leftChild]!
      let rightValid := rightChild >= heap.length || heap[pos]! ≤ heap[rightChild]!
      leftValid && rightValid && checkPos (pos + 1)
  checkPos 0

/--
  Predicate that states a list is a valid heap.
-/
def IsHeap (heap : List α) [Ord α] : Prop :=
  ∀ (pos : Nat), pos < heap.length → 
    let leftChild := 2 * pos + 1
    let rightChild := 2 * pos + 2
    (leftChild < heap.length → heap[pos]! ≤ heap[leftChild]!) ∧
    (rightChild < heap.length → heap[pos]! ≤ heap[rightChild]!)

/--
  Predicate that states a list is a permutation of another list.
-/
def IsPermutation (l1 l2 : List α) [BEq α] : Prop :=
  ∀ (x : α), l1.count x = l2.count x

theorem heappush_preserves_heap {heap : List α} {item : α} [Ord α] :
  IsHeap heap → IsHeap (heappush heap item) :=
  sorry

theorem heappush_is_permutation {heap : List α} {item : α} [Ord α] [BEq α] :
  IsPermutation (heappush heap item) (heap ++ [item]) :=
  sorry

theorem heappush_root_is_min {heap : List α} {item : α} [Ord α] :
  IsHeap heap → heap.length > 0 → 
  let newHeap := heappush heap item
  newHeap[0]! = min item (heap[0]!) :=
  sorry

/--
  Test cases for heappush
-/
def testHeappush : IO Unit := do
  -- Basic test
  let mut h : List Int := []
  let h := heappush h 3
  assert! (isHeap h)
  let h := heappush h 1
  assert! (isHeap h)
  let h := heappush h 2
  assert! (isHeap h)
  assert! (h[0]! = 1)

  -- Edge cases
  let mut h : List Int := []
  let h := heappush h 5
  assert! (isHeap h)
  let h := heappush h 5
  assert! (isHeap h)
  assert! (h[0]! = 5)

  IO.println "All tests passed!"

#eval testHeappush
```
