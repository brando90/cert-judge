/-!
# VeriBench – Heappush (min-heap)

File order:

1. Implementation (`_siftdown`, `heappush`)
2. Unit tests (basic, edge, small property checks)
3. Pre-condition
4. Property propositions
5. Post-condition (same order as properties)
6. Correctness theorem `Pre → Post`

All nontrivial proofs are left as `sorry` for the learner/model/agent.
-/

namespace HeapPush

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
`heappush`

Push `item` onto `heap` (append) and restore heap invariant via `_siftdown`.
-/
def heappush (heap : Array Int) (item : Int) : Array Int :=
  let heap1 := heap.push item
  _siftdown heap1 0 (heap1.size - 1)


/-!
# Tests
-/

/-- Boolean heap invariant checker: for every child, parent ≤ child. -/
def checkInvariant (h : Array Int) : Bool :=
  let n := h.size
  let rec go (i : Nat) : Bool :=
    if i ≥ n then
      true
    else if i = 0 then
      go (i + 1)
    else
      let parentpos := (i - 1) >>> 1
      if h[parentpos]! ≤ h[i]! then
        go (i + 1)
      else
        false
  go 0

/-- expected: root becomes 1 after pushing 3,1,2 -/
example : (heappush (heappush (heappush (#[] : Array Int) 3) 1) 2)[0]! = 1 := by native_decide
#eval (heappush (heappush (heappush (#[] : Array Int) 3) 1) 2)[0]!  -- expected: 1

/-- expected: pushing 5 twice keeps root 5 -/
example :
  let h1 := heappush (#[] : Array Int) 5
  let h2 := heappush h1 5
  h1[0]! = 5 ∧ h2[0]! = 5 := by native_decide
#eval (let h1 := heappush (#[] : Array Int) 5; let h2 := heappush h1 5; (h1[0]!, h2[0]!))  -- expected: (5, 5)

/-- positive: invariant holds after each push in [3,1,2] -/
example :
  let h1 := heappush (#[] : Array Int) 3
  let h2 := heappush h1 1
  let h3 := heappush h2 2
  checkInvariant h1 ∧ checkInvariant h2 ∧ checkInvariant h3 := by native_decide
#eval (let h1 := heappush (#[] : Array Int) 3; let h2 := heappush h1 1; let h3 := heappush h2 2; (checkInvariant h1, checkInvariant h2, checkInvariant h3))  -- expected: (true, true, true)


/-!
# Pre-Condition
-/

/-- **Pre-condition.** The input `heap` already satisfies the min-heap invariant. -/
def Pre (heap : Array Int) : Prop :=
  checkInvariant heap = true

/-!
# Property Theorems
-/

/-- **Invariant property**: after `heappush`, the heap invariant holds. -/
def prop_invariant (heap : Array Int) (item : Int) : Prop :=
  checkInvariant (heappush heap item) = true

/-- **Invariant theorem**: `heappush` preserves the heap invariant (given a heap input). -/
@[simp] theorem invariant_thm (heap : Array Int) (item : Int) (hPre : Pre heap) :
  prop_invariant heap item := by
  sorry

/-- **Size property**: pushing increases the size by one. -/
def prop_size (heap : Array Int) (item : Int) : Prop :=
  (heappush heap item).size = heap.size + 1

/-- **Size theorem**: `heappush` increases the size by one. -/
@[simp] theorem size_thm (heap : Array Int) (item : Int) :
  prop_size heap item := by
  sorry

/-- **Multiset property**: contents are preserved up to permutation. -/
def prop_multiset (heap : Array Int) (item : Int) : Prop :=
  List.Perm (heappush heap item).toList (item :: heap.toList)

/-- **Multiset theorem**: `heappush` preserves contents up to permutation. -/
@[simp] theorem multiset_thm (heap : Array Int) (item : Int) :
  prop_multiset heap item := by
  sorry

/-!
# Post-Condition
-/

/-- **Post-condition** for `heappush`. -/
def Post_prop (heap : Array Int) (item : Int) : Prop :=
  prop_invariant heap item ∧
  prop_size heap item ∧
  prop_multiset heap item

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre-condition implies the post-condition. -/
theorem correctness_thm (heap : Array Int) (item : Int) (hPre : Pre heap) :
  Post_prop heap item := by
  exact And.intro
    (invariant_thm heap item hPre)
    (And.intro (size_thm heap item) (multiset_thm heap item))

end HeapPush
