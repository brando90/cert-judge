import Lean
import Std.Data.List.Basic
import Std.Data.ByteArray

namespace VeriBench.SafeCopy

/--
Safe bytearray copy that prevents overflow.
-/

def safeCopy (dst : ByteArray) (src : ByteArray) : Except String ByteArray :=
  if src.size > dst.size then
    Except.error "source longer than destination"
  else
    -- Copy exactly src.size bytes
    Except.ok (dst.copySlice 0 src 0 src.size)

/-- Precondition: The source and destination must be valid ByteArrays -/
def safeCopyPre (dst : ByteArray) (src : ByteArray) : Prop := True

/-- Postcondition: If successful, the first src.size bytes of dst are replaced with src -/
def safeCopyPost (dst : ByteArray) (src : ByteArray) (result : Except String ByteArray) : Prop :=
  match result with
  | Except.error _ => src.size > dst.size
  | Except.ok newDst => 
      src.size ≤ dst.size ∧ 
      newDst.size = dst.size ∧
      (∀ i, i < src.size → newDst.get! i = src.get! i) ∧
      (∀ i, src.size ≤ i ∧ i < dst.size → newDst.get! i = dst.get! i)

/-- Correctness theorem: safeCopy satisfies its pre and postconditions -/
theorem safeCopy_correct (dst : ByteArray) (src : ByteArray) :
  safeCopyPre dst src → safeCopyPost dst src (safeCopy dst src) := sorry

/-- Tests for safeCopy -/
def tests : IO Bool := do
  -- 1) Safe copy: src fits in dst
  let d := ByteArray.mk #[0, 0, 0]
  let s := ByteArray.mk #[97, 98, 99] -- "abc"
  match safeCopy d s with
  | Except.error msg => 
      IO.println s!"Test 1 failed: {msg}"
      return false
  | Except.ok result =>
      if result.size != 3 || result.data != #[97, 98, 99] then
        IO.println s!"Test 1 failed: expected [97, 98, 99], got {result.data}"
        return false

  -- 2) Exact fit
  let d2 := ByteArray.mk #[0, 0]
  let s2 := ByteArray.mk #[120, 121] -- "xy"
  match safeCopy d2 s2 with
  | Except.error msg => 
      IO.println s!"Test 2 failed: {msg}"
      return false
  | Except.ok result =>
      if result.size != 2 || result.data != #[120, 121] then
        IO.println s!"Test 2 failed: expected [120, 121], got {result.data}"
        return false

  -- 3) Overflow attempt should raise
  let d3 := ByteArray.mk #[0, 0]
  let s3 := ByteArray.mk #[49, 50, 51] -- "123"
  match safeCopy d3 s3 with
  | Except.error _ => pure ()
  | Except.ok _ => 
      IO.println "Test 3 failed: expected error for overflow"
      return false

  -- 4) Empty src → no change
  let d4 := ByteArray.mk #[104, 101, 108, 108, 111] -- "hello"
  let s4 := ByteArray.mk #[]
  match safeCopy d4 s4 with
  | Except.error msg => 
      IO.println s!"Test 4 failed: {msg}"
      return false
  | Except.ok result =>
      if result.size != 5 || result.data != #[104, 101, 108, 108, 111] then
        IO.println s!"Test 4 failed: expected [104, 101, 108, 108, 111], got {result.data}"
        return false

  -- 5) Empty dst, nonempty src → raise
  let d5 := ByteArray.mk #[]
  let s5 := ByteArray.mk #[122] -- "z"
  match safeCopy d5 s5 with
  | Except.error _ => pure ()
  | Except.ok _ => 
      IO.println "Test 5 failed: expected error for overflow"
      return false

  IO.println "All tests passed"
  return true

end VeriBench.SafeCopy
