/-
# VeriBench: EvenNumbers

Return a new list containing only the even numbers from the input list.
-/

def pre (xs : List Int) : Prop :=
  true  -- No need for type checking in Lean

def post (xs : List Int) (result : List Int) : Prop :=
  ∀ x, x ∈ result → x ∈ xs ∧ x % 2 = 0

def isEven (x : Int) : Bool :=
  x % 2 = 0

def evenNumbers (xs : List Int) : List Int :=
  xs.filter isEven

theorem evenNumbers_satisfies_post (xs : List Int) : 
  post xs (evenNumbers xs) := by
  intro x h_in_result
  have h_filter : x ∈ evenNumbers xs → x ∈ xs ∧ isEven x := by
    intro h
    simp [evenNumbers] at h
    exact List.mem_filter.mp h
  have h : x ∈ xs ∧ isEven x := h_filter h_in_result
  simp [isEven] at h
  exact h
  sorry

theorem evenNumbers_empty_list :
  evenNumbers [] = [] := by
  simp [evenNumbers]
  sorry

theorem evenNumbers_no_even_numbers (xs : List Int) :
  (∀ x ∈ xs, x % 2 ≠ 0) → evenNumbers xs = [] := by
  intro h
  simp [evenNumbers]
  apply List.filter_eq_nil_iff.mpr
  intro x h_x
  simp [isEven]
  exact h x h_x
  sorry

-- Tests
example : evenNumbers [1, 2, 3, 4, 5, 6] = [2, 4, 6] := by rfl
example : evenNumbers [] = [] := by rfl
example : evenNumbers [1, 3, 5, 7] = [] := by rfl
example : evenNumbers [2, 4, 6, 8] = [2, 4, 6, 8] := by rfl
example : evenNumbers [-2, -1, 0, 1, 2] = [-2, 0, 2] := by rfl
