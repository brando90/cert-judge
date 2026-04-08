/-
File: humaneval_82_prime_length.lean
HumanEval problem HumanEval/82
-/

def prime_length (s : String) : Bool :=
  let l := s.length
  if l == 0 || l == 1 then
    false
  else
    let rec is_prime_helper (i : Nat) : Bool :=
      if i >= l then
        true
      else if l % i == 0 then
        false
      else
        is_prime_helper (i + 1)
    is_prime_helper 2

/-
Tests for prime_length
-/

def test_prime_length : Bool :=
  prime_length "Hello" == true &&
  prime_length "abcdcba" == true &&
  prime_length "kittens" == true &&
  prime_length "orange" == false &&
  prime_length "wow" == true &&
  prime_length "world" == true &&
  prime_length "MadaM" == true &&
  prime_length "Wow" == true &&
  prime_length "" == false &&
  prime_length "HI" == true &&
  prime_length "go" == true &&
  prime_length "gogo" == false &&
  prime_length "aaaaaaaaaaaaaaa" == false &&
  prime_length "Madam" == true &&
  prime_length "M" == false &&
  prime_length "0" == false

#eval test_prime_length -- Should return true

/-
Formal specification and verification
-/

def is_prime (n : Nat) : Bool :=
  if n <= 1 then
    false
  else
    let rec no_divisors (i : Nat) : Bool :=
      if i >= n then
        true
      else if n % i == 0 then
        false
      else
        no_divisors (i + 1)
    no_divisors 2

-- Precondition: None (function works for any string)
def prime_length_pre (_s : String) : Prop := True

-- Postcondition: Returns true if and only if the string length is a prime number
def prime_length_post (s : String) (result : Bool) : Prop :=
  result = is_prime s.length

-- Correctness theorem
theorem prime_length_correct (s : String) :
  prime_length_pre s → prime_length_post s (prime_length s) := by
  sorry
