-- !benchmark @start import type=solution
import Mathlib
namespace SecretsTokens
-- !benchmark @end import

-- !benchmark @start solution_aux
open Std
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def token_hex_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux
def DEFAULT_ENTROPY : Nat := 32
def stubByte : UInt8 := 0xAB

/-- Deterministic token bytes generation -/
def token_bytes (n : Nat) : List UInt8 :=
  List.replicate n stubByte

/-- Hex helpers -/
def hexDigit (n : Nat) : Char :=
  if n < 10 then Char.ofNat (48 + n) else Char.ofNat (87 + n)

def byteToHex (b : UInt8) : String :=
  let n := b.toNat
  String.mk [hexDigit (n / 16), hexDigit (n % 16)]

def bytesToHex (xs : List UInt8) : String :=
  xs.foldl (fun acc b => acc ++ byteToHex b) ""
-- !benchmark @end code_aux


def token_hex (n : Nat) (h_precond : token_hex_precond (n)) : String :=
  -- !benchmark @start code
  bytesToHex (token_bytes n)
  -- !benchmark @end code


-- !benchmark @start postcond_aux
/-- Property: Token length is 2*n -/
def length_prop (n : Nat) : Prop :=
  (token_hex n (by simp)).length = 2 * n

theorem length_thm (n : Nat) : length_prop n := by
  sorry

-- ==========================================
-- Comparison Logic
-- ==========================================

inductive TokenInput
| str (s : String)
| bytes (bs : List UInt8)
deriving BEq

def toBytes (t : TokenInput) : List UInt8 :=
  match t with
  | .str s => s.toUTF8.data.toList
  | .bytes bs => bs

/--
Functional Compare:
Standard equality check (short-circuiting allowed in spec, but result is boolean eq).
-/
def compare_digest_func (a b : TokenInput) : Bool :=
  a == b

/-- Property: Compare is reflexive -/
def refl_prop (t : TokenInput) : Prop :=
  compare_digest_func t t = true

theorem refl_thm (t : TokenInput) : refl_prop t := by
  sorry
-- !benchmark @end postcond_aux


@[reducible, simp]
def token_hex_postcond (n : Nat) (result : String) (h_precond : token_hex_precond (n)) :=
  -- !benchmark @start postcond
  length_prop n
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

-- !benchmark @end proof_aux


theorem token_hex_spec_satisfied (n : Nat) (h_precond : token_hex_precond (n)) :
    token_hex_postcond (n) (token_hex (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof