import Std.Classes.LT
import Std.Data.HashMap
open Std

structure State where
  start : Nat
  maxLen : Nat
  charPos : HashMap Char Nat
  deriving Inhabited

def lengthOfLongestSubstring (s : String) : Nat :=
  if s.isEmpty then 0
  else
    let rec process (i : Nat) (state : State) : Nat :=
      if i >= s.length then
        state.maxLen
      else
        let char := s.get i
        let newStart := 
          match state.charPos.find? char with
          | some pos => if pos >= state.start then pos + 1 else state.start
          | none => state.start
        
        let newMaxLen := max state.maxLen (i - newStart + 1)
        let newCharPos := state.charPos.insert char i
        
        process (i + 1) { start := newStart, maxLen := newMaxLen, charPos := newCharPos }
    
    process 0 { start := 0, maxLen := 0, charPos := HashMap.empty }

def pre (s : String) : Prop := True

def post (s : String) (result : Nat) : Prop :=
  if s.isEmpty then 
    result = 0
  else
    ∃ (i j : Nat), i ≤ j ∧ j < s.length ∧ 
      (∀ k l, i ≤ k ∧ k < l ∧ l ≤ j → s.get k ≠ s.get l) ∧
      result = j - i + 1 ∧
      (∀ i' j', i' ≤ j' ∧ j' < s.length ∧ 
        (∀ k l, i' ≤ k ∧ k < l ∧ l ≤ j' → s.get k ≠ s.get l) →
        j' - i' + 1 ≤ result)

theorem lengthOfLongestSubstring_correct (s : String) (h : pre s) : 
  post s (lengthOfLongestSubstring s) := by
  sorry

def testLengthOfLongestSubstring : IO Unit := do
  assert! (lengthOfLongestSubstring "abcabcbb" = 3)
  assert! (lengthOfLongestSubstring "bbbbb" = 1)
  assert! (lengthOfLongestSubstring "pwwkew" = 3)
  assert! (lengthOfLongestSubstring "" = 0)
  assert! (lengthOfLongestSubstring " " = 1)
  assert! (lengthOfLongestSubstring "au" = 2)
  assert! (lengthOfLongestSubstring "aab" = 2)
  assert! (lengthOfLongestSubstring "dvdf" = 3)
  IO.println "All tests passed!"

#eval testLengthOfLongestSubstring
