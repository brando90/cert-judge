import Mathlib

namespace FindClosestElements


def findClosestElements (numbers : List Float) : Float × Float :=
  match numbers with
  | [] => (0.0, 0.0)  -- Default case, should not occur given precondition
  | [x] => (x, x)     -- Default case, should not occur given precondition
  | x :: y :: xs =>
    let initial_pair := if x ≤ y then (x, y) else (y, x)
    let initial_dist := Float.abs (x - y)
    
    let rec findMin (remaining : List Float) (best_pair : Float × Float) (min_dist : Float) : Float × Float :=
      match remaining with
      | [] => best_pair
      | a :: rest =>
        let rec checkAgainstAll (elem : Float) (toCheck : List Float) (curr_best : Float × Float) (curr_min : Float) : Float × Float :=
          match toCheck with
          | [] => curr_best
          | b :: others =>
            let dist := Float.abs (elem - b)
            let ordered_pair := if elem ≤ b then (elem, b) else (b, elem)
            if dist < curr_min then
              checkAgainstAll elem others ordered_pair dist
            else
              checkAgainstAll elem others curr_best curr_min
        
        let new_best_pair := checkAgainstAll a (x :: y :: xs) best_pair min_dist
        let new_min_dist := Float.abs (new_best_pair.1 - new_best_pair.2)
        findMin rest new_best_pair new_min_dist
    
    findMin xs initial_pair initial_dist


def findClosestElementsImp (numbers : List Float) : Float × Float :=
  match numbers with
  | [] => (0.0, 0.0)
  | [x] => (x, x)
  | x :: xs =>
    let arr := numbers.toArray
    let n := arr.size
    if n < 2 then (0.0, 0.0)
    else
      let mut min_dist := Float.abs (arr[0]! - arr[1]!)
      let mut result := if arr[0]! ≤ arr[1]! then (arr[0]!, arr[1]!) else (arr[1]!, arr[0]!)
      
      for i in [:n] do
        for j in [i+1:n] do
          let dist := Float.abs (arr[i]! - arr[j]!)
          if dist < min_dist then
            min_dist := dist
            result := if arr[i]! ≤ arr[j]! then (arr[i]!, arr[j]!) else (arr[j]!, arr[i]!)
      
      result



/-!
# Tests
-/

/-- expected: (3.9, 4.0) -/
example : findClosestElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] = (3.9, 4.0) := by sorry
#eval findClosestElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2]

/-- expected: (5.0, 5.9) -/
example : findClosestElements [1.0, 2.0, 5.9, 4.0, 5.0] = (5.0, 5.9) := by sorry
#eval findClosestElements [1.0, 2.0, 5.9, 4.0, 5.0]

/-!
# Tests: Edge Cases
-/

/-- expected: (2.0, 2.2) -/
example : findClosestElements [1.0, 2.0, 3.0, 4.0, 5.0, 2.2] = (2.0, 2.2) := by sorry
#eval findClosestElements [1.0, 2.0, 3.0, 4.0, 5.0, 2.2]

/-- expected: (1.0, 2.0) -/
example : findClosestElements [1.0, 2.0] = (1.0, 2.0) := by sorry
#eval findClosestElements [1.0, 2.0]

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: finds actual closest pair -/
example : findClosestElements [10.0, 1.0, 1.1, 20.0] = (1.0, 1.1) := by sorry
#eval findClosestElements [10.0, 1.0, 1.1, 20.0] -- expected: (1.0, 1.1)

/-- positive: handles negative numbers -/
example : findClosestElements [-1.0, 0.0, 1.0] = (-1.0, 0.0) := by sorry
#eval findClosestElements [-1.0, 0.0, 1.0] -- expected: (-1.0, 0.0)

/-- negative: doesn't return same element twice for different indices -/
example : ¬ (findClosestElements [1.0, 2.0, 3.0] = (1.0, 1.0)) := by sorry
#eval findClosestElements [1.0, 2.0, 3.0] -- should not be (1.0, 1.0)

/-- negative: order matters in result -/
example : ¬ (findClosestElements [2.0, 1.0] = (2.0, 1.0)) := by sorry
#eval findClosestElements [2.0, 1.0] -- should be (1.0, 2.0), not (2.0, 1.0)

/-!
# Positive / Negative Test‑Suite
-/

/-- positive: three elements -/
example : findClosestElementsImp [1.0, 3.0, 2.0] = (1.0, 2.0) := by sorry
#eval findClosestElementsImp [1.0, 3.0, 2.0] -- expected: (1.0, 2.0)

/-- negative: doesn't return unordered pair -/
example : ¬ (findClosestElementsImp [1.0, 2.0] = (2.0, 1.0)) := by sorry
#eval findClosestElementsImp [1.0, 2.0] -- should be (1.0, 2.0), not (2.0, 1.0)

/-- **Equivalence theorem**: functional and imperative implementations coincide. -/
theorem findClosestElements_equivalence_thm (numbers : List Float) :
  findClosestElements numbers = findClosestElementsImp numbers := sorry




end FindClosestElements