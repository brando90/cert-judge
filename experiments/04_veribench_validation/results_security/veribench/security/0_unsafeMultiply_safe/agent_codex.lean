import Lean

namespace VeriBench

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

/-- Specification: The function returns the product if it's within 32-bit signed range -/
def safeMultiplySpec (a b : Int) : Except String Int :=
  let res := a * b
  if res < INT32_MIN || res > INT32_MAX then
    Except.error "32-bit signed overflow"
  else
    Except.ok res

/-- Precondition: None, the function handles all integer inputs -/
def safeMultiplyPre (_a _b : Int) : Prop := True

/-- Postcondition: Result is the product if within range, otherwise error -/
def safeMultiplyPost (a b : Int) (result : Except String Int) : Prop :=
  let product := a * b
  if product < INT32_MIN || product > INT32_MAX then
    result = Except.error "32-bit signed overflow"
  else
    result = Except.ok product

theorem safeMultiplyCorrect (a b : Int) (h : safeMultiplyPre a b) :
  safeMultiplyPost a b (safeMultiply a b) := by
  sorry

def test : IO Unit := do
  -- Normal cases
  assert! (safeMultiply 1000 1000 = Except.ok 1000000)
  assert! (safeMultiply 1 INT32_MAX = Except.ok INT32_MAX)
  assert! (safeMultiply (-1) 1 = Except.ok (-1))

  -- Overflow cases
  assert! (safeMultiply (2^16) (2^16) = Except.error "32-bit signed overflow")
  assert! (safeMultiply (-2^16) (2^16) = Except.error "32-bit signed overflow")
  assert! (safeMultiply INT32_MAX 2 = Except.error "32-bit signed overflow")

  IO.println "All tests passed!"

end VeriBench
