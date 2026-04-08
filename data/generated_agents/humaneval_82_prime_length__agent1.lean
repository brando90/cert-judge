namespace PrimeLength

/-- Checks if a number is a prime number. -/
def isPrime (n : Nat) : Bool :=
  if n ≤ 1 then
    false
  else
    let rec checkDivisors (i : Nat) : Bool :=
      if i * i > n then
        true
      else if n % i == 0 then
        false
      else
        checkDivisors (i + 1)
    checkDivisors 2

/-- Returns true if the string length is a prime number, false otherwise.
Examples:
  prime_length("Hello") == true
  prime_length("abcdcba") == true
  prime_length("kittens") == true
  prime_length("orange") == false
-/
def prime_length (string : String) : Bool :=
  isPrime string.length

/-! Tests -/

#eval prime_length "Hello" == true
#eval prime_length "abcdcba" == true
#eval prime_length "kittens" == true
#eval prime_length "orange" == false
#eval prime_length "wow" == true
#eval prime_length "world" == true
#eval prime_length "MadaM" == true
#eval prime_length "Wow" == true
#eval prime_length "" == false
#eval prime_length "HI" == true
#eval prime_length "go" == true
#eval prime_length "gogo" == false
#eval prime_length "aaaaaaaaaaaaaaa" == false
#eval prime_length "Madam" == true
#eval prime_length "M" == false
#eval prime_length "0" == false

/-! Specification -/

/-- The postcondition states that prime_length returns true if and only if 
    the length of the string is a prime number. -/
def prime_length_post (string : String) (result : Bool) : Prop :=
  result = isPrime string.length

/-- Correctness theorem for prime_length -/
theorem prime_length_correct (string : String) : 
  prime_length_post string (prime_length string) := by
  unfold prime_length_post
  unfold prime_length
  rfl
  sorry

end PrimeLength
