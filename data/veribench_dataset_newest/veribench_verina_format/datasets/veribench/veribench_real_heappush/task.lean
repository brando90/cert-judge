-- !benchmark @start import type=solution
import Mathlib
namespace HeapPush

variable {α : Type} [LT α] [DecidableRel (· < · : α → α → Prop)] [Inhabited α]
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
def checkInvariant [LE α] [DecidableRel (· ≤ · : α → α → Prop)] (h : Array α) : Bool :=
  let n := h.size
  let rec go (i : Nat) : Bool :=
    if i >= n then true
    else if i == 0 then go (i + 1)
    else
      let parentpos := (i - 1) / 2
      if h[parentpos]! <= h[i]! then go (i + 1)
      else false
  go 0
-- !benchmark @end precond_aux

@[reducible, simp]
def heappush_functional_precond [LE α] [DecidableRel (· ≤ · : α → α → Prop)] (heap : Array α) (item : α) : Prop :=
  -- !benchmark @start precond
  checkInvariant heap = true
  -- !benchmark @end precond


-- !benchmark @start code_aux
def siftdown_functional
    (heap : Array α) (startpos pos : Nat)
    (fuel : Nat := pos + 1) : Array α :=
  match fuel with
  | 0 => heap
  | n + 1 =>
    if pos > startpos then
      let parentpos := (pos - 1) / 2
      if parentpos < heap.size ∧ pos < heap.size then
        let newitem := heap[pos]!
        let parent := heap[parentpos]!
        if newitem < parent then
          let h' := heap.set! pos parent
          let h'' := h'.set! parentpos newitem
          siftdown_functional h'' startpos parentpos n
        else
          heap
      else
        heap
    else
      heap
-- !benchmark @end code_aux


def heappush_functional (heap : Array α) (item : α)
    (h_precond : heappush_functional_precond (heap) (item)) : Array α :=
  -- !benchmark @start code
  let heap1 := heap.push item
  siftdown_functional heap1 0 (heap1.size - 1)
  -- !benchmark @end code


-- !benchmark @start postcond_aux
def prop_invariant [LE α] [DecidableRel (· ≤ · : α → α → Prop)]
    (heap : Array α) (item : α) (res : Array α) : Prop :=
  checkInvariant res = true

def prop_size (heap : Array α) (res : Array α) : Prop :=
  res.size = heap.size + 1

def prop_multiset (heap : Array α) (item : α) (res : Array α) : Prop :=
  List.Perm res.toList (item :: heap.toList)
-- !benchmark @end postcond_aux


@[reducible, simp]
def heappush_functional_postcond [LE α] [DecidableRel (· ≤ · : α → α → Prop)]
    (heap : Array α) (item : α) (result : Array α)
    (h_precond : heappush_functional_precond (heap) (item)) : Prop :=
  -- !benchmark @start postcond
  prop_invariant heap item result ∧
    prop_size heap result ∧
    prop_multiset heap item result
  -- !benchmark @end postcond


-- !benchmark @start proof_aux
theorem heappush_invariant_thm [LE α] [DecidableRel (· ≤ · : α → α → Prop)]
    (heap : Array α) (item : α) (h : checkInvariant heap = true) :
    prop_invariant heap item (heappush_functional heap item (by
      -- The precondition is exactly `checkInvariant heap = true`; ignore `item`.
      simpa [heappush_functional_precond] using h)) := by
  sorry
-- !benchmark @end proof_aux


theorem heappush_functional_spec_satisfied [LE α] [DecidableRel (· ≤ · : α → α → Prop)]
    (heap : Array α) (item : α) (h_precond : heappush_functional_precond (heap) (item)) :
    heappush_functional_postcond (heap) (item) (heappush_functional (heap) (item) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof