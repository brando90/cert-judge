import Mathlib.Data.List.Basic
import Mathlib.Data.Nat.Basic

open List
namespace DFS

/-!
# Implementation
-/

def dfsAux (g : Graph) (current target : Nat) (visited : List Nat) (fuel : Nat) : Bool :=
    match fuel with 
     | 0 => false
     | n+1 =>
       if current == target then
         true
       else if current ∈ visited then
         false
       else
         let neighbors := g[current]?.getD []
         neighbors.any (λ next => dfsAux g next target (current :: visited) n)

def dfs (g : Graph) (start target : Nat) : Bool :=
  dfsAux g start target [] (g.length + 1)

-- Helper lemmas for the proofs

/-!
# VeriBench – Depth First Search (DFS)

File order:
1. Implementation
2. Unit tests
3. Pre-condition prop
4. Property theorems
5. Post-condition prop
6. Correctness theorem
7. Imperative implementation
8. Equivalence theorem
-/


open List

abbrev Graph := List (List Nat)

/-!
# Pre-Condition
-/

def Pre(g : Graph)(start target : Nat) : Prop :=
  (∀ i < g.length, ∀ n ∈ g[i]!, n < g.length) ∧
  (start < g.length) ∧
  (target < g.length)

/-!
# Property Theorems
-/

inductive Reachable (g : Graph) : Nat → Nat → Prop where
  | base (x) : Reachable g x x
  | step (x y z) : y ∈ (g[x]?).getD [] → Reachable g y z → Reachable g x z

def soundness_prop (g : Graph) (start target : Nat) : Prop :=
  dfs g start target = true → Reachable g start target

def completeness_prop (g : Graph) (start target : Nat) : Prop :=
  Pre g start target → Reachable g start target → dfs g start target = true

/-!
# Post-Condition
-/

def Post_prop (g : Graph) (start target : Nat) : Prop :=
  (soundness_prop g start target) ∧
  (completeness_prop g start target)

theorem correctness_thm (g : Graph) (start target : Nat) : Post_prop g start target :=
  ⟨soundness_thm g start target, completeness_thm g start target⟩

lemma dfsAux_fuel_monotone (g : Graph) (current target : Nat) (visited : List Nat) (fuel1 fuel2 : Nat) :
  fuel1 ≤ fuel2 → 
  dfsAux g current target visited fuel1 = true → 
  dfsAux g current target visited fuel2 = true := by
  intro h_le h_true
  induction fuel2, fuel1 using Nat.strong_induction_on with
  | ind n ih =>
    cases fuel1 with
    | zero =>
      simp [dfsAux] at h_true
    | succ fuel1' =>
      cases n with
      | zero =>
        simp at h_le
      | succ fuel2' =>
        simp [dfsAux] at h_true ⊢
        split at h_true ⊢
        · exact h_true
        · split at h_true ⊢
          · exact h_true
          · simp [List.any_eq_true] at h_true ⊢
            obtain ⟨next, h_mem, h_rec⟩ := h_true
            use next, h_mem
            apply ih
            · exact Nat.lt_succ_iff.mpr (Nat.le_refl _)
            · exact fuel1'
            · exact Nat.le_of_succ_le_succ h_le
            · exact h_rec

lemma dfsAux_target_true (g : Graph) (target : Nat) (visited : List Nat) (fuel : Nat) :
  fuel > 0 → dfsAux g target target visited fuel = true := by
  intro h_pos
  cases fuel with
  | zero => contradiction
  | succ n =>
    simp [dfsAux]

lemma dfsAux_visited_false (g : Graph) (current target : Nat) (visited : List Nat) (fuel : Nat) :
  current ∈ visited → dfsAux g current target visited fuel = false := by
  intro h_mem
  cases fuel with
  | zero => simp [dfsAux]
  | succ n =>
    simp [dfsAux]
    split
    · split
      · simp at h_mem
        exact h_mem
      · rfl
    · split
      · simp at h_mem
        exact h_mem
      · rfl

lemma reachable_of_dfsAux (g : Graph) (current target : Nat) (visited : List Nat) (fuel : Nat) :
  dfsAux g current target visited fuel = true → Reachable g current target := by
  induction fuel, current using Nat.strong_induction_on with
  | ind n ih =>
    intro h_dfs
    cases n with
    | zero =>
      simp [dfsAux] at h_dfs
    | succ fuel' =>
      simp [dfsAux] at h_dfs
      split at h_dfs
      · simp at *
        rw [←h_dfs]
        exact Reachable.base current
      · split at h_dfs
        · contradiction
        · simp [List.any_eq_true] at h_dfs
          obtain ⟨next, h_mem, h_rec⟩ := h_dfs
          apply Reachable.step current next target h_mem
          apply ih
          · exact Nat.lt_succ_iff.mpr (Nat.le_refl _)
          · exact next
          · exact h_rec

lemma dfsAux_of_reachable (g : Graph) (current target : Nat) (visited : List Nat) (fuel : Nat) :
  (∀ i < g.length, ∀ n ∈ g[i]!, n < g.length) →
  current < g.length →
  target < g.length →
  current ∉ visited →
  (∀ v ∈ visited, v < g.length) →
  visited.length + fuel > g.length →
  Reachable g current target → 
  dfsAux g current target visited fuel = true := by
  intro h_valid h_curr h_targ h_not_visited h_visited_valid h_fuel h_reach
  induction h_reach using Reachable.rec generalizing visited fuel with
  | base x =>
    cases fuel with
    | zero =>
      simp [dfsAux]
      exfalso
      have : visited.length + 0 > g.length := h_fuel
      simp at this
      have : visited.length < g.length := by
        apply List.length_lt_of_mem_of_length_lt_card
        · exact h_visited_valid
        · simp
          exact h_curr
      linarith
    | succ n =>
      simp [dfsAux]
      rfl
  | step x y z h_edge h_reach_yz ih =>
    cases fuel with
    | zero =>
      simp [dfsAux]
      exfalso
      have : visited.length + 0 > g.length := h_fuel
      simp at this
      have : visited.length < g.length := by
        apply List.length_lt_of_mem_of_length_lt_card
        · exact h_visited_valid
        · simp
          exact h_curr
      linarith
    | succ n =>
      simp [dfsAux]
      split
      · rfl
      · split
        · contradiction
        · simp [List.any_eq_true]
          use y, h_edge
          apply ih
          · have : y ∈ g[x]!.toList := h_edge
            simp at this
            cases h_x_bounds : x < g.length with
            | false =>
              exfalso
              simp at h_x_bounds
              exact Nat.not_le.mp h_x_bounds h_curr
            | true =>
              have := h_valid x h_x_bounds y this
              exact this
          · simp
            constructor
            · exact h_curr
            · exact h_visited_valid
          · simp
            have : visited.length + 1 + n = visited.length + Nat.succ n := by simp
            rw [this]
            exact h_fuel
          · exact h_reach_yz

theorem soundness_thm (g : Graph) (start target : Nat) : soundness_prop g start target := by
  intro h_dfs
  simp [dfs] at h_dfs
  exact reachable_of_dfsAux g start target [] (g.length + 1) h_dfs

theorem completeness_thm (g : Graph) (start target : Nat) : completeness_prop g start target := by
  intro h_pre h_reach
  simp [dfs]
  apply dfsAux_of_reachable
  · exact h_pre.1
  · exact h_pre.2.1
  · exact h_pre.2.2
  · simp
  · simp
  · simp
    exact Nat.lt_succ_iff.mpr (Nat.le_refl _)
  · exact h_reach


end DFS