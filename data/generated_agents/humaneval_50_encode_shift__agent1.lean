/-
  File: humaneval_50_encode_shift.lean
  HumanEval problem HumanEval/50
-/

def encode_shift (s : String) : String :=
  let chars := s.toList
  let shifted := chars.map (fun ch =>
    let code := ch.toNat
    let aCode := 'a'.toNat
    let newCode := ((code + 5 - aCode) % 26) + aCode
    Char.ofNat newCode
  )
  String.mk shifted

def decode_shift (s : String) : String :=
  let chars := s.toList
  let shifted := chars.map (fun ch =>
    let code := ch.toNat
    let aCode := 'a'.toNat
    let newCode := ((code - 5 - aCode) % 26 + 26) % 26 + aCode
    Char.ofNat newCode
  )
  String.mk shifted

/--
  Specification: decode_shift takes as input string encoded with encode_shift function and returns the decoded string.
-/

def decode_shift_spec (s : String) : String :=
  let isLowerAlpha (c : Char) := 'a' ≤ c && c ≤ 'z'
  if s.toList.all isLowerAlpha then
    decode_shift s
  else
    ""

-- Test cases
#eval encode_shift "abcde" -- Should be "fghij"
#eval decode_shift "fghij" -- Should be "abcde"
#eval encode_shift "xyz" -- Should be "cde"
#eval decode_shift "cde" -- Should be "xyz"

-- Verify that decode_shift undoes encode_shift
theorem decode_shift_encode_shift_identity (s : String) :
  (s.toList.all (fun c => 'a' ≤ c && c ≤ 'z')) →
  decode_shift (encode_shift s) = s := sorry

-- Verify that encode_shift undoes decode_shift
theorem encode_shift_decode_shift_identity (s : String) :
  (s.toList.all (fun c => 'a' ≤ c && c ≤ 'z')) →
  encode_shift (decode_shift s) = s := sorry

-- Correctness theorem
theorem decode_shift_spec_correct (s : String) :
  decode_shift_spec s = if s.toList.all (fun c => 'a' ≤ c && c ≤ 'z') then
                          decode_shift s
                        else
                          "" := sorry
