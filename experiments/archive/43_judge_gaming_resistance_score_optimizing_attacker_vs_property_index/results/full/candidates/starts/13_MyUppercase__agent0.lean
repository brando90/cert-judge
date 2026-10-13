import Mathlib
import Lean

namespace VeriBench.StringToUpper

def pre (s : String) : Bool := true

def prog (s : String) : String :=
  s.map (fun c => if c.isLower then c.toUpper else c)

end VeriBench.StringToUpper
