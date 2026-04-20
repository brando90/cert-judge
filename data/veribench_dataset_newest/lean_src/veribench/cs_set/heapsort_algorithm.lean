import Mathlib

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

namespace HeapsortAlgorithm

open List

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

```
#eval heapsort #[3, 1, 2]   -- #[1, 2, 3]
#eval heapsort #[5, 13, 2, 25, 7, 17, 20, 8, 4]  -- #[2, 4, 5, 7, 8, 13, 17, 20, 25]
```
-/
def heapsort (arr : Array Nat) : Array Nat :=
  if arr.size <= 1 then arr
  else
    let heap := buildMaxHeap arr
    let rec extractLoop (arr : Array Nat) (i : Nat) (fuel : Nat) : Array Nat :=
      match fuel with
      | 0 => arr
      | fuel' + 1 =>
        if i == 0 then arr
        else
          let arr' := mySwap arr 0 i
          let arr'' := maxHeapify arr' 0 i i
          extractLoop arr'' (i - 1) fuel'
    extractLoop heap (arr.size - 1) arr.size

/-!
# Tests
-/

/-- expected: #[1, 2, 3] -/
example : heapsort #[3, 1, 2] = #[1, 2, 3] := by native_decide
#eval heapsort #[3, 1, 2] -- expected: #[1, 2, 3]

/-- expected: #[1, 2, 3] -/
example : heapsort #[1, 2, 3] = #[1, 2, 3] := by native_decide
#eval heapsort #[1, 2, 3] -- expected: #[1, 2, 3]

/-- Exercise 6.4-1: heapsort on (5, 13, 2, 25, 7, 17, 20, 8, 4) -/
example : heapsort #[5, 13, 2, 25, 7, 17, 20, 8, 4] =
    #[2, 4, 5, 7, 8, 13, 17, 20, 25] := by native_decide
#eval heapsort #[5, 13, 2, 25, 7, 17, 20, 8, 4]

/-!
# Tests: Edge Cases
-/

/-- empty array -/
example : heapsort #[] = #[] := by native_decide
#eval heapsort #[] -- expected: #[]

/-- single element -/
example : heapsort #[42] = #[42] := by native_decide
#eval heapsort #[42] -- expected: #[42]

/-- two elements -/
example : heapsort #[2, 1] = #[1, 2] := by native_decide
#eval heapsort #[2, 1] -- expected: #[1, 2]

/-- all same elements -/
example : heapsort #[7, 7, 7, 7] = #[7, 7, 7, 7] := by native_decide
#eval heapsort #[7, 7, 7, 7] -- expected: #[7, 7, 7, 7]

/-!
# Positive / Negative Test-Suite
-/

/-- positive: already sorted stays sorted -/
example : heapsort #[1, 2, 3, 4, 5] = #[1, 2, 3, 4, 5] := by native_decide
#eval heapsort #[1, 2, 3, 4, 5] -- expected: #[1, 2, 3, 4, 5]

/-- positive: reverse sorted gets sorted (Exercise 6.4-3) -/
example : heapsort #[9, 8, 7, 6, 5, 4, 3, 2, 1] =
    #[1, 2, 3, 4, 5, 6, 7, 8, 9] := by native_decide
#eval heapsort #[9, 8, 7, 6, 5, 4, 3, 2, 1]

/-- positive: duplicates are handled correctly -/
example : heapsort #[3, 1, 4, 1, 5, 9, 2, 6, 5, 3] =
    #[1, 1, 2, 3, 3, 4, 5, 5, 6, 9] := by native_decide
#eval heapsort #[3, 1, 4, 1, 5, 9, 2, 6, 5, 3]

/-- positive: random order -/
example : heapsort #[5, 2, 4, 6, 1, 3] = #[1, 2, 3, 4, 5, 6] := by native_decide
#eval heapsort #[5, 2, 4, 6, 1, 3] -- expected: #[1, 2, 3, 4, 5, 6]

/-- negative: heapsort [3, 1, 2] != [3, 2, 1] -/
example : heapsort #[3, 1, 2] != #[3, 2, 1] := by native_decide
#eval (decide (heapsort #[3, 1, 2] = #[3, 2, 1])) -- expected: false

