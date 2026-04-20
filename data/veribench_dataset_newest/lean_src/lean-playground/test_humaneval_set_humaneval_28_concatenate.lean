import Mathlib

namespace StringConcatenate


def concatenate (strings : List String) : String :=
  String.join strings


def concatenateImp (strings : List String) : String := Id.run do
  let mut result : String := ""
  for s in strings do
    let _ : Unit := ()
    result := result ++ s
  return result



/-!
# Tests
-/

/-- expected: "" -/
example : concatenate [] = "" := by native_decide
#eval concatenate []

/-- expected: "xyz" -/
example : concatenate ["x", "y", "z"] = "xyz" := by native_decide
#eval concatenate ["x", "y", "z"]

/-!
# Tests: Edge Cases
-/

/-- expected: "hello world" -/
example : concatenate ["hello", " ", "world"] = "hello world" := by native_decide
#eval concatenate ["hello", " ", "world"]

/-- expected: "ab" -/
example : concatenate ["a", "", "b"] = "ab" := by native_decide
#eval concatenate ["a", "", "b"]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: single element -/
example : concatenate ["hello"] = "hello" := by native_decide
#eval concatenate ["hello"] -- expected: "hello"

/-- positive: empty strings -/
example : concatenate ["", "", ""] = "" := by native_decide
#eval concatenate ["", "", ""] -- expected: ""

/-- negative: empty list doesn't produce content -/
example : ¬ (concatenate [] = "abc") := by native_decide
#eval (decide (concatenate [] = "abc")) -- expected: false

/-- negative: order matters -/
example : ¬ (concatenate ["a", "b"] = "ba") := by native_decide
#eval (decide (concatenate ["a", "b"] = "ba")) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: multiple elements -/
example : concatenateImp ["a", "b", "c", "d"] = "abcd" := by native_decide
#eval concatenateImp ["a", "b", "c", "d"] -- expected: "abcd"

/-- negative: doesn't reorder -/
example : ¬ (concatenateImp ["a", "b"] = "ba") := by native_decide
#eval (decide (concatenateImp ["a", "b"] = "ba")) -- expected: false

private lemma forIn_concat (strings : List String) (acc : String) :
    (forIn strings acc (fun s r => pure (ForInStep.yield (r ++ s))) : Id String) =
    List.foldl (· ++ ·) acc strings := by
  induction strings generalizing acc with
  | nil =>
    simp only [List.forIn_nil, List.foldl_nil]; rfl
  | cons s ss ih =>
    simp only [List.forIn_cons, List.foldl_cons]
    change (Bind.bind (pure (ForInStep.yield (acc ++ s)) : Id (ForInStep String))
      (fun r => match r with
        | .done b => pure b
        | .yield b => forIn ss b fun s r => pure (ForInStep.yield (r ++ s)))) = _
    simp only [pure_bind]
    exact ih (acc ++ s)

private lemma simplify_forIn_concat (strings : List String) (acc : String) :
    (forIn strings acc (fun s r => (do
      pure PUnit.unit
      pure (ForInStep.yield (r ++ s)))) : Id String) =
    (forIn strings acc (fun s r => pure (ForInStep.yield (r ++ s))) : Id String) := by
  congr 1

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem concatenate_equivalence_thm (strings : List String) :
  concatenate strings = concatenateImp strings := by
  unfold concatenate concatenateImp String.join
  simp only [Id.run, bind_pure]
  rw [simplify_forIn_concat, forIn_concat]




end StringConcatenate