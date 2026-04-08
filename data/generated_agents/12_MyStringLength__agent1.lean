import VeriBench

namespace StringLength

def pre (s : String) : Bool := true

def post (s : String) (r : Nat) : Bool :=
  r = s.length

def prog (s : String) : Nat :=
  s.length

theorem prog_correct (s : String) (h : pre s) : post s (prog s) := by
  simp [post, prog]
  sorry

def test : IO Unit := do
  -- Basic unit test
  assert! (prog "hello" == 5)

  -- Edge unit test
  assert! (prog "" == 0)

  IO.println "All tests passed."

end StringLength
