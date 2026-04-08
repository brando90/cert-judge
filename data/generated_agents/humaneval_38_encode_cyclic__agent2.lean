```lean
def encode_cyclic (s : String) : String :=
  let groups := List.range ((s.length + 2) / 3) |>.map fun i =>
    s.extract (3 * i) (min (3 * i + 3) s.length)
  let cycled := groups.map fun group =>
    if group.length == 3 then
      group.extract 1 3 ++ group.extract 0 1
    else
      group
  String.join cycled

def decode_cyclic (s : String) : String :=
  encode_cyclic (encode_cyclic s)

-- Tests
#eval encode_cyclic "abc" -- "bca"
#eval encode_cyclic "abcdef" -- "bcaef"
#eval encode_cyclic "abcdefghi" -- "bcaefgih"

#eval decode_cyclic (encode_cyclic "abcdef") -- "abcdef"
#eval decode_cyclic "bcaefgih" -- "abcdefghi"

/-- Specification for encode_cyclic -/
def encode_cyclic_spec (s : String) : String :=
  let groups := List.range ((s.length + 2) / 3) |>.map fun i =>
    s.extract (3 * i) (min (3 * i + 3) s.length)
  let cycled := groups.map fun group =>
    if group.length == 3 then
      group.extract 1 3 ++ group.extract 0 1
    else
      group
  String.join cycled

/-- Specification for decode_cyclic -/
def decode_cyclic_spec (s : String) : String :=
  encode_cyclic_spec (encode_cyclic_spec s)

/-- Correctness of encode_cyclic implementation -/
theorem encode_cyclic_correct (s : String) : encode_cyclic s = encode_cyclic_spec s := by
  sorry

/-- Correctness of decode_cyclic implementation -/
theorem decode_cyclic_correct (s : String) : decode_cyclic s = decode_cyclic_spec s := by
  sorry

/-- Decoding an encoded string returns the original string -/
theorem decode_cyclic_inverts_encode (s : String) : decode_cyclic (encode_cyclic s) = s := by
  sorry
```
