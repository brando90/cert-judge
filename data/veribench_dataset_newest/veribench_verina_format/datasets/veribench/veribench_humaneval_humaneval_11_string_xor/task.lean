-- !benchmark @start import type=solution
import Mathlib
namespace StringXor
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def string_xor_precond (a : String) (b : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
/--
Helper function to perform XOR on two bits.
Returns '0' if the bits are equal, '1' otherwise.
-/
def xorBit (x y : Char) : Char :=
  if x == y then '0' else '1'

/--
Helper function to convert a string to a list of characters.
-/
def string_to_list (s : String) : List Char :=
  s.data

/--
Helper function to convert a list of characters back to a string.
-/
def list_to_string (l : List Char) : String :=
  ⟨l⟩
-- !benchmark @end code_aux

/--
**Implementation of `string_xor`.**

Performs bitwise XOR operation on two strings consisting only of 1s and 0s,
returning the result as a string. The operation is performed on corresponding
bits from both strings.
-/
def string_xor (a : String) (b : String) (h_precond : string_xor_precond (a) (b)) : String :=
  -- !benchmark @start code
  let xa := string_to_list a
  let xb := string_to_list b
  let pairs := List.zip xa xb
  list_to_string (pairs.map (fun (x, y) => xorBit x y))
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def string_xor_postcond (a : String) (b : String) (result : String)
    (h_precond : string_xor_precond (a) (b)) : Prop :=
  -- !benchmark @start postcond
  let empty_strings_prop : Prop := string_xor "" "" (by simp) = ""
  let length_preservation_prop (a b : String) : Prop :=
    a.length = b.length → (string_xor a b (by simp)).length = a.length
  let xor_self_prop (a : String) : Prop :=
    string_xor a a (by simp) = String.mk (List.replicate a.length '0')
  let commutativity_prop (a b : String) : Prop :=
    string_xor a b (by simp) = string_xor b a (by simp)
  let xor_zero_prop (a : String) : Prop :=
    string_xor a (String.mk (List.replicate a.length '0')) (by simp) = a
  (empty_strings_prop) ∧
    (length_preservation_prop a b) ∧
    (xor_self_prop a) ∧
    (commutativity_prop a b) ∧
    (xor_zero_prop a)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Empty strings property**: XOR of empty strings is empty. -/
def empty_strings_prop : Prop := string_xor "" "" (by simp) = ""

/-- **Empty strings theorem**: XOR of empty strings is empty. -/
@[simp] theorem empty_strings_thm : empty_strings_prop := by
  sorry

/-- **Length preservation property**: Result has same length as inputs (when equal length). -/
def length_preservation_prop (a b : String) : Prop :=
  a.length = b.length → (string_xor a b (by simp)).length = a.length

/-- **Length preservation theorem**: Result has same length as inputs (when equal length). -/
@[simp] theorem length_preservation_thm (a b : String) : length_preservation_prop a b := by
  sorry

/-- **XOR self property**: XORing a string with itself gives all zeros. -/
def xor_self_prop (a : String) : Prop :=
  string_xor a a (by simp) = String.mk (List.replicate a.length '0')

/-- **XOR self theorem**: XORing a string with itself gives all zeros. -/
@[simp] theorem xor_self_thm (a : String) : xor_self_prop a := by
  sorry

/-- **Commutativity property**: XOR is commutative. -/
def commutativity_prop (a b : String) : Prop :=
  string_xor a b (by simp) = string_xor b a (by simp)

/-- **Commutativity theorem**: XOR is commutative. -/
@[simp] theorem commutativity_thm (a b : String) : commutativity_prop a b := by
  sorry

/-- **Bit operation property**: XOR with zeros gives original string. -/
def xor_zero_prop (a : String) : Prop :=
  string_xor a (String.mk (List.replicate a.length '0')) (by simp) = a

/-- **Bit operation theorem**: XOR with zeros gives original string. -/
@[simp] theorem xor_zero_thm (a : String) : xor_zero_prop a := by
  sorry
-- !benchmark @end proof_aux

theorem string_xor_spec_satisfied (a : String) (b : String) (h_precond : string_xor_precond (a) (b)) :
    string_xor_postcond (a) (b) (string_xor (a) (b) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof