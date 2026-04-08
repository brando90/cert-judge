import Lean

namespace HumanEval36

/-- 
  Return the number of times the digit 7 appears in integers less than n which are divisible by 11 or 13.
-/
def fizz_buzz (n : Int) : Int :=
  let ns := List.range n |>.filter (fun i => i % 11 = 0 || i % 13 = 0)
  let s := String.join (ns.map toString)
  let chars := s.toList
  chars.foldl (fun acc c => if c = '7' then acc + 1 else acc) 0

-- Tests
#eval fizz_buzz 50 -- 0
#eval fizz_buzz 78 -- 2
#eval fizz_buzz 79 -- 3
#eval fizz_buzz 100 -- 3
#eval fizz_buzz 200 -- 6
#eval fizz_buzz 4000 -- 192
#eval fizz_buzz 10000 -- 639
#eval fizz_buzz 100000 -- 8026

-- Specification
def spec (n : Int) : Int :=
  let ns := List.range n |>.filter (fun i => i % 11 = 0 || i % 13 = 0)
  let s := String.join (ns.map toString)
  let chars := s.toList
  chars.foldl (fun acc c => if c = '7' then acc + 1 else acc) 0

-- Precondition
def pre (n : Int) : Prop :=
  n ≥ 0

-- Postcondition
def post (n : Int) (result : Int) : Prop :=
  result = spec n

theorem fizz_buzz_correct (n : Int) (h : pre n) : post n (fizz_buzz n) :=
  sorry

end HumanEval36
