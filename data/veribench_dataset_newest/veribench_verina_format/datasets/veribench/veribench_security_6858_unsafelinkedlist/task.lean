-- !benchmark @start import type=solution
import Mathlib
namespace NullPointerDereference
-- !benchmark @end import

-- !benchmark @start solution_aux
inductive ListNode where
  | node (value : Nat) (next : Option ListNode)
  deriving Repr
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def unsafeFindLast_precond (lst : Option ListNode) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def unsafeFindLast (lst : Option ListNode) (h_precond : unsafeFindLast_precond (lst)) : Option Nat :=
  -- !benchmark @start code
  match lst with
  | none => none
  | some (ListNode.node value none) => some value
  | some (ListNode.node _ (some next)) => unsafeFindLast (some next) (by simp)
  -- !benchmark @end code

-- !benchmark @start postcond_aux
def safeFindLast : Option ListNode → Option Nat :=
  unsafeFindLast (h_precond := (by simp))

def none_handling_prop : Prop := unsafeFindLast (none) (by simp) = none

theorem none_handling_thm : none_handling_prop := by
  sorry

def single_node_prop (val : Nat) : Prop :=
  unsafeFindLast (some ⟨val, none⟩) (by simp) = some val

theorem single_node_thm (val : Nat) : single_node_prop val := by
  sorry

def last_value_prop (lst : Option ListNode) : Prop :=
  match lst with
  | none => unsafeFindLast (lst) (by simp) = none
  | some _ => ∃ val, unsafeFindLast (lst) (by simp) = some val

theorem last_value_thm (lst : Option ListNode) : last_value_prop lst := by
  sorry

def safe_equivalence_prop (lst : Option ListNode) : Prop :=
  safeFindLast lst = unsafeFindLast (lst) (by simp)

theorem safe_equivalence_thm (lst : Option ListNode) : safe_equivalence_prop lst := by
  sorry
-- !benchmark @end postcond_aux

@[reducible, simp]
def unsafeFindLast_postcond (lst : Option ListNode) (result : Option Nat)
    (h_precond : unsafeFindLast_precond (lst)) :=
  -- !benchmark @start postcond
  (none_handling_prop) ∧
    (∀ val, single_node_prop val) ∧
    (last_value_prop lst) ∧
    (safe_equivalence_prop lst)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
-- !benchmark @end proof_aux

theorem unsafeFindLast_spec_satisfied (lst : Option ListNode) (h_precond : unsafeFindLast_precond (lst)) :
    unsafeFindLast_postcond (lst) (unsafeFindLast (lst) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof