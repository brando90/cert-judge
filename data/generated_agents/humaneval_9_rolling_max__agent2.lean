/-
# VeriBench: HumanEval/9
-/

def rollingMax (numbers : List Int) : List Int :=
  let rec loop (remaining : List Int) (runningMax : Option Int) (result : List Int) : List Int :=
    match remaining with
    | [] => result.reverse
    | n :: rest =>
      let newMax := match runningMax with
        | none => n
        | some m => max m n
      loop rest (some newMax) (newMax :: result)
  
  loop numbers none []

/-!
## Specification
-/

def rollingMaxSpec (numbers : List Int) : List Int :=
  let rec loop (i : Nat) (acc : List Int) : List Int :=
    if i ≥ numbers.length then
      acc.reverse
    else
      let prefix := numbers.take (i + 1)
      let maxSoFar := prefix.foldl (fun acc x => max acc x) (prefix.get! 0)
      loop (i + 1) (maxSoFar :: acc)
  
  if numbers.isEmpty then [] else loop 0 []

theorem rollingMax_spec (numbers : List Int) :
  rollingMax numbers = rollingMaxSpec numbers := sorry

/-!
## Tests
-/

#eval rollingMax [] -- Expected: []
#eval rollingMax [1, 2, 3, 4] -- Expected: [1, 2, 3, 4]
#eval rollingMax [4, 3, 2, 1] -- Expected: [4, 4, 4, 4]
#eval rollingMax [3, 2, 3, 100, 3] -- Expected: [3, 3, 3, 100, 100]

theorem rollingMax_empty_test :
  rollingMax [] = [] := rfl

theorem rollingMax_increasing_test :
  rollingMax [1, 2, 3, 4] = [1, 2, 3, 4] := rfl

theorem rollingMax_decreasing_test :
  rollingMax [4, 3, 2, 1] = [4, 4, 4, 4] := rfl

theorem rollingMax_mixed_test :
  rollingMax [3, 2, 3, 100, 3] = [3, 3, 3, 100, 100] := rfl

/-!
## Correctness Proof
-/

theorem rollingMax_correct (numbers : List Int) :
  rollingMax numbers = rollingMaxSpec numbers := sorry
