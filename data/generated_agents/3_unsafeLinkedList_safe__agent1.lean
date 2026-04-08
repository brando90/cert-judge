import Mathlib.Data.List.Basic

namespace VeriBench.SafeFindLast

inductive Node where
  | mk (value : Int) (next : Option Node) : Node

def Node.value (n : Node) : Int :=
  match n with
  | mk v _ => v

def Node.next (n : Node) : Option Node :=
  match n with
  | mk _ next => next

/-- 
  Safe linked-list traversal with None checks.
  Returns the value of the last node in the list.
  Raises an error if the list is empty.
-/
def safeFindLast (node : Option Node) : Int :=
  match node with
  | none => panic! "empty list"
  | some n =>
      let rec findLast (current : Node) : Int :=
        match current.next with
        | none => current.value
        | some next => findLast next
      findLast n

/-- Test implementation for safeFindLast -/
def test : Bool :=
  let n3 := Node.mk 3 none
  let n2 := Node.mk 2 (some n3)
  let n1 := Node.mk 1 (some n2)
  
  let test1 := safeFindLast (some n1) == 3
  let test2 := safeFindLast (some (Node.mk 42 none)) == 42
  
  -- Test empty list exception (can't directly test exceptions in Lean)
  -- We'll assume it works correctly
  
  -- Test long list
  let rec buildList (i : Nat) (current : Node) : Node :=
    if i == 0 then
      current
    else
      let next := Node.mk (i-1) (some current)
      buildList (i-1) next
  
  let longList := buildList 9 (Node.mk 9 none)
  let test4 := safeFindLast (some longList) == 9
  
  test1 && test2 && test4

/-- Convert a Node to a List Int for specification purposes -/
def toList : Option Node → List Int
  | none => []
  | some n =>
      let rec aux : Node → List Int
        | node => node.value :: match node.next with
                              | none => []
                              | some next => aux next
      aux n

/-- Precondition: The list must not be empty -/
def safeFindLastPre (node : Option Node) : Prop :=
  node ≠ none

/-- Postcondition: Returns the value of the last node in the list -/
def safeFindLastPost (node : Option Node) (result : Int) : Prop :=
  ∃ l : List Int, l ≠ [] ∧ toList node = l ∧ result = l.getLast (by
    intro h
    have : l ≠ [] := by assumption
    contradiction)

theorem safeFindLastCorrect (node : Option Node) (h : safeFindLastPre node) :
  safeFindLastPost node (safeFindLast node) := by
  sorry

end VeriBench.SafeFindLast
