-- !benchmark @start import type=solution
import Mathlib
namespace CaesarCipher
-- !benchmark @end import

-- !benchmark @start solution_aux
def isLower (c : Char) : Bool :=
  'a' ≤ c && c ≤ 'z'

def shiftChar (c : Char) (n : Int) : Char :=
  if isLower c then
    let base := c.toNat - 'a'.toNat
    let shifted := ((base + n.toNat) % 26)
    let newCode := shifted + 'a'.toNat
    Char.ofNat newCode
  else
    c

def decodeShift (s : String) : String :=
  String.mk (s.data.map (fun c => shiftChar c (-5)))

def inverse_prop (s : String) : Prop := decodeShift (encodeShift s (by simp)) = s

@[simp] theorem inverse_thm (s : String) : inverse_prop s := by
  sorry

def length_preservation_prop (s : String) : Prop := (encodeShift s (by simp)).length = s.length

@[simp] theorem length_preservation_thm (s : String) : length_preservation_prop s := by
  sorry

def decode_length_preservation_prop (s : String) : Prop := (decodeShift s).length = s.length

@[simp] theorem decode_length_preservation_thm (s : String) : decode_length_preservation_prop s := by
  sorry

def char_preservation_prop (c : Char) : Prop := ¬isLower c → shiftChar c 5 = c

@[simp] theorem char_preservation_thm (c : Char) : char_preservation_prop c := by
  sorry
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def encodeShift_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def encodeShift (s : String) (h_precond : encodeShift_precond (s)) : String :=
  -- !benchmark @start code
  String.mk (s.data.map (fun c => shiftChar c 5))
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def encodeShift_postcond (s : String) (result : String) (h_precond : encodeShift_precond (s)) : Prop :=
  -- !benchmark @start postcond
  (inverse_prop s) ∧
    (length_preservation_prop s) ∧
    (decode_length_preservation_prop s) ∧
    (∀ c, char_preservation_prop c)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem encodeShift_spec_satisfied (s : String) (h_precond : encodeShift_precond (s)) :
    encodeShift_postcond (s) (encodeShift (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof