import Lean
import Init.Data.String.Basic

namespace StringRepeat

def pre (s : String) (n : Nat) : Prop :=
  true  -- In Lean, type checking ensures s is a String and n is a Nat

def post (s : String) (n : Nat) (result : String) : Prop :=
  result = (List.replicate n s).join

def prog (s : String) (n : Nat) : String :=
  match n with
  | 0 => ""
  | _ => (List.replicate n s).join

theorem prog_correct (s : String) (n : Nat) :
  pre s n → post s n (prog s n) := by
  intro h
  unfold post
  unfold prog
  cases n with
  | zero => 
    simp [List.replicate, List.join]
  | succ n' =>
    simp [List.replicate, List.join]
    sorry

#eval prog "abc" 3 -- "abcabcabc"
#eval prog "hello" 0 -- ""
#eval prog "" 5 -- ""

example : prog "abc" 3 = "abcabcabc" := by rfl
example : prog "hello" 0 = "" := by rfl
example : prog "" 5 = "" := by rfl

end StringRepeat
