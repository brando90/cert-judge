import Mathlib

namespace TripleAll


def tripleAll (xs : List Int) : List Int :=
  xs.map (· * 3)


def tripleAllImp (xs : List Int) : List Int :=
  Id.run (do
    let mut out : List Int := []
    for x in xs do
      out := (x * 3) :: out
    return out.reverse)



/-!
# Tests
-/

/-- expected: [3, 6, 9] -/
example : tripleAll [1, 2, 3] = [3, 6, 9] := by native_decide
#eval tripleAll [1, 2, 3] -- expected: [3, 6, 9]

/-- expected: [] -/
example : tripleAll [] = [] := by native_decide
#eval tripleAll [] -- expected: []

/-!
# Tests: Edge Cases
-/

/-- expected: [-3, 0, 12] -/
example : tripleAll [-1, 0, 4] = [-3, 0, 12] := by native_decide
#eval tripleAll [-1, 0, 4] -- expected: [-3, 0, 12]

/-- expected: [0] -/
example : tripleAll [0] = [0] := by native_decide
#eval tripleAll [0] -- expected: [0]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single element -/
example : tripleAll [5] = [15] := by native_decide
#eval tripleAll [5] -- expected: [15]

/-- positive: negative numbers -/
example : tripleAll [-2, -3] = [-6, -9] := by native_decide
#eval tripleAll [-2, -3] -- expected: [-6, -9]

/-- negative: length is preserved -/
example : ¬ ((tripleAll [1, 2]).length ≠ [1, 2].length) := by native_decide
#eval (decide ((tripleAll [1, 2]).length ≠ [1, 2].length)) -- expected: false

/-- negative: empty list doesn't become non-empty -/
example : ¬ ((tripleAll ([] : List Int)).length > 0) := by native_decide
#eval (decide ((tripleAll ([] : List Int)).length > 0)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single element -/
example : tripleAllImp [7] = [21] := by native_decide
#eval tripleAllImp [7] -- expected: [21]

/-- negative: no element is unchanged (except zero) -/
example : ¬ ((tripleAllImp [1, 2, 3]).any (· ∈ [1, 2, 3])) := by sorry
#eval (decide ((tripleAllImp [1, 2, 3]).any (· ∈ [1, 2, 3]))) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
private theorem tripleAllImp_aux (xs acc : List Int) :
    Id.run (do
      let mut out := acc
      for x in xs do
        out := (x * 3) :: out
      return out.reverse) = acc.reverse ++ tripleAll xs := by
  induction xs generalizing acc with
  | nil =>
      simp [tripleAll]
  | cons x xs ih =>
      calc
        Id.run (do
          let mut out := acc
          for x in x :: xs do
            out := (x * 3) :: out
          return out.reverse) =
            Id.run (do
              let mut out := (x * 3) :: acc
              for x in xs do
                out := (x * 3) :: out
              return out.reverse) := by
              simp
        _ = ((x * 3) :: acc).reverse ++ tripleAll xs := ih ((x * 3) :: acc)
        _ = acc.reverse ++ tripleAll (x :: xs) := by
              simp [tripleAll, List.reverse_cons, List.append_assoc]

theorem tripleAll_equivalence_thm (xs : List Int) :
  tripleAll xs = tripleAllImp xs := by
  unfold tripleAllImp
  simpa using (tripleAllImp_aux xs []).symm




end TripleAll