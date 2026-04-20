-- !benchmark @start import type=solution
import Mathlib
namespace CyclicEncoding
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def encode_cyclic_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux
partial def splitIntoGroups (chars : List Char) (n : Nat) : List (List Char) :=
  match chars with
  | [] => []
  | _ =>
    let group := chars.take n
    group :: splitIntoGroups (chars.drop n) n

def cycleGroup (group : List Char) : List Char :=
  if group.length = 3 then
    group.drop 1 ++ group.take 1
  else
    group
-- !benchmark @end code_aux


def encode_cyclic (s : String) (h_precond : encode_cyclic_precond (s)) : String :=
  -- !benchmark @start code
  let groups := splitIntoGroups s.data 3
  let cycled := groups.map cycleGroup
  String.mk (List.flatten cycled)
  -- !benchmark @end code


-- !benchmark @start postcond_aux
def decode_cyclic (s : String) : String :=
  encode_cyclic (encode_cyclic s (by simp)) (by simp)

def length_preservation_prop (s : String) : Prop :=
  (encode_cyclic s (by simp)).length = s.length

@[simp] theorem length_preservation_thm (s : String) : length_preservation_prop s := by
  sorry

def decoding_correctness_prop (s : String) : Prop :=
  decode_cyclic (encode_cyclic s (by simp)) = s

@[simp] theorem decoding_correctness_thm (s : String) : decoding_correctness_prop s := by
  sorry

def empty_string_prop : Prop :=
  encode_cyclic "" (by simp) = ""

@[simp] theorem empty_string_thm : empty_string_prop := by
  sorry

def group_preservation_prop (s : String) : Prop :=
  (splitIntoGroups s.data 3).length = (splitIntoGroups (encode_cyclic s (by simp)).data 3).length

@[simp] theorem group_preservation_thm (s : String) : group_preservation_prop s := by
  sorry
-- !benchmark @end postcond_aux


@[reducible, simp]
def encode_cyclic_postcond (s : String) (result : String) (h_precond : encode_cyclic_precond (s)) :=
  -- !benchmark @start postcond
  (length_preservation_prop s) ∧
    (decoding_correctness_prop s) ∧
    (empty_string_prop) ∧
    (group_preservation_prop s)
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

-- !benchmark @end proof_aux


theorem encode_cyclic_spec_satisfied (s : String) (h_precond : encode_cyclic_precond (s)) :
    encode_cyclic_postcond (s) (encode_cyclic (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof