```lean
/- Implementation -/
def duplicateChars (s : String) : String :=
  s.foldl (fun acc c => acc ++ (String.singleton c ++ String.singleton c)) ""

/- Tests -/
#eval duplicateChars "abc" -- "aabbcc"
#eval duplicateChars "" -- ""
#eval duplicateChars "!a " -- "!!aa  "

/- Specification -/
def duplicateChars_pre (s : String) : Prop := True

def duplicateChars_post (s : String) (result : String) : Prop :=
  result.length = 2 * s.length ∧
  ∀ i, i < s.length → 
    result.get! (2*i) = s.get! i ∧ 
    result.get! (2*i + 1) = s.get! i

theorem duplicateChars_correct (s : String) :
  duplicateChars_pre s →
  duplicateChars_post s (duplicateChars s) :=
  sorry
```
