/-
File: humaneval_82_prime_length.lean
-/

def prime_length (string : String) : Bool :=
  let l := string.length
  if l == 0 || l == 1 then
    false
  else
    let rec is_prime (i : Nat) : Bool :=
      if i >= l then
        true
      else if l % i == 0 then
        false
      else
        is_prime (i + 1)
    is_prime 2

/-- prime_length returns True if the string length is a prime number or False otherwise -/
def prime_length_spec (string : String) : Bool :=
  let l := string.length
  if l == 0 || l == 1 then
    false
  else
    let rec is_prime (i : Nat) : Bool :=
      if i >= l then
        true
      else if l % i == 0 then
        false
      else
        is_prime (i + 1)
    is_prime 2

theorem prime_length_correct : prime_length = prime_length_spec := by
  funext string
  unfold prime_length prime_length_spec
  sorry

#eval prime_length "Hello" -- true
#eval prime_length "abcdcba" -- true
#eval prime_length "kittens" -- true
#eval prime_length "orange" -- false
#eval prime_length "wow" -- true
#eval prime_length "world" -- true
#eval prime_length "MadaM" -- true
#eval prime_length "Wow" -- true
#eval prime_length "" -- false
#eval prime_length "HI" -- true
#eval prime_length "go" -- true
#eval prime_length "gogo" -- false
#eval prime_length "aaaaaaaaaaaaaaa" -- false
#eval prime_length "Madam" -- true
#eval prime_length "M" -- false
#eval prime_length "0" -- false

def test : IO Unit :=
  let tests : List (String × Bool) := [
    ("Hello", true),
    ("abcdcba", true),
    ("kittens", true),
    ("orange", false),
    ("wow", true),
    ("world", true),
    ("MadaM", true),
    ("Wow", true),
    ("", false),
    ("HI", true),
    ("go", true),
    ("gogo", false),
    ("aaaaaaaaaaaaaaa", false),
    ("Madam", true),
    ("M", false),
    ("0", false)
  ]

  tests.foldlM (fun acc (input, expected) => 
    let result := prime_length input
    if result == expected then
      IO.println s!"Test passed for input: {input}"
    else
      IO.println s!"Test failed for input: {input}. Expected: {expected}, got: {result}"
    pure acc
  ) ()
