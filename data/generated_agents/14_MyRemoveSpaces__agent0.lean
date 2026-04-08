import Lean

namespace RemoveSpaces

def pre (s : String) : Bool := true

def post (s : String) (result : String) : Bool :=
  result.length ≤ s.length ∧
  result.toList = s.toList.filter (· != ' ')

def prog (s : String) : String :=
  s.replace ' ' ""

theorem prog_correct (s : String) (h : pre s) : post s (prog s) := by
  unfold post prog
  simp [String.replace_eq_filter]
  apply And.intro
  · apply String.length_filter_le
  · rfl

def test_prog : IO Unit := do
  -- Basic test
  assert! (prog "hello world" == "helloworld")
  
  -- Edge case: empty string
  assert! (prog "" == "")
  
  -- Edge case: only spaces
  assert! (prog "   " == "")
  
  -- String with multiple spaces
  assert! (prog "a b  c   d" == "abcd")
  
  IO.println "All tests passed!"

end RemoveSpaces