/-- negative: heapsort [2, 1] != [2, 1] -/
example : heapsort #[2, 1] != #[2, 1] := by native_decide
#eval (decide (heapsort #[2, 1] = #[2, 1])) -- expected: false

/-!
# Property-Based Tests (via `#eval`)
-/

-- Property test: output is sorted
#eval do
  let inputs : List (Array Nat) := [#[], #[1], #[2, 1], #[3, 1, 2],
      #[5, 13, 2, 25, 7, 17, 20, 8, 4]]
  for arr in inputs do
    let sorted := heapsort arr
    for i in List.range (sorted.size - 1) do
      if sorted[i]! > sorted[i+1]! then
        IO.println s!"FAIL: output not sorted for {arr.toList}"
        return
  IO.println "PASS: all outputs are sorted"

-- Property test: output length matches input length
#eval do
  let inputs : List (Array Nat) := [#[], #[1], #[2, 1], #[3, 1, 2],
      #[5, 13, 2, 25, 7, 17, 20, 8, 4]]
  for arr in inputs do
    let sorted := heapsort arr
    if sorted.size != arr.size then
      IO.println s!"FAIL: length mismatch for {arr.toList}"
      return
  IO.println "PASS: all output lengths match"

-- Property test: output is a permutation (same multiset)
#eval do
  let inputs : List (Array Nat) := [#[], #[1], #[2, 1], #[3, 1, 2],
      #[5, 13, 2, 25, 7, 17, 20, 8, 4]]
  for arr in inputs do
    let sorted := heapsort arr
    let inSorted := arr.toList.mergeSort (· <= ·)
    let outSorted := sorted.toList.mergeSort (· <= ·)
    if inSorted != outSorted then
      IO.println s!"FAIL: not a permutation for {arr.toList}"
      return
  IO.println "PASS: all outputs are permutations"

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
@[simp] theorem sorted_thm (arr : Array Nat) : sorted_prop arr := sorry

/-- **Permutation property**: the output of heapsort is a permutation of the input. -/
def permutation_prop (arr : Array Nat) : Prop := IsPermutation (heapsort arr) arr

/-- **Permutation theorem**: heapsort produces a permutation of the input. -/
-- sorry: verification pass also failed; reason: permutation proof requires tracking element multisets through swap operations
@[simp] theorem permutation_thm (arr : Array Nat) : permutation_prop arr := sorry

/-- **Length preservation property**: the output has the same size as the input. -/
def length_preserved_prop (arr : Array Nat) : Prop := (heapsort arr).size = arr.size

/-- **Length preservation theorem**: heapsort preserves array size. -/
@[simp] theorem length_preserved_thm (arr : Array Nat) : length_preserved_prop arr := by
  unfold length_preserved_prop heapsort
  simp only []
  split
  · rfl
  · exact extractLoop_size _ _ _ (buildMaxHeap_size arr)

/-- **Idempotent property**: sorting an already-sorted array yields the same result. -/
def idempotent_prop (arr : Array Nat) : Prop := heapsort (heapsort arr) = heapsort arr

/-- **Idempotent theorem**: heapsort is idempotent. -/
-- sorry: verification pass also failed; reason: idempotence requires proving sort of sorted array is identity, depends on unproved sorted_thm
@[simp] theorem idempotent_thm (arr : Array Nat) : idempotent_prop arr := sorry

/-!
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

/-!
# Correctness Theorem
-/

/-- **Correctness theorem**: the pre-condition implies the post-condition. -/
theorem correctness_thm (arr : Array Nat) (_hPre : Pre arr) : Post_prop arr := by
  unfold Post_prop
  exact ⟨sorted_thm arr, permutation_thm arr, length_preserved_thm arr, idempotent_thm arr⟩

/-!
# Imperative Implementation

Closely follows the CLRS pseudocode using `Id.run do` with mutable variables.
-/

/-- **MAX-HEAPIFY** (imperative, CLRS 6.2). Restores the max-heap property
    at index `idx` considering the first `heapSz` elements. Uses an
    iterative sift-down loop (equivalent to the recursive version). -/
def maxHeapifyImp (a : Array Nat) (idx : Nat) (heapSz : Nat) : Array Nat :=
  Id.run do
    let mut arr := a
    let mut i := idx
    for _ in List.range heapSz do
      let l := left i
      let r := right i
      let mut largest := i
      if l < heapSz && arr[l]! > arr[largest]! then
        largest := l
      if r < heapSz && arr[r]! > arr[largest]! then
        largest := r
      if largest != i then
        arr := mySwap arr i largest
        i := largest
      else
        return arr
    return arr

/-- **BUILD-MAX-HEAP** (imperative, CLRS 6.3). Builds a max-heap by
    calling maxHeapifyImp from the last internal node down to index 0. -/
def buildMaxHeapImp (a : Array Nat) : Array Nat :=
  Id.run do
    let mut arr := a
    let n := arr.size
    if n <= 1 then return arr
    let start := parent (n - 1)
    for j in List.range (start + 1) do
      let i := start - j
      arr := maxHeapifyImp arr i n
    return arr

/--
**HEAPSORT** (imperative, CLRS 6.4). Sorts using mutable array operations,
closely following the CLRS pseudocode:
```
HEAPSORT(A)
1  BUILD-MAX-HEAP(A)
2  for i = A.length downto 2
3      exchange A[1] with A[i]
4      A.heap-size = A.heap-size - 1
5      MAX-HEAPIFY(A, 1)
```
(Adapted to 0-based indexing.)
-/
def heapsortImp (arr : Array Nat) : Array Nat :=
  Id.run do
    if arr.size <= 1 then return arr
    let mut a := buildMaxHeapImp arr
    for j in List.range (a.size - 1) do
      let i := a.size - 1 - j
      a := mySwap a 0 i
      a := maxHeapifyImp a 0 i
    return a

/-!
# Imperative Tests
-/

/-- expected: #[1, 2, 3] -/
example : heapsortImp #[3, 1, 2] = #[1, 2, 3] := by native_decide
#eval heapsortImp #[3, 1, 2] -- expected: #[1, 2, 3]

/-- Exercise 6.4-1 (imperative): heapsort on (5, 13, 2, 25, 7, 17, 20, 8, 4) -/
example : heapsortImp #[5, 13, 2, 25, 7, 17, 20, 8, 4] =
    #[2, 4, 5, 7, 8, 13, 17, 20, 25] := by native_decide
#eval heapsortImp #[5, 13, 2, 25, 7, 17, 20, 8, 4]

/-!
# Imperative Tests: Edge Cases
-/

/-- empty array -/
example : heapsortImp #[] = #[] := by native_decide
#eval heapsortImp #[] -- expected: #[]

/-- single element -/
example : heapsortImp #[42] = #[42] := by native_decide
#eval heapsortImp #[42] -- expected: #[42]

/-- two elements -/
example : heapsortImp #[2, 1] = #[1, 2] := by native_decide
#eval heapsortImp #[2, 1] -- expected: #[1, 2]

/-- all same -/
example : heapsortImp #[7, 7, 7, 7] = #[7, 7, 7, 7] := by native_decide
#eval heapsortImp #[7, 7, 7, 7] -- expected: #[7, 7, 7, 7]

/-!
# Imperative Positive / Negative Test-Suite
-/

/-- positive: already sorted stays sorted -/
example : heapsortImp #[1, 2, 3, 4, 5] = #[1, 2, 3, 4, 5] := by native_decide
#eval heapsortImp #[1, 2, 3, 4, 5] -- expected: #[1, 2, 3, 4, 5]

/-- positive: reverse sorted gets sorted -/
example : heapsortImp #[9, 8, 7, 6, 5, 4, 3, 2, 1] =
    #[1, 2, 3, 4, 5, 6, 7, 8, 9] := by native_decide
#eval heapsortImp #[9, 8, 7, 6, 5, 4, 3, 2, 1]

/-- negative: heapsortImp [3, 1, 2] != [3, 2, 1] -/
example : heapsortImp #[3, 1, 2] != #[3, 2, 1] := by native_decide
#eval (decide (heapsortImp #[3, 1, 2] = #[3, 2, 1])) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem heapsort_equivalence_thm (arr : Array Nat) :
    -- sorry: verification pass also failed; reason: recursive vs iterative structure mismatch requires auxiliary lemmas for maxHeapify/maxHeapifyImp equivalence
    heapsort arr = heapsortImp arr := sorry

end HeapsortAlgorithm
