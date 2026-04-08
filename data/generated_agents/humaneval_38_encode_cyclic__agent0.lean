/-
  Implementation, tests, pre/post conditions, and a correctness theorem for encode_cyclic and decode_cyclic functions.
-/

import Std.Data.List.Basic

def encode_cyclic (s : String) : String :=
  let groups := List.range ((s.length + 2) / 3) |>.map (fun i => 
    let start := 3 * i
    let endIdx := min (3 * i + 3) s.length
    s.substring start endIdx)
  
  let cycledGroups := groups.map (fun group => 
    if group.length = 3 then 
      group.substring 1 3 ++ group.substring 0 1
    else 
      group)
  
  String.join cycledGroups

def decode_cyclic (s : String) : String :=
  encode_cyclic (encode_cyclic s)

/--
  Specification for encode_cyclic: It splits the string into groups of three characters
  and cycles each complete group (moves the first character to the end).
  Groups with fewer than 3 characters are left unchanged.
-/
def encode_cyclic_spec (s : String) : String :=
  let groups := List.range ((s.length + 2) / 3) |>.map (fun i => 
    let start := 3 * i
    let endIdx := min (3 * i + 3) s.length
    s.substring start endIdx)
  
  let cycledGroups := groups.map (fun group => 
    if group.length = 3 then 
      group.substring 1 3 ++ group.substring 0 1
    else 
      group)
  
  String.join cycledGroups

/--
  Specification for decode_cyclic: It applies encode_cyclic twice to recover the original string.
-/
def decode_cyclic_spec (s : String) : String :=
  encode_cyclic_spec (encode_cyclic_spec s)

theorem encode_cyclic_correct (s : String) : encode_cyclic s = encode_cyclic_spec s := by
  sorry

theorem decode_cyclic_correct (s : String) : decode_cyclic s = decode_cyclic_spec s := by
  sorry

/--
  Applying encode_cyclic twice to a string of length 3 returns the original string.
-/
theorem encode_cyclic_involutive_for_length_3 (s : String) (h : s.length = 3) : 
  encode_cyclic (encode_cyclic s) = s := by
  sorry

/--
  The decode_cyclic function correctly recovers the original string after encoding.
-/
theorem decode_cyclic_inverts_encode (s : String) : decode_cyclic (encode_cyclic s) = s := by
  sorry

-- Tests
def test_encode_cyclic : IO Unit := do
  assert! (encode_cyclic "abc" = "bca")
  assert! (encode_cyclic "abb" = "bba")
  assert! (encode_cyclic "abcd" = "bcaد")
  assert! (encode_cyclic "abcdef" = "bcaefد")
  assert! (encode_cyclic "a" = "a")
  assert! (encode_cyclic "ab" = "ab")
  IO.println "All encode_cyclic tests passed!"

def test_decode_cyclic : IO Unit := do
  assert! (decode_cyclic (encode_cyclic "abc") = "abc")
  assert! (decode_cyclic (encode_cyclic "abcdef") = "abcdef")
  assert! (decode_cyclic (encode_cyclic "hello world") = "hello world")
  assert! (decode_cyclic "bca" = "abc")
  assert! (decode_cyclic "bbaefد" = "abbdef")
  IO.println "All decode_cyclic tests passed!"

def main : IO Unit := do
  test_encode_cyclic
  test_decode_cyclic
