/-
# Benchmark Task: Secure Token Generation and Comparison

This module provides a pure Python implementation of functions for generating
a secure hex token and performing constant-time string comparison. The logic is
sourced from and inspired by Python's standard `secrets` library.

The primary task is to verify that these functions correctly transform a byte
string into the specified token format and that the comparison function is
logically correct.
-/

import Std

namespace VeriBenchSecretsTokens

/-
# Implementation
-/

open Std

/-- Default entropy in bytes, mirroring the Python constant. -/
def DEFAULT_ENTROPY : Nat := 32

/-- Deterministic byte used by the benchmark stubbed RNG (0xAB). -/
def stubByte : UInt8 := UInt8.ofNat 0xAB

/-- Repeat a byte `n` times. -/
def repeatByte (b : UInt8) (n : Nat) : List UInt8 :=
  List.replicate n b

/-- Return a deterministic byte string of length `n`. -/
def token_bytes (n : Nat) : List UInt8 :=
  repeatByte stubByte n

/-- Hex digit helper (lowercase). -/
def hexDigit (n : Nat) : Char :=
  if n < 10 then
    Char.ofNat (48 + n)  -- '0' = 48
  else
    Char.ofNat (87 + n)  -- 'a' = 97 = 87 + 10

/-- Convert a byte to a two-character lowercase hexadecimal string. -/
def byteToHex (b : UInt8) : String :=
  let n := b.toNat
  let hi := n / 16
  let lo := n % 16
  String.mk [hexDigit hi, hexDigit lo]

/-- Convert a byte string to lowercase hexadecimal text. -/
def bytesToHex (xs : List UInt8) : String :=
  xs.foldl (fun acc b => acc ++ byteToHex b) ""

/-- Python-like domain for the optional `nbytes` argument. -/
inductive NBytesArg
| none
| int (n : Int)
| strInput (s : String)
| floatInput (f : Float)
| objectInput
deriving Inhabited

/-- Interpret a Python-style argument into a Lean natural number. -/
def normalizeNBytes : NBytesArg → Nat
| .none => DEFAULT_ENTROPY
| .int n => Int.toNat n
| .strInput _ => DEFAULT_ENTROPY
| .floatInput _ => DEFAULT_ENTROPY
| .objectInput => DEFAULT_ENTROPY

/-- Main `token_hex` wrapper mirroring the benchmark. -/
def benchmark_token_hex (arg : NBytesArg := .none) : String :=
  bytesToHex (token_bytes (normalizeNBytes arg))

/-- Sum type for `compare_digest` arguments (str or bytes). -/
inductive TokenInput
| str (s : String)
| bytes (bs : List UInt8)
deriving Inhabited

/-- Length in "elements" (characters or bytes). -/
def TokenInput.length : TokenInput → Nat
| .str s => s.length
| .bytes bs => bs.length

/-- View the input as a list of natural numbers for comparison. -/
def TokenInput.values : TokenInput → List Nat
| .str s   => s.data.map Char.toNat
| .bytes bs => bs.map UInt8.toNat

/-- Constant-time style equality test (accumulating mismatches). -/
def compare_digest (a b : TokenInput) : Bool :=
  if _ : a.length = b.length then
    let valsA := a.values
    let valsB := b.values
    let zipped := List.zip valsA valsB
    let mismatches :=
      zipped.foldl (fun acc (xy : Nat × Nat) => acc + (if xy.fst == xy.snd then 0 else 1)) 0
    mismatches == 0
  else
    false

/-- `_validate_compare_args` analogue: ensure both args share the same constructor. -/
def sameInputFamily : TokenInput → TokenInput → Prop
| .str _,   .str _   => True
| .bytes _, .bytes _ => True
| _, _ => False

/-- Wrapper mirroring the benchmark's entry point. -/
def benchmark_compare_digest (a b : TokenInput) : Bool :=
  compare_digest a b


/-!
# Tests
-/

/-- Character is hexadecimal digit (`0-9`, `a-f`, or `A-F`). -/
def isHexDigit (c : Char) : Bool :=
  let n := c.toNat
  ((48 ≤ n) && (n ≤ 57)) ||
  ((65 ≤ n) && (n ≤ 70)) ||
  ((97 ≤ n) && (n ≤ 102))

/-- Check every character of the string with a boolean predicate. -/
def String.all (p : Char → Bool) (s : String) : Bool :=
  s.foldl (fun acc c => acc && p c) true

private def bytes (xs : List Nat) : List UInt8 :=
  xs.map (fun n => UInt8.ofNat n)

/-- expected: `token_hex(1)` has length 2 and hex digits. -/
example :
    let token := benchmark_token_hex (.int 1)
    String.length token = 2 ∧ String.all isHexDigit token := by
  native_decide

/-- expected: `token_hex(8)` has length 16 and hex digits. -/
example :
    let token := benchmark_token_hex (.int 8)
    String.length token = 16 ∧ String.all isHexDigit token := by
  native_decide

