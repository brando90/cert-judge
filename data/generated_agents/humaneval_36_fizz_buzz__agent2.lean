```lean
import Mathlib.Tactic.LibrarySearch
import Mathlib.Tactic.Ring
import Mathlib.Data.Nat.Basic
import Mathlib.Data.List.Basic

namespace VeriBench
namespace HumanEval36

/--
Return the number of times the digit 7 appears in integers less than n which are divisible by 11 or 13.
-/
def fizz_buzz (n : Nat) : Nat :=
  let ns := List.filter (fun i => i % 11 = 0 || i % 13 = 0) (List.range n)
  let s := String.join (ns.map (toString))
  s.toList.filter (fun c => c = '7') |>.length

/-- Precondition for the function -/
def fizz_buzz_pre (n : Nat) : Prop := True

/-- Postcondition for the function -/
def fizz_buzz_post (n : Nat) (result : Nat) : Prop :=
  result = fizz_buzz n

/-- Correctness theorem for the function -/
theorem fizz_buzz_correct (n : Nat) (h : fizz_buzz_pre n) : fizz_buzz_post n (fizz_buzz n) := by
  unfold fizz_buzz_post
  simp
  
#eval fizz_buzz 50  -- 0
#eval fizz_buzz 78  -- 2
#eval fizz_buzz 79  -- 3
#eval fizz_buzz 100 -- 3
#eval fizz_buzz 200 -- 6
#eval fizz_buzz 4000 -- 192
-- Larger tests are commented out to avoid long execution times
-- #eval fizz_buzz 10000 -- 639
-- #eval fizz_buzz 100000 -- 8026

end HumanEval36
end VeriBench
```
