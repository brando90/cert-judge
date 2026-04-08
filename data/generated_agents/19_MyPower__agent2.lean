import VeriBench

namespace Power

/-- True iff both inputs are non-negative integers. -/
def pre (base exponent : Int) : Bool :=
  base ≥ 0 && exponent ≥ 0

/-- Return base^exponent for non‑negative integers base and exponent.
    Throws if the precondition is violated. -/
def prog (base exponent : Int) : Except String Int :=
  if !pre base exponent then
    Except.error s!"Require base,exponent ∈ ℕ (got base={base}, exponent={exponent})"
  else if exponent = 0 then
    Except.ok 1
  else
    let mut result := 1
    let mut count := 0
    while count < exponent do
      result := result * base
      count := count + 1
    Except.ok result

/-- Specification: power(base, exponent) = base^exponent -/
def post (base exponent result : Int) : Prop :=
  result = base ^ exponent

/-- Tests for the power function -/
def test : IO Bool := do
  -- Basic test
  if (prog 2 3).toOption.getD 0 ≠ 8 then
    return false
    
  -- Edge case test
  if (prog 0 0).toOption.getD 0 ≠ 1 then
    return false
    
  -- Negative tests (pre-violations)
  let badInputs := [(-1, 2), (2, -1)]
  for (b, e) in badInputs do
    match prog b e with
    | Except.ok _ => 
      return false
    | Except.error _ => 
      pure ()
      
  return true

/-- Theorem: prog is correct with respect to pre and post -/
theorem prog_correct (base exponent : Int) :
  pre base exponent → 
  (∃ result, prog base exponent = Except.ok result ∧ post base exponent result) :=
  sorry

end Power
