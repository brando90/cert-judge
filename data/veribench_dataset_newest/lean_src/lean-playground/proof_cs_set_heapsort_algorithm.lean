import Mathlib

open List
namespace HeapsortAlgorithm

/-!
# Implementation
-/

/-- Parent index in a 0-based max-heap. -/
def parent (i : Nat) : Nat := (i - 1) / 2

/-- Left child index in a 0-based max-heap. -/
def left (i : Nat) : Nat := 2 * i + 1

/-- Right child index in a 0-based max-heap. -/
def right (i : Nat) : Nat := 2 * i + 2

/-- Swap two elements in an array by index (unchecked). -/
def mySwap (arr : Array Nat) (i j : Nat) : Array Nat :=
  let vi := arr[i]!
  let vj := arr[j]!
  (arr.set! i vj).set! j vi

/-- **MAX-HEAPIFY** (CLRS 6.2). Maintains the max-heap property for the
    sub-tree rooted at index `i`, considering only the first `heapSize`
    elements. Uses fuel to guarantee termination. -/
def maxHeapify (arr : Array Nat) (i : Nat) (heapSize : Nat) (fuel : Nat) : Array Nat :=
  match fuel with
  | 0 => arr
  | fuel' + 1 =>
    let l := left i
    let r := right i
    let largest :=
      if l < heapSize then
        if arr[l]! > arr[i]! then l else i
      else i
    let largest :=
      if r < heapSize then
        if arr[r]! > arr[largest]! then r else largest
      else largest
    if largest != i then
      let arr' := mySwap arr i largest
      maxHeapify arr' largest heapSize fuel'
    else
      arr

/-- **BUILD-MAX-HEAP** (CLRS 6.3). Converts an arbitrary array into a
    max-heap by calling maxHeapify from the last internal node down to 0. -/
def buildMaxHeap (arr : Array Nat) : Array Nat :=
  let n := arr.size
  if n <= 1 then arr
  else
    let start := parent (n - 1)
    let rec loop (arr : Array Nat) (fuel : Nat) (i : Nat) : Array Nat :=
      match fuel with
      | 0 => arr
      | fuel' + 1 =>
        let arr' := maxHeapify arr i n n
        if i == 0 then arr'
        else loop arr' fuel' (i - 1)
    loop arr (start + 1) start

/--
**HEAPSORT** (CLRS 6.4). Sorts an array of natural numbers in ascending order.

1. Build a max-heap from the input array.
2. Repeatedly swap the root (maximum) to the end and restore the heap property.

## Examples

/-!
# VeriBench -- HeapsortAlgorithm (CLRS Chapter 6, Section 6.4)

Lean 4 formalization of the HEAPSORT algorithm from CLRS (Introduction to
Algorithms, 3rd Edition), Section 6.4. Uses **0-based indexing**:
- parent(i) = (i - 1) / 2
- left(i)   = 2 * i + 1
- right(i)  = 2 * i + 2

File order:

1. Implementation (functional, Array-based)
2. Unit tests (positive, edge, positive/negative test suite)
3. Property-based tests
4. Pre-condition prop
5. Exhaustive property props and their theorems
6. Post-condition prop (same order as property props)
7. Correctness theorem `Pre -> Post`
8. Imperative implementation, tests, equivalence theorem

All real proofs are left as `sorry` for the learner/model/agent.

## CLRS Pseudocode (Section 6.4)

```
HEAPSORT(A)
1  BUILD-MAX-HEAP(A)
2  for i = A.length downto 2
3      exchange A[1] with A[i]
4      A.heap-size = A.heap-size - 1
5      MAX-HEAPIFY(A, 1)
```

Running time: O(n lg n). BUILD-MAX-HEAP is O(n), followed by n-1 calls to
MAX-HEAPIFY each costing O(lg n).

Loop invariant (Exercise 6.4-2): At the start of each iteration of the for
loop, the subarray A[0..i] is a max-heap containing the i+1 smallest elements
of A[0..n-1], and A[i+1..n-1] contains the n-1-i largest elements in sorted
order.
-/


open List

/-!
# Pre-Condition
-/

/-- **Pre-condition.** Any array of natural numbers is valid input. -/
def Pre (_arr : Array Nat) : Prop := True

/-!
# Auxiliary Size-Preservation Lemmas
-/

/-- mySwap preserves array size. -/
theorem mySwap_size (arr : Array Nat) (i j : Nat) :
    (mySwap arr i j).size = arr.size := by
  unfold mySwap
  simp

