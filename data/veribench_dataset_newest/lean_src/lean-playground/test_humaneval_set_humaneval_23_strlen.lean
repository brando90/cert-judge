import Mathlib

namespace StrLen


def strlen (s : String) : Nat :=
  s.length


def strlenImp (s : String) : Nat := Id.run do
  let mut count := 0
  for _ in s.toList do
    count := count + 1
  return count



/-!
# Tests
-/

/-- expected: 0 -/
example : strlen "" == 0 := by native_decide
#eval strlen ""

/-- expected: 3 -/
example : strlen "abc" == 3 := by native_decide
#eval strlen "abc"

/-!
# Tests: Edge Cases
-/

/-- expected: 1 -/
example : strlen "x" == 1 := by native_decide
#eval strlen "x"

/-- expected: 9 -/
example : strlen "asdasnakj" == 9 := by native_decide
#eval strlen "asdasnakj"

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: longer string -/
example : strlen "Hello, World!" == 13 := by native_decide
#eval strlen "Hello, World!" -- expected: 13

/-- positive: string with spaces -/
example : strlen "   " == 3 := by native_decide
#eval strlen "   " -- expected: 3

/-- negative: empty string is not length 1 -/
example : ¬ (strlen "" == 1) := by native_decide
#eval (decide (strlen "" == 1)) -- expected: false

/-- negative: single char is not length 0 -/
example : ¬ (strlen "a" == 0) := by native_decide
#eval (decide (strlen "a" == 0)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: longer string -/
example : strlenImp "Hello" == 5 := by native_decide
#eval strlenImp "Hello" -- expected: 5

/-- negative: doesn't undercount -/
example : ¬ (strlenImp "ab" == 1) := by native_decide
#eval (decide (strlenImp "ab" == 1)) -- expected: false

private lemma forIn_count (l : List Char) (acc : Nat) :
    (forIn l acc (fun _ (r : Nat) => pure (ForInStep.yield (r + 1))) : Id Nat) =
    acc + l.length := by
  induction l generalizing acc with
  | nil =>
    simp only [List.forIn_nil, List.length_nil, Nat.add_zero]; rfl
  | cons x xs ih =>
    simp only [List.forIn_cons]
    change (Bind.bind (pure (ForInStep.yield (acc + 1)) : Id (ForInStep Nat))
      (fun r => match r with
        | .done b => pure b
        | .yield b => forIn xs b fun _ r => pure (ForInStep.yield (r + 1)))) = _
    simp only [pure_bind, ih]
    show acc + 1 + xs.length = acc + (x :: xs).length
    rw [List.length_cons]; ring

private lemma string_length_eq (s : String) : s.length = s.toList.length := by rfl

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem strlen_equivalence_thm (s : String) :
  strlen s = strlenImp s := by
  unfold strlen strlenImp
  simp only [Id.run, bind_pure, pure_bind]
  rw [forIn_count, Nat.zero_add, string_length_eq]




end StrLen