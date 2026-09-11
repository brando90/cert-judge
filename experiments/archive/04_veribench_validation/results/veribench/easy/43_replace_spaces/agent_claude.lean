```lean
import Lean
import Std

namespace VeriBench.ReplaceSpaces

/- Implementation -/

def pre (s : String) : Bool := true  -- In Lean, type system ensures s is a String

def replaceSpaces (s : String) : String :=
  s.replace " " "_"

/- Tests -/

def test_replaceSpaces : IO Unit := do
  assert! (replaceSpaces "hello world" == "hello_world")
  assert! (replaceSpaces "a b c" == "a_b_c")
  assert! (replaceSpaces "no-spaces" == "no-spaces")
  assert! (replaceSpaces "" == "")
  IO.println "All tests passed"

/- Verification -/

/-- Predicate that holds when all spaces in a string are replaced with underscores -/
def spacesReplacedWithUnderscores (s : String) (result : String) : Prop :=
  ∀ i : Fin result.length, 
    result.get i ≠ ' ' ∧ 
    (result.get i = '_' → ∃ j : Fin s.length, s.get j = ' ' ∧ 
      (∀ k : Fin s.length, k < j → s.get k ≠ ' ' → 
        ∃ l : Fin result.length, l < i ∧ result.get l = s.get k) ∧
      (∀ k : Fin s.length, k > j → s.get k ≠ ' ' → 
        ∃ l : Fin result.length, l > i ∧ result.get l = s.get k))

/-- Specification for replaceSpaces -/
def post (s : String) (result : String) : Prop :=
  spacesReplacedWithUnderscores s result ∧
  result.length = s.length

theorem replaceSpaces_correct (s : String) :
  pre s → post s (replaceSpaces s) := by
  sorry

end VeriBench.ReplaceSpaces
```
