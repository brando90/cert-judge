import Lean
import Std

namespace VeriBench.HumanEval14

/-- Return list of all prefixes from shortest to longest of the input string -/
def all_prefixes (string : String) : List String :=
  let rec aux (i : Nat) (acc : List String) : List String :=
    if i ≥ string.length then
      acc.reverse
    else
      let prefix := string.take (i + 1)
      aux (i + 1) (prefix :: acc)
  aux 0 []

/-- Specification for all_prefixes -/
def all_prefixes_spec (string : String) : List String :=
  List.map (fun i => string.take (i + 1)) (List.range string.length)

theorem all_prefixes_correct (string : String) : all_prefixes string = all_prefixes_spec string := by
  sorry

/-- Test cases for all_prefixes -/
def test : IO Unit := do
  assert! (all_prefixes "" == [])
  assert! (all_prefixes "asdfgh" == ["a", "as", "asd", "asdf", "asdfg", "asdfgh"])
  assert! (all_prefixes "WWW" == ["W", "WW", "WWW"])
  IO.println "All tests passed!"

end VeriBench.HumanEval14
