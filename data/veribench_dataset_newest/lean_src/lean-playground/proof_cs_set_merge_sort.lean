import Mathlib.Data.List.Sort
import Mathlib.Data.List.Permutation

open List
namespace MergeSort

/-- Merges two sorted lists into a single sorted list. -/
def merge (l₁ l₂ : List Nat) : List Nat :=
  match l₁, l₂ with
  | [], _ => l₂
  | _, [] => l₁
  | x :: xs, y :: ys =>
    if x ≤ y then
      x :: merge xs (y :: ys)
    else
      y :: merge (x :: xs) ys

/-- Implementation of mergeSort using divide and conquer approach. -/
def mergeSort : List Nat → List Nat
  | [] => []
  | [x] => [x]
  | l =>
    let mid := l.length / 2
    let (front, back) := l.splitAt mid
    merge (mergeSort front) (mergeSort back)

/-- Imperative-style implementation of merge sort (equivalent to functional version). -/
def mergeSortImp (l : List Nat) : List Nat := mergeSort l

-- Helper lemmas for merge function

/-!
# VeriBench – MergeSort

File order:

1. Implementation
2. Unit tests (positive, edge, positive/negative test suite)
3. Pre‑condition prop
4. Exhaustive property prop and their theorems
5. Post‑condition prop (same order as property props)
6. Correctness theorem `Pre → Post`
7. Imperative i. implementation, ii. tests (positive, edge, positive/negative
test suite), and iii. equivalence theorem.

All real proofs are left as `sorry` for the learner/model/agent.

# Implementation

## Merge Sort

Implements the merge sort algorithm for sorting lists of natural numbers.
-/


open List

/-- Merges two sorted lists into a single sorted list. -/
def merge (l₁ l₂ : List Nat) : List Nat := -- This helper is appropriate for merge sort
  match l₁, l₂ with
  | [], _ => l₂
  | _, [] => l₁
  | x :: xs, y :: ys =>
    if x ≤ y then
      x :: merge xs (y :: ys)
    else
      y :: merge (x :: xs) ys

/--
**Implementation of `mergeSort`.**

`mergeSort l` returns a sorted list containing the same elements as `l`.

## Examples

#eval mergeSort [3, 1, 2] -- expected: [1, 2, 3]
#eval mergeSort [] -- expected: []
-/
partial def mergeSort : List Nat → List Nat
  | [] => []
  | [x] => [x] -- Base case for a single-element list
  | l =>
    let (front, back) := l.splitAt (l.length / 2)
    merge (mergeSort front) (mergeSort back)

/-!
# Pre‑Condition
-/

/-- **Pre‑condition.** Any list is valid input. -/
def Pre (xs : List Nat) : Prop := True

/-!
# Property Theorems
-/

/-- **Sorted property**: Result is sorted in ascending order. -/
def sorted_prop (xs : List Nat) : Prop := List.Sorted (· ≤ ·) (mergeSort xs)

/-- **Sorted theorem**: Result is sorted in ascending order. -/
def permutation_prop (xs : List Nat) : Prop := mergeSort xs ~ xs

/-- **Permutation theorem**: Result is a permutation of input. -/
def length_preservation_prop (xs : List Nat) : Prop := (mergeSort xs).length = xs.length

/-- **Length preservation theorem**: Length is preserved. -/
def idempotent_prop (xs : List Nat) : Prop := mergeSort (mergeSort xs) = mergeSort xs

/-- **Idempotent theorem**: Sorting twice gives same result as sorting once. -/

/-!
# Post‑Condition  (conjunction of all desired properties)
-/

/-- **Post‑condition**: conjunction of all desired properties for mergeSort. -/
def Post_prop (xs : List Nat) : Prop :=
  (sorted_prop xs) ∧                                     -- sorted property
  (permutation_prop xs) ∧                                -- permutation property
  (length_preservation_prop xs) ∧                        -- length preservation property
  (idempotent_prop xs)                                   -- idempotent property

lemma merge_sorted_of_sorted {l₁ l₂ : List Nat} 
  (h₁ : List.Sorted (· ≤ ·) l₁) (h₂ : List.Sorted (· ≤ ·) l₂) : 
  List.Sorted (· ≤ ·) (merge l₁ l₂) := by
  induction l₁, l₂ using merge.induct with
  | case1 l => exact h₂
  | case2 l => exact h₁
  | case3 x xs y ys ih₁ ih₂ =>
    simp only [merge]
    split_ifs with h
    · exact List.sorted_cons_of_sorted_of_forall_le (ih₁ (List.sorted_of_sorted_cons h₁) h₂) 
        (fun z hz => by
          have : z ∈ merge xs (y :: ys) := hz
          by_cases hxy : x ≤ y
          · have : y ≤ z ∨ z ∈ xs := by
              induction xs, (y :: ys) using merge.induct generalizing z with
              | case1 => simp [merge] at this; exact Or.inl (le_of_eq this.symm)
              | case2 => simp [merge] at this; exact Or.inr this
              | case3 a as b bs _ _ =>
                simp only [merge] at this
                split_ifs at this with hab
                · cases this with
                  | head => exact Or.inr (Or.inl rfl)
                  | tail => exact Or.inr (Or.inr (ih₁ (List.sorted_of_sorted_cons h₁) h₂).2)
                · cases this with
                  | head => exact Or.inl (le_refl _)
                  | tail => exact ih₂ h₁ (List.sorted_of_sorted_cons h₂)
            cases this with
            | inl h_yz => exact le_trans h h_yz
            | inr h_z_in_xs => 
              exact List.sorted_cons.mp h₁ |>.2 z h_z_in_xs
          · exact le_trans h (le_of_not_le (fun h' => h (le_trans h' (le_of_not_le h))))
        )
    · exact List.sorted_cons_of_sorted_of_forall_le (ih₂ h₁ (List.sorted_of_sorted_cons h₂))
        (fun z hz => by
          have : z ∈ merge (x :: xs) ys := hz
          have hyx : y ≤ x := le_of_not_le h
          by_cases hzx : z = x
          · rw [hzx]; exact hyx
          · have : z ∈ xs ∨ z ∈ ys := by
              induction (x :: xs), ys using merge.induct generalizing z with
              | case1 => simp [merge] at this
              | case2 => 
                simp only [merge] at this
                cases this with
                | head => contradiction
                | tail => exact Or.inl this
              | case3 a as b bs _ _ =>
                simp only [merge] at this
                split_ifs at this
                · cases this with
                  | head => exact Or.inl (Or.inl rfl)
                  | tail => have := ih₂ h₁ (List.sorted_of_sorted_cons h₂); exact this
                · cases this with
                  | head => exact Or.inr (Or.inl rfl)
                  | tail => have := ih₁ (List.sorted_of_sorted_cons h₁) h₂; exact this
            cases this with
            | inl h_z_in_xs => exact List.sorted_cons.mp h₁ |>.2 z h_z_in_xs
            | inr h_z_in_ys => exact List.sorted_cons.mp h₂ |>.2 z h_z_in_ys
        )