/-- expected: `token_hex(16)` has length 32. -/
example :
    String.length (benchmark_token_hex (.int 16)) = 32 := by
  native_decide

/-- expected: default `token_hex()` uses `DEFAULT_ENTROPY`. -/
example :
    String.length (benchmark_token_hex .none) = 2 * DEFAULT_ENTROPY := by
  native_decide

/-- compare_digest on equal strings. -/
example :
    benchmark_compare_digest (.str "abc") (.str "abc") = true := by
  native_decide

/-- compare_digest on equal byte arrays. -/
example :
    benchmark_compare_digest (.bytes (bytes [97, 98, 99]))
        (.bytes (bytes [97, 98, 99])) = true := by
  native_decide

/-- compare_digest detects mismatched length. -/
example :
    benchmark_compare_digest (.str "abc") (.str "abcd") = false := by
  native_decide

/-- compare_digest detects mismatched byte content. -/
example :
    benchmark_compare_digest (.bytes (bytes [97, 98, 99]))
        (.bytes (bytes [120, 121, 122])) = false := by
  native_decide

/-
Negative scenarios (TypeError / ValueError) are captured by the pre-condition
defined in the next section.
-/

/-
# Pre-condition
-/

/-- Pre-condition for `benchmark_token_hex`. -/
def Pre_token_hex : NBytesArg → Prop
| .none => True
| .int n => n ≥ 0
| .strInput _ => False
| .floatInput _ => False
| .objectInput => False

/-- Pre-condition for `benchmark_compare_digest`. -/
def Pre_compare_digest (a b : TokenInput) : Prop :=
  sameInputFamily a b

/-- negative: string argument should trigger a TypeError in Python. -/
example :
    ¬ Pre_token_hex (.strInput "8") := by
  simp [Pre_token_hex]

/-- negative: float argument should trigger a TypeError in Python. -/
example :
    ¬ Pre_token_hex (.floatInput (3.14 : Float)) := by
  simp [Pre_token_hex]

/-- negative: negative integer should trigger a ValueError in Python. -/
example :
    ¬ Pre_token_hex (.int (-1)) := by
  simp [Pre_token_hex]

/-- negative: mixed input types should trigger a TypeError in Python. -/
example :
    ¬ Pre_compare_digest (.str "abc") (.bytes (bytes [97, 98, 99])) := by
  simp [Pre_compare_digest, sameInputFamily]


/-
# Property Theorems
-/

/-- Length property for generated tokens. -/
def token_length_prop (arg : NBytesArg) : Prop :=
  let n := normalizeNBytes arg
  String.length (benchmark_token_hex arg) = 2 * n

/-- Hex-digit property for generated tokens. -/
def token_hex_digit_prop (arg : NBytesArg) : Prop :=
  String.all isHexDigit (benchmark_token_hex arg)

/-- Equality property when inputs are identical. -/
def digest_equal_prop (inp : TokenInput) : Prop :=
  benchmark_compare_digest inp inp = true

/-- Mismatch property: unequal but same-family inputs of same length return false. -/
def digest_mismatch_prop (a b : TokenInput) : Prop :=
  sameInputFamily a b →
  a.length = b.length →
  a.values ≠ b.values →
  benchmark_compare_digest a b = false

/-- Length theorem relies on the precondition. -/
theorem token_length_thm (arg : NBytesArg) (h : Pre_token_hex arg) :
    token_length_prop arg := by
  sorry

/-- Hex-digit theorem uses precondition. -/
theorem token_hex_digit_thm (arg : NBytesArg) (h : Pre_token_hex arg) :
    token_hex_digit_prop arg := by
  sorry

/-- Equality theorem for constant-time comparison. -/
theorem digest_equal_thm (inp : TokenInput) :
    digest_equal_prop inp := by
  sorry

/-- Mismatch theorem skeleton (non-trivial proof left as `sorry`). -/
theorem digest_mismatch_thm (a b : TokenInput) :
    digest_mismatch_prop a b := sorry


/-
# Post-condition
-/

/-- Combined post-condition. -/
def Post_prop (arg : NBytesArg) (a b : TokenInput) : Prop :=
  token_length_prop arg ∧
  token_hex_digit_prop arg ∧
  digest_equal_prop a ∧
  digest_mismatch_prop a b


/-
# Correctness Theorem
-/

/-- Correctness: valid inputs imply the post-condition. -/
theorem correctness_thm
    (arg : NBytesArg) (a b : TokenInput)
    (hArg : Pre_token_hex arg)
    (hAB : Pre_compare_digest a b) :
    Post_prop arg a b := by
  have _ := hAB
  refine And.intro ?length (And.intro ?hex (And.intro ?eq ?mismatch))
  · exact token_length_thm arg hArg
  · exact token_hex_digit_thm arg hArg
  · exact digest_equal_thm a
  · exact digest_mismatch_thm a b

end VeriBenchSecretsTokens
