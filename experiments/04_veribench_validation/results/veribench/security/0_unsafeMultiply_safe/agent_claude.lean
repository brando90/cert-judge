import VeriBench

namespace SafeMultiply

/-- Constants defining 32-bit signed integer range -/
def INT32_MIN : Int := -2^31
def INT32_MAX : Int := 2^31 - 1

/-- Safe integer multiply with 32-bit signed overflow checks.
    Mitigation: raise on overflow rather than wrap. -/
def safeMultiply (a b : Int) : Except String Int :=
  let res := a * b
  if res < INT32_MIN || res > INT32_MAX then
    Except.error "32-bit signed overflow"
  else
    Except.ok res

/-- Precondition: Input values must be integers (always true in Lean) -/
def pre (a b : Int) : Prop := True

/-- Postcondition: Result is within 32-bit signed integer range -/
def post (a b : Int) (res : Int) : Prop :=
  INT32_MIN ≤ res ∧ res ≤ INT32_MAX

/-- Correctness theorem: If the precondition holds and the function returns a value,
    then the postcondition holds for that value -/
theorem safeMultiply_correct (a b : Int) :
  pre a b → 
  (match safeMultiply a b with
   | Except.ok res => post a b res
   | Except.error _ => True) :=
  sorry

/-- Test cases for safeMultiply -/
def testSafeMultiply : IO Bool := do
  -- Normal cases
  assert! (safeMultiply 1000 1000 == Except.ok 1000000)
  assert! (safeMultiply 1 INT32_MAX == Except.ok INT32_MAX)
  assert! (safeMultiply (-1) 1 == Except.ok (-1))

  -- Overflow cases
  assert! (safeMultiply (2^16) (2^16) == Except.error "32-bit signed overflow")
  assert! (safeMultiply (-2^16) (2^16) == Except.error "32-bit signed overflow")
  assert! (safeMultiply INT32_MAX 2 == Except.error "32-bit signed overflow")

  return true

end SafeMultiply
