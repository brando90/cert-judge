/-!
# VeriBench – Heappop (min-heap)

File order:

1. Implementation (`_siftdown`, `_siftup`, `heappop`)
2. Unit tests (basic, edge)
3. Pre-condition
4. Property propositions
5. Post-condition (same order as properties)
6. Correctness theorem `Pre → Post`

All nontrivial proofs are left as `sorry` for the learner/model/agent.
-/

namespace HeapPop

/--
`_siftdown`

Given:
* `heap` : a min-heap at all indices ≥ `startpos` except possibly at `pos`
* `startpos` : root of the sifted subtree (usually `0`)
* `pos` : index of a leaf whose value may violate the heap invariant

Restores the heap invariant by moving parents down until a slot for `newitem`
is found, then writes `newitem` once.
-/
def _siftdown (heap : Array Int) (startpos pos : Nat) : Array Int :=
  let newitem := heap[pos]!
  let rec loop (h : Array Int) (pos : Nat) : Array Int :=
    if pos > startpos then
      let parentpos := (pos - 1) >>> 1
      let parent := h[parentpos]!
      if newitem < parent then
        let h' := h.set! pos parent
        loop h' parentpos
      else
        h.set! pos newitem
    else
      h.set! pos newitem
  loop heap pos

/--
`_siftup`

Bubbles the smaller child up until reaching a leaf, then places `newitem`
and calls `_siftdown` to give it a final resting place.
-/
partial def _siftup (heap : Array Int) (pos : Nat) : Array Int :=
  let endpos := heap.size
  let startpos := pos
  let newitem := heap[pos]!
  -- Bubble down by moving the smaller child up.
  let rec loop (h : Array Int) (pos : Nat) : Array Int :=
    let childpos := (2 * pos) + 1  -- leftmost child
    if childpos < endpos then
      let rightpos := childpos + 1
      -- choose the smaller child
      let childpos' :=
        if rightpos < endpos ∧ ¬ (h[childpos]! < h[rightpos]!) then rightpos else childpos
      -- move smaller child up
      let h' := h.set! pos h[childpos']!
      loop h' childpos'
    else
      -- leaf: put newitem, then sift it down to final place
      let h' := h.set! pos newitem
      _siftdown h' startpos pos
  loop heap pos

/--
`heappop`
Pop the smallest item and maintain the heap invariant.
Returns the popped item and the resulting heap.
-/
def heappop (heap : Array Int) : Int × Array Int :=
  let n := heap.size
  -- indexing will panic if empty (like raising IndexError)
  let lastelt := heap[n - 1]!
  let heap1   := heap.extract 0 (n - 1)   -- remove last element
  if heap1.size > 0 then
    let returnitem := heap1[0]!
    let heap2 := heap1.set! 0 lastelt
    let heap3 := _siftup heap2 0
    (returnitem, heap3)
  else
    (lastelt, heap1)

/-!
# Tests
-/

/-- Boolean heap invariant checker: for every child, parent ≤ child. -/
def checkInvariant (h : Array Int) : Bool :=
  let n := h.size
  let rec go (i : Nat) : Bool :=
    if i ≥ n then true
    else if i = 0 then go (i+1)
    else
      let parent := (i - 1) >>> 1
      if h[parent]! ≤ h[i]! then go (i+1) else false
  go 0

/-- expected: popping from heap [1,3,2] returns 1 and keeps invariant -/
example :
  let r := heappop (#[(1 : Int), 3, 2])
  r.fst = 1 ∧ checkInvariant r.snd
:= by native_decide
#eval (let r := heappop (#[(1 : Int), 3, 2]); (r.fst, checkInvariant r.snd))  -- expected: (1, true)

/-- expected: popping single-element heap returns the element and empty heap -/
example :
  let r := heappop (#[(5 : Int)])
  r.fst = 5 ∧ r.snd.isEmpty
:= by native_decide
#eval (let r := heappop (#[(5 : Int)]); (r.fst, r.snd.isEmpty))  -- expected: (5, true)

/-!
# Pre-Condition
-/

/-- **Pre-condition.** The input `heap` is a non-empty min-heap. -/
def Pre (heap : Array Int) : Prop :=
  checkInvariant heap = true ∧ heap.size > 0

/-!
# Property Theorems
-/

/-- **Invariant property**: result heap after `heappop` is a min-heap. -/
def prop_invariant (heap : Array Int) : Prop :=
  let (_, h') := heappop heap
  checkInvariant h' = true

/-- **Invariant theorem**: `heappop` preserves the heap invariant (for non-empty heap input). -/
@[simp] theorem invariant_thm (heap : Array Int) (hPre : Pre heap) :
  prop_invariant heap := by
  sorry

/-- **Size property**: size decreases by one. -/
def prop_size (heap : Array Int) : Prop :=
  let (_, h') := heappop heap
  h'.size = heap.size - 1

/-- **Size theorem**: `heappop` reduces the size by one. -/
@[simp] theorem size_thm (heap : Array Int) (hPre : Pre heap) :
  prop_size heap := by
  sorry

/-- **Multiset property**: contents are preserved up to permutation with the popped head. -/
def prop_multiset (heap : Array Int) : Prop :=
  let (x, h') := heappop heap
  List.Perm heap.toList (x :: h'.toList)

/-- **Multiset theorem**: `heappop` preserves contents up to permutation. -/
@[simp] theorem multiset_thm (heap : Array Int) (hPre : Pre heap) :
  prop_multiset heap := by
  -- proof left to the learner/agent
  sorry

/-!
# Post-Condition
-/

/-- **Post-condition** for `heappop`. -/
def Post_prop (heap : Array Int) : Prop :=
  prop_invariant heap ∧
  prop_size heap ∧
  prop_multiset heap

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre-condition implies the post-condition. -/
theorem correctness_thm (heap : Array Int) (hPre : Pre heap) :
  Post_prop heap := by
  exact And.intro
    (invariant_thm heap hPre)
    (And.intro (size_thm heap hPre) (multiset_thm heap hPre))

end HeapPop
