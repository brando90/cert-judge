-- !benchmark @start import type=solution
import Mathlib
namespace Humaneval51_RemoveVowels
-- !benchmark @end import

-- !benchmark @start solution_aux
/-- List of vowels considered by `isVowel`. -/
def vowels : List Char := ("aeiouAEIOU").data

/-- Predicate: `true` iff the character is a vowel (case‑insensitive). -/
def isVowel (c : Char) : Bool :=
  let rec loop : List Char → Bool
    | []      => false
    | d :: ds => if decide (c = d) then true else loop ds
  loop vowels
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def removeVowels_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def removeVowels (s : String) (h_precond : removeVowels_precond (s)) : String :=
  -- !benchmark @start code
  String.mk <| s.data.filter (fun c => !(isVowel c))
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


@[reducible, simp]
def removeVowels_postcond (s : String) (result : String) (h_precond : removeVowels_precond (s)) : Prop :=
  -- !benchmark @start postcond
  (∀ c, c ∈ result.data → isVowel c = false) ∧
    result.data = s.data.filter (fun c => !(isVowel c)) ∧
    result.data.length = s.data.countP (fun c => !(isVowel c)) ∧
    removeVowels (result) (by simp) = result ∧
    (∀ c, c ∈ result.data ↔ (c ∈ s.data ∧ isVowel c = false)) ∧
    (∀ t, removeVowels (s ++ t) (by simp) = (removeVowels (s) (by simp)) ++ (removeVowels (t) (by simp))) ∧
    ((∀ c ∈ s.data, isVowel c = true) → result = "") ∧
    ((∀ c ∈ s.data, isVowel c = false) → result = s)
  -- !benchmark @end postcond


-- !benchmark @start proof_aux
/-- **No‑vowels property**: output contains no vowels. -/
def no_vowels_prop (s : String) : Prop :=
  ∀ c, c ∈ (removeVowels s (by simp)).data → isVowel c = false

/-- **No‑vowels theorem**: output contains no vowels. -/
@[simp] theorem no_vowels_thm (s : String) : no_vowels_prop s := by
  sorry

/-- **Filter‑spec property**: equals filtering non‑vowels from the input. -/
def filter_spec_prop (s : String) : Prop :=
  (removeVowels s (by simp)).data = s.data.filter (fun c => !(isVowel c))

/-- **Filter‑spec theorem**: equals filtering non‑vowels from the input. -/
@[simp] theorem filter_spec_thm (s : String) : filter_spec_prop s := by
  sorry

/--
**Length property**: exact character count equals the number of non‑vowels.

Note: we phrase length on the underlying character list to avoid encoding subtleties.
-/
def length_prop (s : String) : Prop :=
  (removeVowels s (by simp)).data.length = s.data.countP (fun c => !(isVowel c))

/-- **Length theorem**: exact character count equals the number of non‑vowels. -/
@[simp] theorem length_thm (s : String) : length_prop s := by
  sorry

/-- **Idempotence property**: removing vowels twice is the same as once. -/
def idempotent_prop (s : String) : Prop :=
  removeVowels (removeVowels s (by simp)) (by simp) = removeVowels s (by simp)

/-- **Idempotence theorem**: removing vowels twice is the same as once. -/
@[simp] theorem idempotent_thm (s : String) : idempotent_prop s := by
  sorry

/--
**Membership equivalence property**: a character appears in the output iff it
appears in the input and is not a vowel (ignoring multiplicity).
-/
def mem_iff_prop (s : String) : Prop :=
  ∀ c, c ∈ (removeVowels s (by simp)).data ↔ (c ∈ s.data ∧ isVowel c = false)

/-- **Membership equivalence theorem**: a character appears in the output iff it appears in the input and is not a vowel (ignoring multiplicity). -/
@[simp] theorem mem_iff_thm (s : String) : mem_iff_prop s := by
  sorry

/--
**Append‑homomorphism property**: removing vowels distributes over concatenation.
-/
def append_hom_prop (s t : String) : Prop :=
  removeVowels (s ++ t) (by simp) = (removeVowels s (by simp)) ++ (removeVowels t (by simp))

/-- **Append‑homomorphism theorem**: removing vowels distributes over concatenation. -/
@[simp] theorem append_hom_thm (s t : String) : append_hom_prop s t := by
  sorry

/--
**All‑vowels collapse property**: if every character is a vowel, the result is empty.
-/
def all_vowels_empty_prop (s : String) : Prop :=
  (∀ c ∈ s.data, isVowel c = true) → removeVowels s (by simp) = ""

/-- **All‑vowels collapse theorem**: if every character is a vowel, the result is empty. -/
@[simp] theorem all_vowels_empty_thm (s : String) : all_vowels_empty_prop s := by
  sorry

/--
**No‑vowels identity property**: if the input has no vowels, the output equals the input.
-/
def no_vowels_identity_prop (s : String) : Prop :=
  (∀ c ∈ s.data, isVowel c = false) → removeVowels s (by simp) = s

/-- **No‑vowels identity theorem**: if the input has no vowels, the output equals the input. -/
@[simp] theorem no_vowels_identity_thm (s : String) : no_vowels_identity_prop s := by
  sorry
-- !benchmark @end proof_aux


theorem removeVowels_spec_satisfied (s : String) (h_precond : removeVowels_precond (s)) :
    removeVowels_postcond (s) (removeVowels (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof

end Humaneval51_RemoveVowels