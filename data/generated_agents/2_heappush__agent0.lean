```lean
import Mathlib.Data.List.Basic
import Mathlib.Tactic.LibrarySearch

namespace VeriBench

/- 
  A heap is a list satisfying the min-heap property: 
  for every element at position i, the element at position (i-1)/2 is less than or equal to it
  (except for the root which has no parent).
-/
def IsHeap (heap : List α) [LT α] : Prop := 
  ∀ i, 0 < i → i < heap.length → heap[(i - 1) / 2] ≤ heap[i]

/- Implementation of _siftdown helper function -/
def _siftdown [Ord α] (heap : List α) (startpos : Nat) (pos : Nat) : List α :=
  if h : pos < heap.length then
    let newitem := heap.get ⟨pos, h⟩
    let rec loop (heap : List α) (pos : Nat) : List α :=
      if pos > startpos then
        let parentpos := (pos - 1) / 2
        if h' : parentpos < heap.length then
          let parent := heap.get ⟨parentpos, h'⟩
          if newitem < parent then
            let heap' := heap.set ⟨pos, by
              have : pos < heap.length := by
                apply List.getElem_pos_lt_length heap pos
            ⟩ parent
            loop heap' parentpos
          else
            heap.set ⟨pos, by
              apply List.getElem_pos_lt_length heap pos
            ⟩ newitem
        else
          heap.set ⟨pos, by
            apply List.getElem_pos_lt_length heap pos
          ⟩ newitem
      else
        heap.set ⟨pos, by
          apply List.getElem_pos_lt_length heap pos
        ⟩ newitem
    loop heap pos
  else
    heap

/- Implementation of heappush function -/
def heappush [Ord α] (heap : List α) (item : α) : List α :=
  let heap' := heap.append [item]
  _siftdown heap' 0 (heap'.length - 1)

/- Specification: heappush maintains the heap invariant -/
theorem heappush_preserves_heap [Ord α] (heap : List α) (item : α) :
  IsHeap heap → IsHeap (heappush heap item) :=
sorry

/- Specification: heappush adds exactly one element -/
theorem heappush_length [Ord α] (heap : List α) (item : α) :
  (heappush heap item).length = heap.length + 1 :=
sorry

/- Specification: the minimum element is at the root after heappush -/
theorem heappush_min [Ord α] (heap : List α) (item : α) :
  IsHeap heap → heap.length > 0 → 
  (heappush heap item).get ⟨0, by simp [heappush_length]⟩ ≤ item :=
sorry

/- Test cases for heappush -/
def test_heappush : Bool :=
  -- Basic test
  let h1 := heappush [] 3
  let h2 := heappush h1 1
  let h3 := heappush h2 2
  
  -- Check results
  h1 == [3] &&
  h2 == [1, 3] &&
  h3 == [1, 3, 2] &&
  
  -- Edge cases
  let h4 := heappush [] 5
  let h5 := heappush h4 5
  h4 == [5] &&
  h5 == [5, 5]

#eval test_heappush

end VeriBench
```
