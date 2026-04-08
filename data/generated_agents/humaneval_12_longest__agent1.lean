import VeriBench

namespace HumanEval12

def longest (strings : List String) : Option String :=
  if strings.isEmpty then
    none
  else
    let maxlen := strings.map String.length |>.maximum?.getD 0
    strings.find? (fun s => s.length = maxlen)

-- Tests
def test : IO Unit := do
  assert $ longest [] = none
  assert $ longest ["x", "y", "z"] = some "x"
  assert $ longest ["x", "yyy", "zzzz", "www", "kkkk", "abc"] = some "zzzz"
  IO.println "All tests passed!"

-- Specification
def longestSpec (strings : List String) : Option String :=
  if strings.isEmpty then
    none
  else
    let maxlen := strings.map String.length |>.maximum?.getD 0
    strings.find? (fun s => s.length = maxlen)

-- Verification
theorem longest_correct (strings : List String) : longest strings = longestSpec strings := by
  simp [longest, longestSpec]
  sorry

end HumanEval12
