import Mathlib.Data.List.Basic

namespace VeriBench

structure StringList where
  elements : List String
  isValid : elements.all (λ s => s.data.all (λ c => c.isValid)) := by simp

def longestCommonPrefix (strs : StringList) : String :=
  match strs.elements with
  | [] => ""
  | firstStr :: restStrs =>
    let minLen := (List.foldl (λ minSoFar str => min minSoFar str.length) firstStr.length strs.elements)
    if minLen = 0 then
      ""
    else
      let rec findPrefix (i : Nat) : String :=
        if i = minLen then
          firstStr.take minLen
        else
          let c := firstStr.get ⟨i, by simp [minLen, i]; exact Nat.lt_of_lt_of_le (Nat.lt_succ_self i) (Nat.le_of_eq rfl)⟩
          if restStrs.all (λ s => s.get ⟨i, by simp [minLen, i]; exact Nat.lt_of_lt_of_le (Nat.lt_succ_self i) (Nat.le_of_eq rfl)⟩ = c) then
            findPrefix (i + 1)
          else
            firstStr.take i
      findPrefix 0

def isPrefix (prefix : String) (s : String) : Bool :=
  prefix.length ≤ s.length && prefix = s.take prefix.length

def verifyPrefix (prefix : String) (strs : StringList) : Bool :=
  strs.elements.all (isPrefix prefix)

def verifyNoLongerPrefix (prefix : String) (strs : StringList) : Bool :=
  match strs.elements with
  | [] => prefix = ""
  | _ =>
    if prefix = "" then true
    else
      strs.elements.any (λ s => s.length ≤ prefix.length) ||
      let nextChars := strs.elements.filterMap (λ s => if s.length > prefix.length then some (s.get ⟨prefix.length, by simp⟩) else none)
      nextChars.length > 0 && (List.foldl (λ acc c => acc || nextChars.any (λ c' => c ≠ c')) false nextChars.head!)

def longestCommonPrefixPre (strs : StringList) : Prop := True

def longestCommonPrefixPost (strs : StringList) (result : String) : Prop :=
  verifyPrefix result strs = true ∧ verifyNoLongerPrefix result strs = true

theorem longestCommonPrefixCorrect (strs : StringList) :
  longestCommonPrefixPre strs → longestCommonPrefixPost strs (longestCommonPrefix strs) := by
  sorry

-- Test cases
def test1 : StringList := { elements := ["flower", "flow", "flight"] }
def test2 : StringList := { elements := ["dog", "racecar", "car"] }
def test3 : StringList := { elements := [] }
def test4 : StringList := { elements := [""] }
def test5 : StringList := { elements := ["a"] }
def test6 : StringList := { elements := ["", ""] }
def test7 : StringList := { elements := ["flower", "flower", "flower"] }
def test8 : StringList := { elements := ["interspecies", "interstellar", "interstate"] }

#eval longestCommonPrefix test1 -- "fl"
#eval longestCommonPrefix test2 -- ""
#eval longestCommonPrefix test3 -- ""
#eval longestCommonPrefix test4 -- ""
#eval longestCommonPrefix test5 -- "a"
#eval longestCommonPrefix test6 -- ""
#eval longestCommonPrefix test7 -- "flower"
#eval longestCommonPrefix test8 -- "inters"

end VeriBench
