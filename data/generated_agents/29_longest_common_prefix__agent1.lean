import Std

/-- Longest common prefix among an array of strings. -/
def longestCommonPrefix (strs : List String) : String :=
  if strs.isEmpty then
    ""
  else
    -- Find the length of the shortest string
    let minLen := strs.foldl (fun minL s => min minL s.length) (strs.head!.length)
    if minLen == 0 then
      ""
    else
      -- Compare character by character up to minLen
      let rec findPrefix (i : Nat) : String :=
        if i == minLen then
          strs.head!.extract 0 minLen
        else
          let c := strs.head!.get ⟨i, by sorry⟩
          if strs.tail!.all (fun s => s.get ⟨i, by sorry⟩ == c) then
            findPrefix (i + 1)
          else
            strs.head!.extract 0 i
      findPrefix 0

/-- Verify if `prefix` is a common prefix of all strings in the array. -/
def verifyPrefix (prefix : String) (strs : List String) : Bool :=
  strs.all (fun s => s.startsWith prefix)

/-- Verify that there is no strictly longer valid prefix. -/
def verifyNoLongerPrefix (prefix : String) (strs : List String) : Bool :=
  if strs.isEmpty then
    prefix == ""
  else if prefix == "" then
    true
  else
    -- If any string is shorter than or equal to prefix, there can't be a longer one
    if strs.any (fun s => s.length ≤ prefix.length) then
      true
    else
      -- Otherwise, look at the next character in each string
      let nextChars := strs.filterMap (fun s => if s.length > prefix.length then some (s.get ⟨prefix.length, by sorry⟩) else none)
      let uniqueChars := nextChars.foldl (fun set c => set.insert c) {}
      uniqueChars.size > 1

/-- Precondition for longestCommonPrefix -/
def longestCommonPrefix.pre (strs : List String) : Prop := True

/-- Postcondition for longestCommonPrefix -/
def longestCommonPrefix.post (strs : List String) (result : String) : Prop :=
  verifyPrefix result strs ∧ verifyNoLongerPrefix result strs

/-- Correctness theorem for longestCommonPrefix -/
theorem longestCommonPrefix.correct (strs : List String) : 
  longestCommonPrefix.pre strs → longestCommonPrefix.post strs (longestCommonPrefix strs) := by
  sorry

/-- Tests for longestCommonPrefix -/
def longestCommonPrefix.tests : IO Unit := do
  let test1 := longestCommonPrefix ["flower", "flow", "flight"] == "fl"
  IO.println s!"Test 1: {test1}"
  
  let test2 := longestCommonPrefix ["dog", "racecar", "car"] == ""
  IO.println s!"Test 2: {test2}"
  
  let test3 := longestCommonPrefix [] == ""
  IO.println s!"Test 3: {test3}"
  
  let test4 := longestCommonPrefix [""] == ""
  IO.println s!"Test 4: {test4}"
  
  let test5 := longestCommonPrefix ["a"] == "a"
  IO.println s!"Test 5: {test5}"
  
  let test6 := longestCommonPrefix ["", ""] == ""
  IO.println s!"Test 6: {test6}"
  
  let test7 := longestCommonPrefix ["flower", "flower", "flower"] == "flower"
  IO.println s!"Test 7: {test7}"
  
  let test8 := longestCommonPrefix ["interspecies", "interstellar", "interstate"] == "inters"
  IO.println s!"Test 8: {test8}"
  
  IO.println "All tests completed."
