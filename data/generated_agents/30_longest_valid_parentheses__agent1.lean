import Lean

namespace VeriBench

def isValidParenthesesSubstring (s : String) (start : Nat) (len : Nat) : Bool :=
  if start + len > s.length then
    false
  else
    let substring := s.extract start (start + len)
    let mut count := 0
    let mut valid := true
    for i in [0:substring.length] do
      let c := substring.get ⟨i, by
        simp_arith
        apply Nat.lt_of_lt_of_le
        · exact i.2
        · simp [substring]
          exact Nat.le_of_lt (Nat.lt_of_lt_of_le i.2 (by simp [len]))
      ⟩
      if c == '(' then
        count := count + 1
      else
        count := count - 1
        if count < 0 then
          valid := false
    valid && count == 0

def pre (s : String) : Bool := true

def longest_valid_parentheses (s : String) : Nat :=
  if s.isEmpty then 
    0
  else
    -- Use a stack to track indices of unmatched parentheses
    let mut stack := [-1] -- Initialize with -1 to handle cases where valid substring starts at beginning
    let mut max_len := 0
    
    for i in [0:s.length] do
      let char := s.get ⟨i, by simp_arith; exact i.2⟩
      if char == '(' then
        -- Push the index of opening parenthesis
        stack := stack ++ [i]
      else -- char == ')'
        -- Pop the last opening parenthesis index
        stack := stack.take (stack.length - 1)
        if stack.isEmpty then
          -- If stack is empty, push current index as new base
          stack := [i]
        else
          -- Calculate length of current valid substring
          let curr_len := i - stack.getLast (by simp [stack])
          max_len := max max_len curr_len
    
    max_len

def post (s : String) (result : Nat) : Bool :=
  -- Check that result is the length of a valid substring
  (∃ start, isValidParenthesesSubstring s start result) &&
  -- Check that there is no longer valid substring
  (∀ len, len > result → ∀ start, !isValidParenthesesSubstring s start len)

theorem longest_valid_parentheses_correct (s : String) :
  pre s → post s (longest_valid_parentheses s) := by
  sorry

-- Tests
#eval longest_valid_parentheses "(())" -- 4
#eval longest_valid_parentheses ")()())" -- 4
#eval longest_valid_parentheses "" -- 0
#eval longest_valid_parentheses "(" -- 0
#eval longest_valid_parentheses ")" -- 0
#eval longest_valid_parentheses "()" -- 2
#eval longest_valid_parentheses "(())" -- 4
#eval longest_valid_parentheses "()()" -- 4
#eval longest_valid_parentheses "(()())" -- 6

end VeriBench
