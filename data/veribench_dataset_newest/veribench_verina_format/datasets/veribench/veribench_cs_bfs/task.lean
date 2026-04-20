-- !benchmark @start import type=solution
import Mathlib
namespace BFS
-- !benchmark @end import

-- !benchmark @start solution_aux
open List

abbrev Graph := List (List Nat)
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def bfs_precond (g : Graph) (start : Nat) (target : Nat) : Prop :=
  -- !benchmark @start precond
  (∀ i < g.length, ∀ n ∈ g[i]!, n < g.length) ∧
  (start < g.length) ∧
  (target < g.length)
  -- !benchmark @end precond

-- !benchmark @start code_aux
def bfsAux (g : Graph) (target : Nat) (queue : List (Nat × Nat)) (visited : List Nat) (fuel : Nat) : Option Nat :=
  match fuel with
  | 0 => none
  | n + 1 =>
    match queue with
    | [] => none
    | (curr, dist) :: restQueue =>
      if curr == target then
        some dist
      else
        let neighbors := g[curr]?.getD []
        let newNeighbors := neighbors.filter (fun x => x ∉ visited)
        let newEntries := newNeighbors.map (fun x => (x, dist + 1))
        bfsAux g target (restQueue ++ newEntries) (visited ++ newNeighbors) n
-- !benchmark @end code_aux

def bfs (g : Graph) (start : Nat) (target : Nat) (h_precond : bfs_precond (g) (start) (target)) : Option Nat :=
  -- !benchmark @start code
  if start == target then
    some 0
  else
    bfsAux g target [(start, 0)] [start] (g.length * g.length + 1)
  -- !benchmark @end code

-- !benchmark @start postcond_aux
inductive IsPath (g : Graph) : Nat → Nat → List Nat → Prop where
  | base (x) : IsPath g x x []
  | step (x y z path) : y ∈ g[x]?.getD [] → IsPath g y z path → IsPath g x z (y :: path)

def soundness_prop (g : Graph) (start target : Nat) : Prop :=
  ∀ d, bfs g start target (by sorry) = some d → ∃ path, IsPath g start target path ∧ path.length = d

def optimality_prop (g : Graph) (start target : Nat) : Prop :=
  ∀ d, bfs g start target (by sorry) = some d →
    ∀ path, IsPath g start target path → path.length ≥ d
-- !benchmark @end postcond_aux

@[reducible, simp]
def bfs_postcond (g : Graph) (start : Nat) (target : Nat) (result : Option Nat) (h_precond : bfs_precond (g) (start) (target)) :=
  -- !benchmark @start postcond
  soundness_prop g start target ∧
    optimality_prop g start target
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
theorem soundness_thm (g : Graph) (start target : Nat) : soundness_prop g start target := by
  sorry

theorem optimality_thm (g : Graph) (start target : Nat) : optimality_prop g start target := by
  sorry
-- !benchmark @end proof_aux

theorem bfs_spec_satisfied (g : Graph) (start : Nat) (target : Nat) (h_precond : bfs_precond (g) (start) (target)) :
    bfs_postcond (g) (start) (target) (bfs (g) (start) (target) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof