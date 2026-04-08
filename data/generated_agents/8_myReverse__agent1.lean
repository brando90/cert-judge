import Batteries.Data.List.Basic
import Batteries.Misc.General
import Batteries.Lean.List
import Batteries.Tactic.Basic

namespace ReverseList

def pre (xs : List Int) : Prop := True

def post (xs result : List Int) : Prop :=
  result = xs.reverse

def prog (xs : List Int) : List Int :=
  xs.reverse

theorem prog_correct (xs : List Int) :
  pre xs → post xs (prog xs) := by
  intro h
  unfold post
  unfold prog
  rfl
  
example : prog [1, 2, 3, 4] = [4, 3, 2, 1] := rfl

example : prog [] = [] := rfl

example : prog [5] = [5] := rfl

end ReverseList
