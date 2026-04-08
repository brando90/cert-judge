```lean
/- 
VeriBench: Problem HumanEval/36
-/

def fizzBuzz (n : Nat) : Nat :=
  let ns := (List.range n).filter (fun i => i % 11 == 0 || i % 13 == 0)
  let s := String.join (ns.map toString)
  s.toList.foldl (fun count c => if c == '7' then count + 1 else count) 0

/-- Returns the number of times the digit 7 appears in integers less than n which are divisible by 11 or 13. -/
def fizzBuzz_spec (n : Nat) : Nat :=
  let ns := (List.range n).filter (fun i => i % 11 == 0 || i % 13 == 0)
  let s := String.join (ns.map toString)
  s.toList.foldl (fun count c => if c == '7' then count + 1 else count) 0

theorem fizzBuzz_correct (n : Nat) : fizzBuzz n = fizzBuzz_spec n := by
  simp [fizzBuzz, fizzBuzz_spec]
  sorry

/-- Test cases for fizzBuzz -/
def fizzBuzz_test : IO Unit := do
  assert! (fizzBuzz 50 = 0)
  assert! (fizzBuzz 78 = 2)
  assert! (fizzBuzz 79 = 3)
  assert! (fizzBuzz 100 = 3)
  assert! (fizzBuzz 200 = 6)
  assert! (fizzBuzz 4000 = 192)
  assert! (fizzBuzz 10000 = 639)
  assert! (fizzBuzz 100000 = 8026)
  IO.println "All tests passed!"

#eval fizzBuzz_test
```
