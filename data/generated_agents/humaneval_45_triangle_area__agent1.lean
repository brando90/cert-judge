import VeriBench.Common

/--
Given length of a side and high return area for a triangle.
-/
def triangleArea (a h : Float) : Float :=
  a * h / 2.0

/--
Predicate specifying the correctness of the `triangleArea` function.
-/
def triangleAreaSpec (a h : Float) (result : Float) : Prop :=
  result = a * h / 2.0

/--
Theorem stating that `triangleArea` satisfies its specification.
-/
theorem triangleArea_correct (a h : Float) : 
  triangleAreaSpec a h (triangleArea a h) := by
  unfold triangleAreaSpec
  unfold triangleArea
  simp
  sorry

/--
Test cases for the `triangleArea` function.
-/
def triangleAreaTests : IO Unit := do
  assertEq (triangleArea 5 3) 7.5
  assertEq (triangleArea 2 2) 2.0
  assertEq (triangleArea 10 8) 40.0

#eval triangleAreaTests
