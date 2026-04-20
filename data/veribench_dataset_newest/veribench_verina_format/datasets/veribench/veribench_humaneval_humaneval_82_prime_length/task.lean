-- !benchmark @start import type=solution
import Mathlib
namespace PrimeLength
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def primeLength_precond (s : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def primeLength (s : String) (h_precond : primeLength_precond (s)) : Bool :=
  -- !benchmark @start code
  let n := s.length
  if n ≤ 1 then
    false
  else
    (List.range n).drop 2 |>.all (fun i => n % i ≠ 0)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def primeLength_postcond (s : String) (result : Bool) (h_precond : primeLength_precond (s)) : Prop :=
  -- !benchmark @start postcond
  let isPrime (n : Nat) : Prop :=
    n > 1 ∧ ∀ i, 2 ≤ i ∧ i < n → n % i ≠ 0
  let empty_string_prop : Prop := primeLength ("") (by simp) = false
  let single_char_prop (c : Char) : Prop := primeLength (String.singleton c) (by simp) = false
  let length_independence_prop (s1 s2 : String) : Prop :=
    s1.length = s2.length → primeLength (s1) (by simp) = primeLength (s2) (by simp)
  let consistency_prop (t : String) : Prop := primeLength (t) (by simp) = true ↔ isPrime t.length
  empty_string_prop ∧
    (∀ c, single_char_prop c) ∧
    (∀ s1 s2, length_independence_prop s1 s2) ∧
    (result = true ↔ isPrime s.length)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem primeLength_spec_satisfied (s : String) (h_precond : primeLength_precond (s)) :
    primeLength_postcond (s) (primeLength (s) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof