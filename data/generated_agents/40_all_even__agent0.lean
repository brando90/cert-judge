import Lean.Data.HashMap
import Std.Data.List.Basic

def List.all {α : Type} (p : α → Bool) : List α → Bool
  | [] => true
  | (x :: xs) => p x && all p xs

def allEven (xs : List Int) : Bool :=
  List.all (fun x => x % 2 == 0) xs

def allEvenPreCond (xs : List Int) : Prop := True

def allEvenPostCond (xs : List Int) (result : Bool) : Prop :=
  result = List.all (fun x => x % 2 == 0) xs

theorem allEvenCorrect (xs : List Int) (h : allEvenPreCond xs) : 
  allEvenPostCond xs (allEven xs) := by
  unfold allEvenPostCond
  unfold allEven
  rfl

-- Tests
example : allEven [2, 4, 6] = true := rfl
example : allEven [1, 2, 4] = false := rfl
example : allEven [] = true := rfl
