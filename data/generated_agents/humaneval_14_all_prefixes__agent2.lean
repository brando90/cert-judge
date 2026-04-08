```lean
/-
File: humaneval_14_all_prefixes.lean
HumanEval problem HumanEval/14
-/

def allPrefixes (string : String) : List String :=
  let rec helper (i : Nat) (acc : List String) : List String :=
    if i ≥ string.length then
      acc
    else
      helper (i + 1) (acc ++ [string.extract 0 (i + 1)])
  helper 0 []

/-- Specification for `allPrefixes` -/
def allPrefixes_spec (string : String) : List String :=
  let rec helper (i : Nat) (acc : List String) : List String :=
    if i ≥ string.length then
      acc
    else
      helper (i + 1) (acc ++ [string.extract 0 (i + 1)])
  helper 0 []

/-- Precondition for `allPrefixes` -/
def allPrefixes_pre (_string : String) : Prop := True

/-- Postcondition for `allPrefixes` -/
def allPrefixes_post (string : String) (result : List String) : Prop :=
  result = allPrefixes_spec string

theorem allPrefixes_correct (string : String) (h_pre : allPrefixes_pre string) :
  allPrefixes_post string (allPrefixes string) := by
  simp [allPrefixes_post, allPrefixes]
  sorry

/-- Test cases for `allPrefixes` -/
def allPrefixes_test : IO Unit := do
  assert! (allPrefixes "" = [])
  assert! (allPrefixes "asdfgh" = ["a", "as", "asd", "asdf", "asdfg", "asdfgh"])
  assert! (allPrefixes "WWW" = ["W", "WW", "WWW"])
  IO.println "All tests passed!"

#eval allPrefixes_test
```
