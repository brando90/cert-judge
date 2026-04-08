```lean
import Std.Data.String.Basic
import Std.Data.List.Basic

/--
  `string_xor a b` performs binary XOR on two strings `a` and `b` consisting only of 1s and 0s,
  and returns the result as a string.
  
  For example, `string_xor "010" "110" = "100"`.
-/
def string_xor (a : String) (b : String) : String :=
  let len := min a.length b.length
  let chars := List.range len |>.map (fun i =>
    let aChar := a.get ⟨i, by sorry⟩
    let bChar := b.get ⟨i, by sorry⟩
    if aChar == bChar then '0' else '1')
  String.mk chars

/--
  Tests for the `string_xor` function.
-/
def string_xor_tests : IO Unit := do
  assert! (string_xor "111000" "101010" == "010010")
  assert! (string_xor "1" "1" == "0")
  assert! (string_xor "0101" "0000" == "0101")
  IO.println "All tests passed!"

/--
  Predicate indicating that a string consists only of 0s and 1s.
-/
def isBinaryString (s : String) : Prop :=
  ∀ i, i < s.length → (s.get ⟨i, by sorry⟩ = '0' ∨ s.get ⟨i, by sorry⟩ = '1')

/--
  Specification for the `string_xor` function.
-/
theorem string_xor_correct (a b : String) 
  (ha : isBinaryString a) (hb : isBinaryString b) : 
  isBinaryString (string_xor a b) ∧
  ∀ i, i < (min a.length b.length) → 
    (string_xor a b).get ⟨i, by sorry⟩ = 
      if a.get ⟨i, by sorry⟩ == b.get ⟨i, by sorry⟩ then '0' else '1' :=
  sorry
```
