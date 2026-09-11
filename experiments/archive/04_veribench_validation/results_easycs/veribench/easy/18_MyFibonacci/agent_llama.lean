import Std.Data.Nat.Basic

/-- Return the nth Fibonacci number for natural number indices.

Edge cases:
- fibonacci(0) = 0
- fibonacci(1) = 1
- fibonacci(n) = fibonacci(n-1) + fibonacci(n-2) for n > 1
-/

def fib (n : Nat) : Nat :=
  match n with
  | 0 => 0
  | 1 => 1
  | n+2 => fib (n+1) + fib n

def fibonacci (n : Int) : Int :=
  if n < 0 then
    panic! s!"Input must be a non-negative integer (got n={n})"
  else
    let n' := n.toNat
    if n' <= 1 then
      n
    else
      let mut a := 0
      let mut b := 1
      for _ in [2:n'+1] do
        let temp := a + b
        a := b
        b := temp
      b

def fibonacci_spec (n : Int) : Int :=
  if n < 0 then
    panic! s!"Input must be a non-negative integer (got n={n})"
  else
    fib n.toNat

theorem fibonacci_correct (n : Int) : fibonacci n = fibonacci_spec n := by
  sorry

#eval fibonacci 6 -- 8
#eval fibonacci 0 -- 0

def test : IO Unit := do
  assert! (fibonacci 6 = 8)
  assert! (fibonacci 0 = 0)
  
  let badInputs := [-1, -100]
  for x in badInputs do
    try
      let _ := fibonacci x
      panic! "expected pre-violation did not raise"
    catch _ =>
      pure ()
  
  IO.println "All tests passed."
