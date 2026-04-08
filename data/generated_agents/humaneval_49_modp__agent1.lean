```lean
def modp (n p : Nat) : Nat :=
  let rec helper (i acc : Nat) : Nat :=
    if i = 0 then
      acc
    else
      helper (i - 1) ((2 * acc) % p)
  helper n 1

/--
Return 2^n modulo p.

Precondition: p > 0
Postcondition: result = (2^n) % p
-/
def modp_spec (n p : Nat) : Nat :=
  modp n p

theorem modp_correct (n p : Nat) (h : p > 0) : 
  modp n p = (2^n) % p := sorry

-- Tests
#eval modp 3 5 -- 3
#eval modp 1101 101 -- 2
#eval modp 0 101 -- 1
#eval modp 3 11 -- 8
#eval modp 100 101 -- 1
#eval modp 30 5 -- 4
#eval modp 31 5 -- 3

-- Test assertions
example : modp 3 5 = 3 := rfl
example : modp 1101 101 = 2 := rfl
example : modp 0 101 = 1 := rfl
example : modp 3 11 = 8 := rfl
example : modp 100 101 = 1 := rfl
example : modp 30 5 = 4 := rfl
example : modp 31 5 = 3 := rfl
```
