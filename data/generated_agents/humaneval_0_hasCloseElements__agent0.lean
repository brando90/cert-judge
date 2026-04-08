import Lean
import Mathlib.Data.List.Basic
import Mathlib.Tactic.LibrarySearch
import Mathlib.Data.Real.Basic

namespace VeriBench.HasCloseElements

/- Implementation -/
def hasCloseElements (numbers : List Float) (threshold : Float) : Bool :=
  let rec hasClosePair (i : Nat) : Bool :=
    if i >= numbers.length then
      false
    else
      let elem := numbers.get! i
      let rec checkRest (j : Nat) : Bool :=
        if j >= numbers.length then
          false
        else if i != j then
          let elem2 := numbers.get! j
          let distance := Float.abs (elem - elem2)
          if distance < threshold then
            true
          else
            checkRest (j + 1)
        else
          checkRest (j + 1)
      if checkRest 0 then
        true
      else
        hasClosePair (i + 1)
  hasClosePair 0

/- Specification -/
def hasClosePair (numbers : List Float) (threshold : Float) : Bool :=
  numbers.anyPairs (fun x y => Float.abs (x - y) < threshold)

/- Theorems -/
theorem hasCloseElements_spec (numbers : List Float) (threshold : Float) :
  hasCloseElements numbers threshold = hasClosePair numbers threshold := by
  sorry

/- Tests -/
#eval hasCloseElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] 0.3 -- true
#eval hasCloseElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] 0.05 -- false
#eval hasCloseElements [1.0, 2.0, 5.9, 4.0, 5.0] 0.95 -- true
#eval hasCloseElements [1.0, 2.0, 5.9, 4.0, 5.0] 0.8 -- false
#eval hasCloseElements [1.0, 2.0, 3.0, 4.0, 5.0, 2.0] 0.1 -- true
#eval hasCloseElements [1.1, 2.2, 3.1, 4.1, 5.1] 1.0 -- true
#eval hasCloseElements [1.1, 2.2, 3.1, 4.1, 5.1] 0.5 -- false

-- Empty list
#eval hasCloseElements [] 0.1 -- false

-- Single element
#eval hasCloseElements [1.5] 0.1 -- false

-- Two identical elements
#eval hasCloseElements [3.14, 3.14] 0.1 -- true
#eval hasCloseElements [3.14, 3.14] 0.0 -- false

-- Large threshold
#eval hasCloseElements [100.0, 200.0] 999.9 -- true

-- Very close elements
#eval hasCloseElements [1.0, 1.00000001] 0.00001 -- true

-- Not so close elements
#eval hasCloseElements [1.0, 1.0002] 0.00001 -- false

end VeriBench.HasCloseElements
