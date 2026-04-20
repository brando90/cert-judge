import Mathlib

namespace HeapStructure

/-!
# Implementation
-/

/--
**PARENT(i)** (CLRS p. 152, adapted to 0-based indexing)

Returns the index of the parent of node `i`.
For the root (i = 0), returns 0.

## Examples

/-!
# VeriBench – Heap Structure (CLRS Chapter 6, Section 6.1)

File order:

1. Implementation
2. Tests (positive/negative, edge cases, property based tests)
3. Pre‑condition prop
4. Exhaustive property prop and their theorems
5. Post‑condition prop (same order as property props)
6. Correctness theorem `Pre → Post`
7. Imperative i. implementation, ii. tests, and iii. equivalence theorem.

Formalizes CLRS 3rd Ed. Section 6.1: Heaps.
A binary (max/min) heap is an array-based, nearly complete binary tree.

**Index convention**: CLRS uses 1-based indexing. This formalization uses
0-based indexing to match Lean 4 arrays:
- parent(i) = (i - 1) / 2
- left(i) = 2 * i + 1
- right(i) = 2 * i + 2

Covers exercises 6.1-1 through 6.1-7.

# Implementation

## Heap Index Functions & Predicates

Defines parent/left/right index computation, max-heap and min-heap predicates,
heap height, and leaf detection.
-/


/-!
# Pre‑Condition
-/

/-- **Pre‑condition**: the array is non-empty and heapSize is valid. -/
def Pre (a : Array Nat) (heapSize : Nat) : Prop :=
  heapSize ≤ a.size

/-!
# Property Theorems
-/

/-- **Max-heap parent-geq property** (CLRS max-heap property):
    For a max-heap, for every node i > 0 within heapSize,
    a[parent(i)] >= a[i]. -/
def max_heap_parent_geq_prop (a : Array Nat) (heapSize : Nat) : Prop :=
  isMaxHeap a heapSize = true →
    ∀ i, 1 ≤ i → i < heapSize → i < a.size →
      a[parent i]! ≥ a[i]!

/-- **Max-heap parent-geq theorem**. -/
def height_bound_prop (n : Nat) : Prop :=
  n > 0 → heapHeight n = Nat.log 2 n

/-- **Height bound theorem**. -/
def leaf_index_range_prop (n : Nat) : Prop :=
  ∀ i, i < n → (isLeaf i n = true ↔ i ≥ n / 2)

/-- **Leaf index range theorem**. -/
def root_is_max_prop (a : Array Nat) (heapSize : Nat) : Prop :=
  isMaxHeap a heapSize = true → heapSize > 0 → heapSize ≤ a.size →
    ∀ i, i < heapSize → a[0]! ≥ a[i]!

/-- **Root is max theorem**. -/
def sorted_is_min_heap_prop (a : Array Nat) : Prop :=
  (∀ i j, i < j → j < a.size → a[i]! ≤ a[j]!) →
    isMinHeap a a.size = true

/-- **Sorted is min-heap theorem**. -/
def parent_left_inverse_prop (i : Nat) : Prop :=
  parent (left i) = i

/-- **Parent-left inverse theorem**. -/
def parent_right_inverse_prop (i : Nat) : Prop :=
  parent (right i) = i

/-- **Parent-right inverse theorem**. -/
def left_lt_right_prop (i : Nat) : Prop :=
  left i < right i

/-- **Left less than right theorem**. -/
def smallest_at_leaf_prop (a : Array Nat) (heapSize : Nat) : Prop :=
  isMaxHeap a heapSize = true → heapSize > 0 → heapSize ≤ a.size →
    ∃ j, j < heapSize ∧ isLeaf j heapSize = true ∧
      ∀ k, k < heapSize → a[j]! ≤ a[k]!

/-- **Smallest at leaf theorem**. -/

/-!
# Post‑Condition (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for heap structure. -/
def Post_prop (a : Array Nat) (heapSize : Nat) : Prop :=
  (max_heap_parent_geq_prop a heapSize) ∧
  (height_bound_prop heapSize) ∧
  (leaf_index_range_prop heapSize) ∧
  (root_is_max_prop a heapSize) ∧
  (sorted_is_min_heap_prop a) ∧
  (∀ i, parent_left_inverse_prop i) ∧
  (∀ i, parent_right_inverse_prop i) ∧
  (∀ i, left_lt_right_prop i) ∧
  (smallest_at_leaf_prop a heapSize)


end HeapStructure