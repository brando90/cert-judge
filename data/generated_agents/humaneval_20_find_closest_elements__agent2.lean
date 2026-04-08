import Mathlib.Data.Real.Basic
import Mathlib.Data.List.Basic
import Mathlib.Data.List.Nodup

/--
From a supplied list of numbers (of length at least two) select and return two that are the closest to each
other and return them in order (smaller number, larger number).
-/
def find_closest_elements (numbers : List Float) : Float × Float :=
  let rec helper (idx : Nat) (numbers : List Float) (closest_pair : Option (Float × Float)) (distance : Option Float) : Float × Float :=
    match idx with
    | 0 => 
      match closest_pair with
      | some pair => pair
      | none => (0.0, 0.0) -- Should never happen given the precondition
    | idx + 1 =>
      match numbers with
      | [] => helper idx [] closest_pair distance
      | elem :: rest =>
        let (new_closest_pair, new_distance) := 
          List.foldl (fun (acc, min_dist) elem2 =>
            if elem = elem2 then (acc, min_dist)
            else
              let new_dist := Float.abs (elem - elem2)
              match min_dist with
              | none => ((min elem elem2, max elem elem2), some new_dist)
              | some dist =>
                if new_dist < dist then
                  ((min elem elem2, max elem elem2), some new_dist)
                else
                  (acc, min_dist)
          ) (closest_pair, distance) numbers
        helper idx rest new_closest_pair new_distance
  
  helper (numbers.length) numbers none none

/-- The list must have at least two elements -/
def find_closest_elements_pre (numbers : List Float) : Prop :=
  numbers.length ≥ 2

/-- The returned pair contains two elements from the list in ascending order that have the minimum distance -/
def find_closest_elements_post (numbers : List Float) (result : Float × Float) : Prop :=
  let (a, b) := result
  a ≤ b ∧ 
  (a ∈ numbers) ∧ 
  (b ∈ numbers) ∧
  (∀ x y : Float, x ∈ numbers → y ∈ numbers → x ≠ y → Float.abs (x - y) ≥ Float.abs (a - b))

theorem find_closest_elements_correct (numbers : List Float) :
  find_closest_elements_pre numbers → find_closest_elements_post numbers (find_closest_elements numbers) :=
  sorry

#eval find_closest_elements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2] -- (3.9, 4.0)
#eval find_closest_elements [1.0, 2.0, 5.9, 4.0, 5.0] -- (5.0, 5.9)
#eval find_closest_elements [1.0, 2.0, 3.0, 4.0, 5.0, 2.2] -- (2.0, 2.2)
#eval find_closest_elements [1.0, 2.0, 3.0, 4.0, 5.0, 2.0] -- (2.0, 2.0)
#eval find_closest_elements [1.1, 2.2, 3.1, 4.1, 5.1] -- (2.2, 3.1)