lemma merge_perm {l₁ l₂ : List Nat} : merge l₁ l₂ ~ l₁ ++ l₂ := by
  induction l₁, l₂ using merge.induct with
  | case1 l => simp [merge]
  | case2 l => simp [merge]; rfl
  | case3 x xs y ys ih₁ ih₂ =>
    simp only [merge]
    split_ifs with h
    · calc merge (x :: xs) (y :: ys)
        = x :: merge xs (y :: ys) := rfl
        _ ~ x :: (xs ++ y :: ys) := List.Perm.cons _ ih₁
        _ = (x :: xs) ++ (y :: ys) := by simp
    · calc merge (x :: xs) (y :: ys)
        = y :: merge (x :: xs) ys := by simp [merge, h]
        _ ~ y :: ((x :: xs) ++ ys) := List.Perm.cons _ ih₂
        _ ~ (x :: xs) ++ (y :: ys) := by simp [List.perm_append_comm]; rfl

-- Termination proof helper
lemma splitAt_length_lt {l : List Nat} (h : l.length ≥ 2) :
  let (front, back) := l.splitAt (l.length / 2)
  front.length < l.length ∧ back.length < l.length := by
  have h_pos : 0 < l.length := Nat.lt_of_succ_lt_succ (Nat.succ_lt_succ h)
  have h_mid_pos : 0 < l.length / 2 := Nat.div_pos h_pos (by norm_num)
  have h_mid_lt : l.length / 2 < l.length := Nat.div_lt_self h_pos (by norm_num)
  constructor
  · exact List.length_take_le _ _ |>.trans_lt h_mid_lt
  · rw [List.length_drop]
    exact Nat.sub_lt h_pos h_mid_pos

/-- **Sorted theorem**: Result is sorted in ascending order. -/
@[simp] theorem sorted_thm (xs : List Nat) : sorted_prop xs := by
  induction xs using List.strong_induction_on with
  | ind xs ih =>
    unfold sorted_prop mergeSort
    match xs with
    | [] => exact List.sorted_nil
    | [x] => exact List.sorted_singleton _ _
    | _ =>
      let mid := xs.length / 2
      let (front, back) := xs.splitAt mid
      have h_len : xs.length ≥ 2 := by
        match xs with
        | [] | [_] => contradiction
        | _ :: _ :: _ => simp; norm_num
      have h_front : front.length < xs.length := (splitAt_length_lt h_len).1
      have h_back : back.length < xs.length := (splitAt_length_lt h_len).2
      exact merge_sorted_of_sorted (ih front h_front) (ih back h_back)

/-- **Permutation theorem**: Result is a permutation of input. -/
@[simp] theorem permutation_thm (xs : List Nat) : permutation_prop xs := by
  induction xs using List.strong_induction_on with
  | ind xs ih =>
    unfold permutation_prop mergeSort
    match xs with
    | [] => rfl
    | [x] => rfl
    | _ =>
      let mid := xs.length / 2
      let (front, back) := xs.splitAt mid
      have h_len : xs.length ≥ 2 := by
        match xs with
        | [] | [_] => contradiction
        | _ :: _ :: _ => simp; norm_num
      have h_front : front.length < xs.length := (splitAt_length_lt h_len).1
      have h_back : back.length < xs.length := (splitAt_length_lt h_len).2
      calc merge (mergeSort front) (mergeSort back)
        ~ mergeSort front ++ mergeSort back := merge_perm
        _ ~ front ++ mergeSort back := List.Perm.append_left _ (ih front h_front)
        _ ~ front ++ back := List.Perm.append_right _ (ih back h_back)
        _ ~ xs := (List.perm_append_splitAt xs mid).symm

/-- **Length preservation theorem**: Length is preserved. -/
@[simp] theorem length_preservation_thm (xs : List Nat) : length_preservation_prop xs := by
  unfold length_preservation_prop
  exact List.Perm.length_eq (permutation_thm xs)

/-- **Idempotent theorem**: Sorting twice gives same result as sorting once. -/
@[simp] theorem idempotent_thm (xs : List Nat) : idempotent_prop xs := by
  unfold idempotent_prop
  apply List.eq_of_perm_of_sorted
  · exact permutation_thm (mergeSort xs)
  · exact sorted_thm (mergeSort xs)
  · exact sorted_thm xs


end MergeSort