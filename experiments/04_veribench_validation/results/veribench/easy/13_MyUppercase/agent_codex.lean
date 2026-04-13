import Lean
import Lean.Data.String

namespace VeriBench.StringToUpper

def pre (s : String) : Bool := true

def prog (s : String) : String :=
  s.map (fun c => if c.isLower then c.toUpper else c)

def post (s : String) (result : String) : Bool :=
  result.length = s.length &&
  ∀ i, i < s.length → 
    let c := s.get i
    let r := result.get i
    if c.isLower then r = c.toUpper else r = c

theorem prog_spec (s : String) :
  post s (prog s) := by
  sorry

-- Tests
def test1 : prog "hello" = "HELLO" := rfl
def test2 : prog "" = "" := rfl
def test3 : prog "Hello123" = "HELLO123" := rfl
def test4 : prog "ALREADY UPPER" = "ALREADY UPPER" := rfl
def test5 : prog "Mixed Case 123!@#" = "MIXED CASE 123!@#" := rfl

end VeriBench.StringToUpper
