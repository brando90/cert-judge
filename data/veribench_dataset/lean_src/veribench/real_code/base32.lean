/-
# Benchmark Task: Base32 Encoding and Decoding

This module provides a pure Lean implementation of Base32 encoding and
decoding, sourced from Python's standard `base64` library.

The primary functions to verify are `benchmark_b32encode` and
`benchmark_b32decode`. The key property to prove is round-trip correctness:
`decode (encode s) = s` for supported byte strings.
-/

import Std

namespace VeriBenchBase32

/-
# Implementation
-/

open Std

def base32Alphabet : Array Char :=
  #['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P',
    'Q','R','S','T','U','V','W','X','Y','Z','2','3','4','5','6','7']

def alphabetList : List Char := base32Alphabet.toList

def pow2 (n : Nat) : Nat :=
  Nat.pow 2 n

/-- Find the index of a character in the Base32 alphabet (case-insensitive). -/
def indexInAlphabet? (target : Char) : Option Nat :=
  let upper := target.toUpper
  let rec loop : List Char → Nat → Option Nat
    | [], _ => none
    | h :: t, idx =>
        if h = upper then
          some idx
        else
          loop t (idx + 1)
  loop alphabetList 0

/-- Encode a chunk of up to five bytes into eight Base32 characters (with padding). -/
def encodeChunk (chunk : List UInt8) : List Char :=
  let len := chunk.length
  let padded := chunk ++ List.replicate (5 - len) 0
  let bits : Nat := padded.foldl (fun acc b => acc * 256 + b.toNat) 0
  let chars :=
    (List.range 8).map fun (i : Nat) =>
      let shift := 35 - 5 * i
      let idx := (bits / pow2 shift) % 32
      base32Alphabet[idx]!
  match len with
  | 1 => chars.take 2 ++ List.replicate 6 '='
  | 2 => chars.take 4 ++ List.replicate 4 '='
  | 3 => chars.take 5 ++ List.replicate 3 '='
  | 4 => chars.take 7 ++ List.replicate 1 '='
  | _ => chars

/-- Encode an arbitrary byte string into Base32. -/
partial def b32encodeBytes : List UInt8 → List Char
  | [] => []
  | data =>
      let chunk := data.take 5
      let rest := data.drop 5
      encodeChunk chunk ++ b32encodeBytes rest

/-- Map padding count to the number of payload bytes to keep. -/
def validBytesForPad : Nat → Option Nat
  | 0 => some 5
  | 1 => some 4
  | 3 => some 3
  | 4 => some 2
  | 6 => some 1
  | _ => none

/-- Decode a chunk of eight Base32 characters into up to five bytes. -/
def decodeChunk (chunk : List Char) : Option (List UInt8) := do
  guard (chunk.length = 8)
  let pad := chunk.count '='
  let payload := chunk.map fun c => if c = '=' then 'A' else c
  let values ← payload.mapM indexInAlphabet?
  let bits : Nat := values.foldl (fun acc v => acc * 32 + v) 0
  let bytes :=
    (List.range 5).map fun (i : Nat) =>
      let shift := 32 - 8 * i
      let value := (bits / pow2 shift) % 256
      UInt8.ofNat value
  let keep ← validBytesForPad pad
  pure (bytes.take keep)

/-- Decode an entire Base32 string into bytes. -/
partial def b32decodeChars : List Char → Option (List UInt8)
  | [] => some []
  | chars =>
      let chunk := chars.take 8
      if chunk.length < 8 then
        none
      else
        let rest := chars.drop 8
        do
          let decoded ← decodeChunk chunk
          let tail ← b32decodeChars rest
          pure (decoded ++ tail)

/-- Apply optional case folding and `map01` translation. -/
def transformInput (s : String) (casefold : Bool) (map01? : Option Char) : String :=
  let folded :=
    if casefold then
      String.mk (s.data.map Char.toUpper)
    else
      s
  match map01? with
  | none => folded
  | some c =>
      String.mk <|
        folded.data.map fun ch =>
          if ch = '0' then 'O'
          else if ch = '1' then c
          else ch

/-- Base32 encoder mirroring the Python benchmark. -/
def benchmark_b32encode (data : List UInt8) : String :=
  String.mk (b32encodeBytes data)

/-- Base32 decoder mirroring the Python benchmark. -/
def benchmark_b32decode (s : String) (casefold : Bool := false) (map01? : Option Char := none) : List UInt8 :=
  let transformed := transformInput s casefold map01?
  if transformed.length % 8 ≠ 0 then
    []
  else
    match b32decodeChars transformed.data with
    | some bytes => bytes
    | none => []

/--
Predicate for valid transformed Base32 characters (alphabet or padding).
-/
def isValidChar (c : Char) : Bool :=
  if c = '=' then
    true
  else
    alphabetList.contains c

def validTransformed (t : String) : Bool :=
  t.data.all isValidChar


/-
# Tests
-/

/-- Helper to build byte lists from natural numbers. -/
def bytes (ns : List Nat) : List UInt8 :=
  ns.map fun n => UInt8.ofNat n

/-- Basic encode vectors (from CPython tests). -/
example : benchmark_b32encode (bytes []) = "" := by native_decide
example : benchmark_b32encode (bytes [0]) = "AA======" := by native_decide
example : benchmark_b32encode (bytes [97]) = "ME======" := by native_decide
example : benchmark_b32encode (bytes [97, 98]) = "MFRA====" := by native_decide
example : benchmark_b32encode (bytes [97, 98, 99]) = "MFRGG===" := by native_decide
example : benchmark_b32encode (bytes [97, 98, 99, 100]) = "MFRGGZA=" := by native_decide
example : benchmark_b32encode (bytes [97, 98, 99, 100, 101]) = "MFRGGZDF" := by native_decide

/-- Decode vectors (bytes and ASCII inputs). -/
example : benchmark_b32decode "" = bytes [] := by native_decide
example : benchmark_b32decode "AA======" = bytes [0] := by native_decide
example : benchmark_b32decode "ME======" = bytes [97] := by native_decide
example : benchmark_b32decode "MFRA====" = bytes [97, 98] := by native_decide
example : benchmark_b32decode "MFRGG===" = bytes [97, 98, 99] := by native_decide
example : benchmark_b32decode "MFRGGZA=" = bytes [97, 98, 99, 100] := by native_decide
example : benchmark_b32decode "MFRGGZDF" = bytes [97, 98, 99, 100, 101] := by native_decide
example : benchmark_b32decode "MFRGG===" true = bytes [97, 98, 99] := by native_decide

/-- Casefold allows lowercase input. -/
example : benchmark_b32decode "me======" true = bytes [97] := by native_decide
example : benchmark_b32decode "mfrgg===" true = bytes [97, 98, 99] := by native_decide

/-- Mapping `map01` enables decoding strings containing `0`/`1`. -/
example :
    benchmark_b32decode "M1023456" false (some 'L')
      = bytes [98, 221, 173, 243, 190] := by native_decide

/-- Round-trip property on representative inputs. -/
example :
    benchmark_b32decode (benchmark_b32encode (bytes [])) = bytes [] ∧
    benchmark_b32decode (benchmark_b32encode (bytes [1, 2, 3])) = bytes [1, 2, 3] ∧
    benchmark_b32decode (benchmark_b32encode (bytes [0, 1, 2, 3, 4, 5])) = bytes [0, 1, 2, 3, 4, 5] := by
  native_decide


/-
# Pre-condition
-/

def Pre_encode (data : List UInt8) : Prop := True

def Pre_decode (s : String) (casefold : Bool := false) (map01? : Option Char := none) : Prop :=
  let transformed := transformInput s casefold map01?
  transformed.length % 8 = 0 ∧ validTransformed transformed = true

/-- Negative tests: strings that violate the precondition. -/
example : ¬ Pre_decode "M1023456" := by
  intro h
  rcases h with ⟨_, hValid⟩
  have hFalse : validTransformed (transformInput "M1023456" false none) = false := by decide
  exact Bool.noConfusion (Eq.trans hFalse.symm hValid)

example : ¬ Pre_decode "abc" := by
  intro h
  rcases h with ⟨hLen, _⟩
  have : (transformInput "abc" false none).length % 8 ≠ 0 := by decide
  exact this hLen

example : ¬ Pre_decode "AAAAAA" := by
  intro h
  rcases h with ⟨hLen, _⟩
  have : (transformInput "AAAAAA" false none).length % 8 ≠ 0 := by decide
  exact this hLen

/-- Map01 enables the precondition for strings containing `0`/`1`. -/
example : Pre_decode "M1023456" false (some 'L') := by
  constructor
  · decide
  · have : validTransformed (transformInput "M1023456" false (some 'L')) = true := by decide
    simpa [Pre_decode]


/-
# Property Theorems
-/

def round_trip_prop (data : List UInt8) : Prop :=
  benchmark_b32decode (benchmark_b32encode data) = data

def uppercase_prop (s : String) : Prop :=
  benchmark_b32decode s true = benchmark_b32decode (String.mk (s.data.map Char.toUpper)) true

theorem round_trip_thm (data : List UInt8) :
    round_trip_prop data := by
  sorry

theorem uppercase_thm (s : String) :
    uppercase_prop s := by
  sorry


/-
# Post-condition
-/

def Post (data : List UInt8) (s : String) : Prop :=
  round_trip_prop data ∧ uppercase_prop s


/-
# Correctness Theorem
-/

theorem correctness_thm (data : List UInt8) (s : String)
    (hEncode : Pre_encode data) (hDecode : Pre_decode s true) :
    Post data s := by
  have _ := hEncode
  have _ := hDecode
  exact And.intro (round_trip_thm data) (uppercase_thm s)

end VeriBenchBase32
