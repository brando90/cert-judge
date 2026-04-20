-- !benchmark @start import type=solution
import Mathlib
namespace DFS

open List

abbrev Graph := List (List Nat)
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def dfs_precond (g : Graph) (start : Nat) (target : Nat) : Prop :=
  -- !benchmark @start precond
  (∀ i < g.length, ∀ n ∈ g[i]!, n < g.length) ∧
  (start < g.length) ∧
  (target < g.length)
  -- !benchmark @end precond

-- !benchmark @start code_aux
def dfsAux (g : Graph) (current target : Nat) (visited : List Nat) (fuel : Nat) : Bool :=
  match fuel with
  | 0 => false
  | n + 1 =>
    if current == target then
      true
    else if current ∈ visited then
      false
    else
      let neighbors := g[current]?.getD []
      neighbors.any (fun next => dfsAux g next target (current :: visited) n)
-- !benchmark @end code_aux

def dfs (g : Graph) (start : Nat) (target : Nat) (h_precond : dfs_precond (g) (start) (target)) : Bool :=
  -- !benchmark @start code
  dfsAux g start target [] (g.length + 1)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def dfs_postcond (g : Graph) (start : Nat) (target : Nat) (result : Bool)
    (h_precond : dfs_precond (g) (start) (target)) : Prop :=
  -- !benchmark @start postcond
  (result = true → Reachable g start target) ∧
  (dfs_precond g start target → Reachable g start target → result = true)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
inductive Reachable (g : Graph) : Nat → Nat → Prop where
  | base (x) : Reachable g x x
  | step (x y z) : y ∈ (g[x]?).getD [] → Reachable g y z → Reachable g x z

def soundness_prop (g : Graph) (start target : Nat) : Prop :=
  dfs g start target (by sorry) = true → Reachable g start target

theorem soundness_thm (g : Graph) (start target : Nat) : soundness_prop g start target := by
  sorry

def completeness_prop (g : Graph) (start target : Nat) : Prop :=
  dfs_precond g start target → Reachable g start target → dfs g start target (by sorry) = true

theorem completeness_thm (g : Graph) (start target : Nat) : completeness_prop g start target := by
  sorry
-- !benchmark @end proof_aux

theorem dfs_spec_satisfied (g : Graph) (start : Nat) (target : Nat) (h_precond : dfs_precond (g) (start) (target)) :
    dfs_postcond (g) (start) (target) (dfs (g) (start) (target) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof