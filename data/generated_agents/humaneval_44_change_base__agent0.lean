```lean
import Std

/-- Change numerical base of input number x to base.
    return string representation after the conversion.
    base numbers are less than 10. -/
def changeBase (x : Int) (base : Int) : String :=
  if x = 0 then "0" else
    let rec aux (x : Int) (acc : String) : String :=
      if x ≤ 0 then acc
      else aux (x / base) (toString (x % base) ++ acc)
    aux x ""

/-- Tests for changeBase function -/
def changeBaseTests : IO Unit := do
  assert! (changeBase 8 3 = "22")
  assert! (changeBase 9 3 = "100")
  assert! (changeBase 234 2 = "11101010")
  assert! (changeBase 16 2 = "10000")
  assert! (changeBase 8 2 = "1000")
  assert! (changeBase 7 2 = "111")
  assert! (changeBase 0 2 = "0") -- Edge case for x = 0
  for x in [2:8] do
    assert! (changeBase x (x + 1) = toString x)
  IO.println "All tests passed!"

/-- Precondition for changeBase: base must be greater than 1 and less than 10 -/
def changeBasePre (x : Int) (base : Int) : Prop :=
  x ≥ 0 ∧ base > 1 ∧ base < 10

/-- Postcondition for changeBase: the result is a valid string representation of x in the given base -/
def changeBasePost (x : Int) (base : Int) (result : String) : Prop :=
  if x = 0 then result = "0" else
    (∀ (i : Nat), i < result.length → 
      let digit := result.get ⟨i, by sorry⟩
      0 ≤ digit.toNat - '0'.toNat ∧ digit.toNat - '0'.toNat < base) ∧
    (let value := result.foldl (fun acc c => acc * base + (c.toNat - '0'.toNat)) 0
     value = x)

/-- Theorem stating that changeBase satisfies its specification -/
theorem changeBaseCorrect (x : Int) (base : Int) 
    (h : changeBasePre x base) : 
    changeBasePost x base (changeBase x base) := by
  sorry
```
