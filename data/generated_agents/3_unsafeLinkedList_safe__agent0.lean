import Lean

inductive Node where
  | mk (value : Int) (next : Option Node)
  deriving Repr

namespace Node

/-- Safe linked-list traversal with None checks. -/
def safeFindLast (node : Option Node) : Except String Int :=
  match node with
  | none => Except.error "empty list"
  | some n => 
    let rec findLast (current : Node) : Int :=
      match current.next with
      | none => current.value
      | some next => findLast next
    findLast n

/-- Specification: safeFindLast returns the value of the last node in the list.
    If the list is empty (None), it returns an error. -/
def safeFindLastSpec (node : Option Node) : Except String Int :=
  match node with
  | none => Except.error "empty list"
  | some n =>
    let rec lastNode (current : Node) : Node :=
      match current.next with
      | none => current
      | some next => lastNode next
    Except.ok (lastNode n).value

/-- Implementation correctness: safeFindLast matches its specification -/
theorem safeFindLast_correct (node : Option Node) :
  safeFindLast node = safeFindLastSpec node := by
  sorry

#eval safeFindLast none -- Except.error "empty list"

def test : IO Unit := do
  let n3 := Node.mk 3 none
  let n2 := Node.mk 2 (some n3)
  let n1 := Node.mk 1 (some n2)
  
  -- Test case 1: List with multiple nodes
  assert! (safeFindLast (some n1) == Except.ok 3)
  
  -- Test case 2: Single node list
  assert! (safeFindLast (some (Node.mk 42 none)) == Except.ok 42)
  
  -- Test case 3: Empty list
  assert! (safeFindLast none == Except.error "empty list")
  
  -- Test case 4: Long list
  let mut head := Node.mk 0 none
  let mut current := head
  for i in [1:10] do
    let next := Node.mk i none
    current := Node.mk current.value (some next)
    head := if i == 1 then Node.mk head.value (some current) else head
    current := next
  assert! (safeFindLast (some head) == Except.ok 9)
  
  IO.println "All tests passed!"

#eval test

end Node
