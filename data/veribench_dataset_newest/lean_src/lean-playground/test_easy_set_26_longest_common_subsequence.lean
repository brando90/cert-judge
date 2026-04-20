import Mathlib

namespace LongestCommonSubsequence


def List.isSubsequence [DecidableEq α] (sub : List α) (sup : List α) : Bool :=
  match sub, sup with
  | [], _ => true
  | _, [] => false
  | h₁::t₁, h₂::t₂ =>
    if h₁ = h₂ then
      isSubsequence t₁ t₂
    else
      isSubsequence (h₁::t₁) t₂


def String.isSubsequence (sub : String) (sup : String) : Bool :=
  List.isSubsequence sub.toList sup.toList


def longestCommonSubsequence (s1 s2 : String) : String :=
  if s1.isEmpty || s2.isEmpty then
    ""
  else
    let chars1 := s1.toList
    let chars2 := s2.toList
    let rec lcsHelper (l1 l2 : List Char) : List Char :=
      match l1, l2 with
      | [], _ => []
      | _, [] => []
      | h1::t1, h2::t2 =>
        if h1 = h2 then
          h1 :: lcsHelper t1 t2
        else
          let lcs1 := lcsHelper t1 (h2::t2)
          let lcs2 := lcsHelper (h1::t1) t2
          if lcs1.length >= lcs2.length then lcs1 else lcs2
    String.mk (lcsHelper chars1 chars2)


def longestCommonSubsequenceImp (s1 s2 : String) : String :=
  if s1.isEmpty || s2.isEmpty then
    ""
  else
    let chars1 := s1.toList
    let chars2 := s2.toList
    let m := chars1.length
    let n := chars2.length
    
    -- Create DP table
    let rec buildDP (i j : Nat) : List Char :=
      if i = 0 || j = 0 then
        []
      else if chars1[i-1]! = chars2[j-1]! then
        chars1[i-1]! :: buildDP (i-1) (j-1)
      else
        let lcs1 := buildDP (i-1) j
        let lcs2 := buildDP i (j-1)
        if lcs1.length >= lcs2.length then lcs1 else lcs2
    
    String.mk (buildDP m n).reverse



/-!
# Tests
-/

/-- expected: "ace" -/
example : longestCommonSubsequence "abcde" "ace" = "ace" := by native_decide
#eval! longestCommonSubsequence "abcde" "ace" -- expected: "ace"

/-- expected: "abc" -/
example : longestCommonSubsequence "abc" "abc" = "abc" := by native_decide
#eval! longestCommonSubsequence "abc" "abc" -- expected: "abc"

/-!
# Tests: Edge Cases
-/

/-- expected: "" -/
example : longestCommonSubsequence "" "" = "" := by unfold longestCommonSubsequence; rfl
#eval! longestCommonSubsequence "" "" -- expected: ""

/-- expected: "" -/
example : longestCommonSubsequence "abc" "" = "" := by native_decide
#eval! longestCommonSubsequence "abc" "" -- expected: ""

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: identical strings return the string -/
example : longestCommonSubsequence "test" "test" = "test" := by native_decide
#eval! longestCommonSubsequence "test" "test" -- expected: "test"

/-- positive: no common characters -/
example : longestCommonSubsequence "abc" "def" = "" := by native_decide
#eval! longestCommonSubsequence "abc" "def" -- expected: ""

/-- negative: result should not be longer than either input -/
example : ¬ ((longestCommonSubsequence "abc" "def").length > "abc".length) := by native_decide
#eval! (decide ((longestCommonSubsequence "abc" "def").length > "abc".length)) -- expected: false

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: identical strings return the string -/
example : longestCommonSubsequenceImp "test" "test" = "test" := by native_decide
#eval! longestCommonSubsequenceImp "test" "test" -- expected: "test"

/-- negative: result should not be longer than shorter input -/
example : ¬ ((longestCommonSubsequenceImp "ab" "abc").length > "ab".length) := by native_decide
#eval! (decide ((longestCommonSubsequenceImp "ab" "abc").length > "ab".length)) -- expected: false

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem longestCommonSubsequence_equivalence_thm (s1 s2 : String) :
  longestCommonSubsequence s1 s2 = longestCommonSubsequenceImp s1 s2 := sorry




end LongestCommonSubsequence