/-- maxHeapify preserves array size. -/
theorem maxHeapify_size (arr : Array Nat) (i heapSize fuel : Nat) :
    (maxHeapify arr i heapSize fuel).size = arr.size := by
  induction fuel generalizing arr i with
  | zero => simp [maxHeapify]
  | succ n ih =>
    unfold maxHeapify
    dsimp only []
    split <;> split <;> try split <;> try split <;> try split
    all_goals (first | (rw [ih]; simp [mySwap_size]) | simp)

/-- buildMaxHeap.loop preserves array size. -/
theorem buildMaxHeap_loop_size (n : Nat) (a : Array Nat) (fuel i : Nat) :
    (buildMaxHeap.loop n a fuel i).size = a.size := by
  induction fuel generalizing a i with
  | zero => simp [buildMaxHeap.loop]
  | succ f ih =>
    unfold buildMaxHeap.loop
    simp only []
    split
    · exact maxHeapify_size a i n n
    · rw [ih]; exact maxHeapify_size a i n n

/-- buildMaxHeap preserves array size. -/
theorem buildMaxHeap_size (arr : Array Nat) :
    (buildMaxHeap arr).size = arr.size := by
  unfold buildMaxHeap
  simp only []
  split
  · rfl
  · exact buildMaxHeap_loop_size arr.size arr _ _

/-- heapsort.extractLoop preserves array size. -/
theorem extractLoop_size (arr : Array Nat) (i fuel : Nat) (h : arr.size = n) :
    (heapsort.extractLoop arr i fuel).size = n := by
  induction fuel generalizing arr i with
  | zero => simp [heapsort.extractLoop]; exact h
  | succ f ih =>
    unfold heapsort.extractLoop
    simp only []
    split
    · exact h
    · exact ih _ _ (by rw [maxHeapify_size, mySwap_size]; exact h)

/-!
# Property Theorems
-/

/-- Helper: an array is sorted in ascending order. -/
def IsSorted (arr : Array Nat) : Prop :=
  ∀ i j : Fin arr.size, i.val < j.val → arr[i] <= arr[j]

/-- Helper: two arrays are permutations of each other (same multiset). -/
def IsPermutation (a b : Array Nat) : Prop :=
  a.toList ~ b.toList

/-- **Sorted property**: the output of heapsort is sorted in ascending order. -/
def sorted_prop (arr : Array Nat) : Prop := IsSorted (heapsort arr)

/-- **Sorted theorem**: heapsort produces a sorted array. -/
-- sorry: verification pass also failed; reason: deep inductive proof over fuel-based recursion requiring heap invariant reasoning
def permutation_prop (arr : Array Nat) : Prop := IsPermutation (heapsort arr) arr

/-- **Permutation theorem**: heapsort produces a permutation of the input. -/
-- sorry: verification pass also failed; reason: permutation proof requires tracking element multisets through swap operations
def length_preserved_prop (arr : Array Nat) : Prop := (heapsort arr).size = arr.size

/-- **Length preservation theorem**: heapsort preserves array size. -/
def idempotent_prop (arr : Array Nat) : Prop := heapsort (heapsort arr) = heapsort arr

/-- **Idempotent theorem**: heapsort is idempotent. -/
-- sorry: verification pass also failed; reason: idempotence requires proving sort of sorted array is identity, depends on unproved sorted_thm
## CLRS Running Time Theorems (stated as comments)

-- **Theorem (CLRS 6.4)**: HEAPSORT runs in O(n lg n) time.
--   BUILD-MAX-HEAP takes O(n), followed by (n-1) calls to MAX-HEAPIFY,
--   each taking O(lg n).

-- **Exercise 6.4-3**: On already-sorted input, HEAPSORT still runs in
--   Theta(n lg n) because BUILD-MAX-HEAP must rearrange the elements and
--   each MAX-HEAPIFY call traverses O(lg n) levels.

-- **Exercise 6.4-4**: The worst-case running time of HEAPSORT is Omega(n lg n).

-- **Exercise 6.4-5**: When all elements are distinct, the best-case
--   running time of HEAPSORT is Omega(n lg n).
-/

/-!
# Post-Condition (conjunction of all desired properties)
-/

/-- **Post-condition**: conjunction of all desired properties for heapsort. -/
def Post_prop (arr : Array Nat) : Prop :=
  (sorted_prop arr) ∧
  (permutation_prop arr) ∧
  (length_preserved_prop arr) ∧
  (idempotent_prop arr)


end HeapsortAlgorithm