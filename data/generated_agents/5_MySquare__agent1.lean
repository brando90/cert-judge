```lean
import VeriBench

namespace Square

/-- True iff the input is a non-negative integer. -/
def pre (n : Int) : Bool :=
  n ≥ 0

/-- Return n² for non‑negative integer n. -/
def prog (n : Int) : Option Int :=
  if pre n then
    some (n * n)
  else
    none

/-- The square of a natural number is non-negative. -/
def post (n : Int) (result : Int) : Bool :=
  result ≥ 0

theorem prog_correct (n : Int) : 
  pre n → match prog n with
          | some result => post n result ∧ result = n * n
          | none => False
  := by sorry

-- Tests
def tests : IO Unit := do
  -- Basic test
  assertEq (prog 3) (some 9) "Basic test failed"
  
  -- Edge cases
  assertEq (prog 0) (some 0) "Edge case 0 failed"
  assertEq (prog 1) (some 1) "Edge case 1 failed"
  
  -- Negative tests (pre-condition violations)
  assertEq (prog (-1)) none "Negative input test failed"
  
  IO.println "All tests passed."

end Square
```
