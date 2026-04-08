```lean
def modp (n p : Nat) : Nat :=
  let rec loop (i ret : Nat) : Nat :=
    if i < n then
      loop (i + 1) ((2 * ret) % p)
    else
      ret
  loop 0 1

-- Tests
example : modp 3 5 = 3 := by decide
example : modp 1101 101 = 2 := by decide
example : modp 0 101 = 1 := by decide
example : modp 3 11 = 8 := by decide
example : modp 100 101 = 1 := by decide
example : modp 30 5 = 4 := by decide
example : modp 31 5 = 3 := by decide

-- Specification
def modpSpec (n p : Nat) : Nat :=
  (2 ^ n) % p

theorem modp_correct (n p : Nat) (h : p > 0) : modp n p = modpSpec n p := by
  sorry
```
