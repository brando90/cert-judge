```lean
/- VeriBench problem: humaneval_44_change_base -/

def changeBase (x : Nat) (base : Nat) : String :=
  if x = 0 then 
    "0"
  else
    let rec buildDigits (n : Nat) (acc : String) : String :=
      if n = 0 then 
        acc
      else 
        buildDigits (n / base) (toString (n % base) ++ acc)
    buildDigits x ""

def changeBaseSpec (x : Nat) (base : Nat) : String :=
  if x = 0 then 
    "0"
  else
    let rec buildDigits (n : Nat) (acc : List Nat) : List Nat :=
      if n = 0 then 
        acc
      else 
        buildDigits (n / base) ((n % base) :: acc)
    let digits := buildDigits x []
    String.join (digits.map toString)

/-- Precondition for changeBase -/
def changeBasePre (x : Nat) (base : Nat) : Prop :=
  base > 1 && base < 10

/-- Postcondition for changeBase -/
def changeBasePost (x : Nat) (base : Nat) (result : String) : Prop :=
  result = changeBaseSpec x base

theorem changeBase_correct (x : Nat) (base : Nat)
  (h : changeBasePre x base) : 
  changeBasePost x base (changeBase x base) := 
  sorry

#eval changeBase 8 3 -- Expected: "22"
#eval changeBase 9 3 -- Expected: "100"
#eval changeBase 234 2 -- Expected: "11101010"
#eval changeBase 16 2 -- Expected: "10000"
#eval changeBase 8 2 -- Expected: "1000"
#eval changeBase 7 2 -- Expected: "111"

example : changeBase 8 3 = "22" := by rfl
example : changeBase 9 3 = "100" := by rfl
example : changeBase 234 2 = "11101010" := by rfl
example : changeBase 16 2 = "10000" := by rfl
example : changeBase 8 2 = "1000" := by rfl
example : changeBase 7 2 = "111" := by rfl
example : changeBase 2 3 = "2" := by rfl
example : changeBase 3 4 = "3" := by rfl
example : changeBase 4 5 = "4" := by rfl
example : changeBase 5 6 = "5" := by rfl
example : changeBase 6 7 = "6" := by rfl
example : changeBase 7 8 = "7" := by rfl
```
