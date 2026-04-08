import Lean

namespace VeriBench.SafeFindLast

inductive Node where
  | mk : Int → Option Node → Node
  deriving Repr

def Node.value : Node → Int
  | mk v _ => v

def Node.next : Node → Option Node
  | mk _ n => n

/-- Safe linked-list traversal with None checks. -/
def safe_find_last (node : Option Node) : Int :=
  match node with
  | none => panic! "empty list"
  | some n =>
    let rec traverse (current : Node) : Int :=
      match current.next with
      | none => current.value
      | some next => traverse next
    traverse n

/-- The safe_find_last function returns the value of the last node in the list. -/
theorem safe_find_last_correct (node : Option Node) :
  match node with
  | none => True -- error case
  | some n => 
    let rec last (n : Node) : Int :=
      match n.next with
      | none => n.value
      | some next => last next
    safe_find_last node = last n
  := by sorry

/-- Tests for safe_find_last -/
def test_safe_find_last : IO Bool := do
  let n3 := Node.mk 3 none
  let n2 := Node.mk 2 (some n3)
  let n1 := Node.mk 1 (some n2)
  
  assert! (safe_find_last (some n1) == 3)
  
  assert! (safe_find_last (some (Node.mk 42 none)) == 42)
  
  -- Test empty list (should panic)
  let caught ← IO.catchExceptions (do
    let _ := safe_find_last none
    pure false) (fun _ => pure true)
  assert! caught
  
  -- Test long list
  let head := Node.mk 0 none
  let mut cur := head
  for i in [1:10] do
    let nxt := Node.mk i none
    let cur' := Node.mk cur.value (some nxt)
    cur := nxt
  
  assert! (safe_find_last (some head) == 9)
  
  return true

end VeriBench.SafeFindLast
