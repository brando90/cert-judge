import Std.Data.List.Basic

/-- Check if in given list of numbers, are any two numbers closer to each other
    than given threshold. -/
def hasCloseElements (numbers : List Float) (threshold : Float) : Bool :=
  let rec check (idx : Nat) (rest : List Float) : Bool :=
    match rest with
    | [] => false
    | elem :: rest' =>
      let rec checkAgainst (idx2 : Nat) (rest2 : List Float) : Bool :=
        match rest2 with
        | [] => check (idx + 1) rest'
        | elem2 :: rest2' =>
          if idx != idx2 then
            let distance := Float.abs (elem - elem2)
            if distance < threshold then
              true
            else
              checkAgainst (idx2 + 1) rest2'
          else
            checkAgainst (idx2 + 1) rest2'
      checkAgainst 0 numbers
  check 0 numbers

/-- Specification for hasCloseElements -/
def hasCloseElementsSpec (numbers : List Float) (threshold : Float) : Bool :=
  List.any (fun i => 
    List.any (fun j => 
      i.1 != j.1 && Float.abs (i.2 - j.2) < threshold
    ) (List.enum numbers)
  ) (List.enum numbers)

/-- Precondition: threshold must be non-negative -/
def hasCloseElementsPre (numbers : List Float) (threshold : Float) : Prop :=
  threshold >= 0

/-- Postcondition: hasCloseElements returns true if and only if there exist
    two distinct elements in the list that are closer than the threshold -/
def hasCloseElementsPost (numbers : List Float) (threshold : Float) (result : Bool) : Prop :=
  result = hasCloseElementsSpec numbers threshold

theorem hasCloseElements_correct (numbers : List Float) (threshold : Float)
  (h : hasCloseElementsPre numbers threshold) :
  hasCloseElementsPost numbers threshold (hasCloseElements numbers threshold) :=
  sorry

#eval hasCloseElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] 0.3 -- true
#eval hasCloseElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] 0.05 -- false
#eval hasCloseElements [1.0, 2.0, 5.9, 4.0, 5.0] 0.95 -- true
#eval hasCloseElements [1.0, 2.0, 5.9, 4.0, 5.0] 0.8 -- false
#eval hasCloseElements [1.0, 2.0, 3.0, 4.0, 5.0, 2.0] 0.1 -- true
#eval hasCloseElements [1.1, 2.2, 3.1, 4.1, 5.1] 1.0 -- true
#eval hasCloseElements [1.1, 2.2, 3.1, 4.1, 5.1] 0.5 -- false
#eval hasCloseElements [] 0.1 -- false
#eval hasCloseElements [1.5] 0.1 -- false
#eval hasCloseElements [3.14, 3.14] 0.1 -- true
#eval hasCloseElements [3.14, 3.14] 0.0 -- false
#eval hasCloseElements [100, 200] 999.9 -- true
#eval hasCloseElements [1.0, 1.00000001] 0.00001 -- true
#eval hasCloseElements [1.0, 1.0002] 0.00001 -- false
