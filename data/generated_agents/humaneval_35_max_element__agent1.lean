import VeriBench

namespace MaxElement

/--
  Return maximum element in the list.
  Example:
  max_element [1, 2, 3] = 3
  max_element [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] = 123
-/
def max_element (l: List Int) : Int :=
  match l with
  | [] => 0 -- Default value for empty list (not in the specification)
  | x::xs => 
    let rec helper (m: Int) (remaining: List Int) : Int :=
      match remaining with
      | [] => m
      | e::es => 
        if e > m then
          helper e es
        else
          helper m es
    helper x xs

-- Precondition: the list must be non-empty
def pre (l: List Int) : Prop :=
  l ≠ []

-- Postcondition: the result is in the list and no element in the list is greater than the result
def post (l: List Int) (result: Int) : Prop :=
  result ∈ l ∧ ∀ e ∈ l, e ≤ result

-- Tests
example : max_element [1, 2, 3] = 3 := rfl
example : max_element [5, 3, -5, 2, -3, 3, 9, 0, 123, 1, -10] = 123 := rfl
example : max_element [5, 3, -5, 2, -3, 3, 9, 0, 124, 1, -10] = 124 := rfl

-- Correctness theorem
theorem max_element_correct (l: List Int) (h: pre l) : post l (max_element l) := sorry

end MaxElement
