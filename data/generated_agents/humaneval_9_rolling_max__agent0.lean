import Std.Data.List.Basic
import Mathlib.Data.List.Basic
import Mathlib.Data.Int.Basic

/-!
# Rolling Max

From a given list of integers, generate a list of rolling maximum element found until given moment
in the sequence.
-/

/--
Computes a list where each element is the maximum of all elements seen so far in the input list.
-/
def rollingMax (numbers : List Int) : List Int :=
  match numbers with
  | [] => []
  | x::xs => 
    let rec loop (nums : List Int) (currMax : Int) (acc : List Int) : List Int :=
      match nums with
      | [] => acc
      | y::ys => 
        let newMax := max currMax y
        loop ys newMax (acc ++ [newMax])
    loop xs x [x]

/-- Tests for `rollingMax` -/
def rollingMaxTests : List (List Int × List Int) := [
  ([], []),
  ([1, 2, 3, 4], [1, 2, 3, 4]),
  ([4, 3, 2, 1], [4, 4, 4, 4]),
  ([3, 2, 3, 100, 3], [3, 3, 3, 100, 100]),
  ([1, 2, 3, 2, 3, 4, 2], [1, 2, 3, 3, 3, 4, 4])
]

theorem rollingMaxTest : rollingMaxTests.all (fun (input, expected) => rollingMax input = expected) := by
  simp [rollingMaxTests]
  decide

/-- 
The `rollingMax` function satisfies the property that each element in the output list
is the maximum of all elements up to that point in the input list.
-/
def rollingMaxSpec (input : List Int) (output : List Int) : Prop :=
  input.length = output.length ∧
  ∀ (i : Nat), i < input.length → output[i]? = some (List.foldl max Int.min (input.take (i+1)))

/-- The `rollingMax` function satisfies its specification. -/
theorem rollingMax_correct (numbers : List Int) : 
  rollingMaxSpec numbers (rollingMax numbers) := by
  sorry
