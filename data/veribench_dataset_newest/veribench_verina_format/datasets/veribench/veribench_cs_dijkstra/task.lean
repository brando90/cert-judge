-- !benchmark @start import type=solution
import Mathlib
namespace Dijkstra
open List
-- !benchmark @end import

-- !benchmark @start solution_aux
abbrev Graph := List (List (Nat × Nat))

-- helpers
def extractMin (queue : List (Nat × Nat)) : Option ((Nat × Nat) × List (Nat × Nat)) :=
  match queue with
  | [] => none
  | head :: tail =>
    let minEntry := queue.foldl (fun acc x => if x.1 < acc.1 then x else acc) head
    let rest := queue.erase minEntry
    some (minEntry, rest)

def dijkstraAux (g : Graph) (target : Nat) (queue : List (Nat × Nat)) (visited : List Nat) (fuel : Nat) : Option Nat :=
  match fuel with
  | 0 => none
  | n + 1 =>
    match extractMin queue with
    | none => none
    | some ((dist, u), restQueue) =>
      if u == target then
        some dist
      else if u ∈ visited then
        dijkstraAux g target restQueue visited n
      else
        let neighbors := g[u]?.getD []
        let newEntries := neighbors.map (fun (v, w) => (dist + w, v))
        dijkstraAux g target (restQueue ++ newEntries) (u :: visited) n

inductive IsWeightedPath (g : Graph) : Nat → Nat → Nat → Prop where
  | base (x) : IsWeightedPath g x x 0
  | step (x y z w total) :
      (y, w) ∈ g[x]?.getD [] →
      IsWeightedPath g y z total →
      IsWeightedPath g x z (w + total)
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def dijkstra_precond (g : Graph) (start : Nat) (target : Nat) : Prop :=
  -- !benchmark @start precond
  (∀ i < g.length, ∀ edge ∈ g[i]!, edge.1 < g.length) ∧
  (start < g.length) ∧
  (target < g.length)
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

/--
**Implementation of `dijkstra`.**

Computes shortest path from `start` to `target`.
Returns `some distance` or `none`.
-/
def dijkstra (g : Graph) (start : Nat) (target : Nat) (h_precond : dijkstra_precond (g) (start) (target)) : Option Nat :=
  -- !benchmark @start code
  let n := g.length
  dijkstraAux g target [(0, start)] [] (n * n + 1)
  -- !benchmark @end code

-- !benchmark @start postcond_aux
def soundness_prop (g : Graph) (start target : Nat) : Prop :=
  ∀ d, dijkstra g start target (by sorry) = some d → IsWeightedPath g start target d

theorem soundness_thm (g : Graph) (start target : Nat) : soundness_prop g start target := by
  sorry

def optimality_prop (g : Graph) (start target : Nat) : Prop :=
  ∀ d, dijkstra g start target (by sorry) = some d →
  ∀ d', IsWeightedPath g start target d' → d ≤ d'

theorem optimality_thm (g : Graph) (start target : Nat) : optimality_prop g start target := by
  sorry
-- !benchmark @end postcond_aux

@[reducible, simp]
def dijkstra_postcond (g : Graph) (start : Nat) (target : Nat) (result : Option Nat)
    (h_precond : dijkstra_precond (g) (start) (target)) :=
  -- !benchmark @start postcond
  soundness_prop g start target ∧
  optimality_prop g start target
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- !benchmark @end proof_aux

theorem dijkstra_spec_satisfied (g : Graph) (start : Nat) (target : Nat)
    (h_precond : dijkstra_precond (g) (start) (target)) :
    dijkstra_postcond (g) (start) (target) (dijkstra (g) (start) (target) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof