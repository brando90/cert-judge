```lean
import Std.Data.List.Basic
import Std.Data.String.Basic

/-- 
  Input are two strings a and b consisting only of 1s and 0s.
  Perform binary XOR on these inputs and return result also as a string.
-/
def string_xor (a : String) (b : String) : String :=
  let rec xor (i j : Char) : Char :=
    if i == j then '0' else '1'
  
  let len := min a.length b.length
  let result := List.map₂ xor (a.toList.take len) (b.toList.take len)
  String.mk result

/-- Tests for string_xor -/
def string_xor_tests : IO Unit := do
  assert! (string_xor "111000" "101010" == "010010")
  assert! (string_xor "1" "1" == "0")
  assert! (string_xor "0101" "0000" == "0101")
  IO.println "All tests passed!"

/-- Check if a string consists only of '0' and '1' characters -/
def isBinaryString (s : String) : Bool :=
  s.all (fun c => c == '0' || c == '1')

/-- Precondition: Both input strings must consist only of '0' and '1' characters -/
def string_xor_pre (a b : String) : Prop :=
  isBinaryString a ∧ isBinaryString b

/-- Postcondition: The output string must also consist only of '0' and '1' characters,
    and each character is the XOR of the corresponding characters in the input strings -/
def string_xor_post (a b : String) (result : String) : Prop :=
  isBinaryString result ∧
  result.length = min a.length b.length ∧
  ∀ (i : Nat), i < result.length → 
    let a_char := a.get ⟨i, by sorry⟩
    let b_char := b.get ⟨i, by sorry⟩
    let r_char := result.get ⟨i, by sorry⟩
    r_char = (if a_char == b_char then '0' else '1')

/-- Theorem: string_xor satisfies its specification -/
theorem string_xor_correct (a b : String) :
  string_xor_pre a b → string_xor_post a b (string_xor a b) := by
  sorry
```
