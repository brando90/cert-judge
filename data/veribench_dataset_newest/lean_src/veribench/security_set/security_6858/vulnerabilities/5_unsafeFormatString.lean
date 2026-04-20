import Mathlib

/-! Unsafe Format String (placeholder) -/
namespace UnsafeFormatString
def Pre : Prop := True
def Post : Prop := True
theorem correctness_thm (h:Pre): Post := by trivial
end UnsafeFormatString
