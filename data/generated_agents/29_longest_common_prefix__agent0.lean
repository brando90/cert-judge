import VeriBench.Common

/--
Find the longest common prefix among an array of strings.

Examples:
  - longest_common_prefix ["flower", "flow", "flight"] = "fl"
  - longest_common_prefix ["dog", "racecar", "car"] = ""
  - longest_common_prefix [] = ""
  - longest_common_prefix [""] = ""
  - longest_common_prefix ["a"] = "a"
  - longest_common_prefix ["", ""] = ""
  - longest_common_prefix ["flower", "flower", "flower"] = "flower"
  - longest_common_prefix ["interspecies", "interstellar", "interstate"] = "inters"
-/

def longest_common_prefix (strs : List String) : String :=
  if strs.isEmpty then
    ""
  else
    -- Find the length of the shortest string
    let minLen := strs.foldl (fun acc s => min acc s.length) strs.head!.length
    if minLen = 0 then
      ""
    else
      -- Compare character by character up to minLen
      let rec findPrefix (i : Nat) : String :=
        if i = minLen then
          strs.head!.take minLen
        else
          let c := strs.head![i]!
          if strs.tail!.all (fun s => s[i]! = c) then
            findPrefix (i + 1)
          else
            strs.head!.take i
      findPrefix 0

/-- Verify if `prefix` is a common prefix of all strings in the array. -/
def verify_prefix (prefix : String) (strs : List String) : Bool :=
  strs.all (fun s => s.startsWith prefix)

/-- Verify that there is no strictly longer valid prefix. -/
def verify_no_longer_prefix (prefix : String) (strs : List String) : Bool :=
  if strs.isEmpty then
    prefix = ""
  else if prefix = "" then
    true
  else
    -- If any string is shorter than or equal to prefix, there can't be a longer one
    if strs.any (fun s => s.length ≤ prefix.length) then
      true
    else
      -- Otherwise, look at the next character in each string
      let nextChars := strs.filterMap (fun s => if s.length > prefix.length then some s[prefix.length]! else none)
      let uniqueChars := nextChars.foldl (fun acc c => if acc.contains c then acc else c :: acc) []
      uniqueChars.length > 1

/-- Precondition: All elements must be strings. -/
def pre (strs : List String) : Bool := true

/-- 
Postcondition: The result is a common prefix of all strings, 
and there is no longer common prefix.
-/
def post (strs : List String) (result : String) : Bool :=
  verify_prefix result strs && verify_no_longer_prefix result strs

theorem longest_common_prefix_correct (strs : List String) :
  pre strs → post strs (longest_common_prefix strs) := sorry

/-- Tests for the longest_common_prefix function -/
def longest_common_prefix_tests : List (Test (List String) String) := [
  -- Basic test
  Test.mk "Basic test" ["flower", "flow", "flight"] "fl",
  -- Empty list returns empty string
  Test.mk "Empty list" [] "",
  -- Single element
  Test.mk "Single element" ["a"] "a",
  -- Empty string in list
  Test.mk "Empty string in list" [""] "",
  -- Multiple empty strings
  Test.mk "Multiple empty strings" ["", ""] "",
  -- All identical strings
  Test.mk "All identical strings" ["flower", "flower", "flower"] "flower",
  -- Longer example
  Test.mk "Longer example" ["interspecies", "interstellar", "interstate"] "inters",
  -- No common prefix
  Test.mk "No common prefix" ["dog", "racecar", "car"] ""
]

/-- Run all tests for the longest_common_prefix function -/
def main : IO Unit :=
  testRunner longest_common_prefix_tests longest_common_prefix
