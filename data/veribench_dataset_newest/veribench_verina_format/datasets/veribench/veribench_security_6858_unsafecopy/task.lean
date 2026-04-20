-- !benchmark @start import type=solution
import Mathlib
namespace BufferOverflow
-- !benchmark @end import

-- !benchmark @start solution_aux
-- (no additional solution-level auxiliaries)
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- (no precondition auxiliaries)
-- !benchmark @end precond_aux

@[reducible, simp]
def unsafeCopy_precond (dst : List UInt8) (src : List UInt8) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- (no code auxiliaries)
-- !benchmark @end code_aux

def unsafeCopy (dst : List UInt8) (src : List UInt8)
    (h_precond : unsafeCopy_precond (dst) (src)) : Option (List UInt8) :=
  -- !benchmark @start code
  let n := dst.length
  -- fold over enumerated bytes with their indices
  src.zipIdx.foldl
      (fun o (b, i) =>
        o.bind fun acc =>
          if _ : i < n then
            some (acc.set i b)
          else
            none)
      (some dst)
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- (no postcondition auxiliaries)
-- !benchmark @end postcond_aux

@[reducible, simp]
def unsafeCopy_postcond (dst : List UInt8) (src : List UInt8) (result : Option (List UInt8))
    (h_precond : unsafeCopy_precond (dst) (src)) : Prop :=
  -- !benchmark @start postcond
  (dst.length ≥ src.length → ∃ r, unsafeCopy (dst) (src) h_precond = some r) ∧
    (dst.length < src.length → unsafeCopy (dst) (src) h_precond = none) ∧
    (∀ r, unsafeCopy (dst) (src) h_precond = some r → r.length = dst.length) ∧
    (∃ r, unsafeCopy (dst) [] (by simp) = some r)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Safe copy property**: When destination is large enough, copy succeeds. -/
def safe_copy_prop (dst src : List UInt8) : Prop :=
  dst.length ≥ src.length → ∃ result, unsafeCopy dst src (by simp) = some result

/-- **Safe copy theorem**: When destination is large enough, copy succeeds. -/
theorem safe_copy_thm (dst src : List UInt8) : safe_copy_prop dst src := by
  sorry

/-- **Overflow detection property**: When source is larger, copy fails. -/
def overflow_detection_prop (dst src : List UInt8) : Prop :=
  dst.length < src.length → unsafeCopy dst src (by simp) = none

/-- **Overflow detection theorem**: When source is larger, copy fails. -/
theorem overflow_detection_thm (dst src : List UInt8) : overflow_detection_prop dst src := by
  sorry

/-- **Length preservation property**: Successful copy preserves destination length. -/
def length_preservation_prop (dst src : List UInt8) : Prop :=
  ∀ result, unsafeCopy dst src (by simp) = some result → result.length = dst.length

/-- **Length preservation theorem**: Successful copy preserves destination length. -/
theorem length_preservation_thm (dst src : List UInt8) : length_preservation_prop dst src := by
  sorry

/-- **Empty source property**: Copying empty source succeeds. -/
def empty_source_prop (dst : List UInt8) : Prop :=
  ∃ result, unsafeCopy dst [] (by simp) = some result

/-- **Empty source theorem**: Copying empty source succeeds. -/
theorem empty_source_thm (dst : List UInt8) : empty_source_prop dst := by
  sorry
-- !benchmark @end proof_aux

theorem unsafeCopy_spec_satisfied (dst : List UInt8) (src : List UInt8)
    (h_precond : unsafeCopy_precond (dst) (src)) :
    unsafeCopy_postcond (dst) (src) (unsafeCopy (dst) (src) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof