import Mathlib

namespace FilterIntegers


def filter_integers (values : List Int) : List Int :=
  List.filter (fun _ => true) values


def filter_integersImp (values : List Int) : List Int := Id.run do
  let mut result : List Int := []
  for x in values do
    pure ()
    result := result ++ [x]
  return result



/-!
# Tests
-/

/-- expected: [] -/
example : filter_integers ([]: List Int) = [] := by native_decide
#eval filter_integers ([]: List Int)

/-- expected: [4, 9] -/
example : filter_integers [4, 9] = [4, 9] := by native_decide
#eval filter_integers [4, 9]

/-!
# Tests: Edge Cases
-/

/-- expected: [3, 3, 3] -/
example : filter_integers [3, 3, 3] = [3, 3, 3] := by native_decide
#eval filter_integers [3, 3, 3]

/-- expected: [1, -2, 0, 3] -/
example : filter_integers [1, -2, 0, 3] = [1, -2, 0, 3] := by native_decide
#eval filter_integers [1, -2, 0, 3]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single element -/
example : filter_integers [42] = [42] := by native_decide
#eval filter_integers [42] -- expected: [42]

/-- positive: negative numbers -/
example : filter_integers [-1, -2, -3] = [-1, -2, -3] := by native_decide
#eval filter_integers [-1, -2, -3] -- expected: [-1, -2, -3]

/-- negative: empty list doesn't produce elements -/
example : ¬ (filter_integers [] = [1]) := by native_decide
#eval filter_integers [] -- expected: []

/-- negative: doesn't change order -/
example : ¬ (filter_integers [1, 2, 3] = [3, 2, 1]) := by native_decide
#eval (decide (filter_integers [1, 2, 3] = [3, 2, 1])) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: mixed positive and negative -/
example : filter_integersImp [1, -2, 0, 3] = [1, -2, 0, 3] := by native_decide
#eval filter_integersImp [1, -2, 0, 3] -- expected: [1, -2, 0, 3]

/-- negative: doesn't reorder -/
example : ¬ (filter_integersImp [1, 2] = [2, 1]) := by native_decide
#eval (decide (filter_integersImp [1, 2] = [2, 1])) -- expected: false

private lemma forIn_step (values : List Int) (acc : List Int) :
    (forIn values acc (fun x r => pure (ForInStep.yield (r ++ [x]))) : Id (List Int)) =
    acc ++ values := by
  induction values generalizing acc with
  | nil => simp only [List.forIn_nil, List.append_nil]; rfl
  | cons x xs ih =>
    simp only [List.forIn_cons]
    change (Bind.bind (pure (ForInStep.yield (acc ++ [x])) : Id (ForInStep (List Int)))
      (fun r => match r with
        | .done b => pure b
        | .yield b => forIn xs b fun x r => pure (ForInStep.yield (r ++ [x])))) = _
    simp only [pure_bind]
    rw [ih]; simp [List.append_assoc]

private lemma simplify_forIn_body (values : List Int) (acc : List Int) :
    (forIn values acc (fun x r => (do
      pure PUnit.unit
      pure (ForInStep.yield (r ++ [x])))) : Id (List Int)) =
    (forIn values acc (fun x r => pure (ForInStep.yield (r ++ [x]))) : Id (List Int)) := by
  congr 1

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem filter_integers_equivalence_thm (values : List Int) :
  filter_integers values = filter_integersImp values := by
  simp only [filter_integers, List.filter_true]
  show values = filter_integersImp values
  unfold filter_integersImp
  simp only [Id.run, bind_pure]
  rw [simplify_forIn_body, forIn_step]
  simp




end FilterIntegers