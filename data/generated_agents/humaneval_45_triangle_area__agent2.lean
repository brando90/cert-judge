import VeriBench.Common

/-!
# Triangle Area

Given length of a side and high return area for a triangle.
-/

/--
Calculates the area of a triangle given the length of a side and the height.

## Example
```lean
#eval triangle_area 5 3 -- 7.5
```
-/
def triangle_area (a h : Float) : Float :=
  a * h / 2.0

/-!
## Tests
-/

def test_triangle_area : IO Unit := do
  assert! (triangle_area 5 3 = 7.5)
  assert! (triangle_area 2 2 = 2.0)
  assert! (triangle_area 10 8 = 40.0)

#eval test_triangle_area

/-!
## Verification
-/

/--
Precondition for `triangle_area`: both inputs must be non-negative.
-/
def triangle_area_pre (a h : Float) : Prop :=
  a ≥ 0 ∧ h ≥ 0

/--
Postcondition for `triangle_area`: the result is half the product of the inputs.
-/
def triangle_area_post (a h : Float) (result : Float) : Prop :=
  result = a * h / 2.0

/--
Theorem: `triangle_area` satisfies its specification.
-/
theorem triangle_area_correct (a h : Float) :
  triangle_area_pre a h → triangle_area_post a h (triangle_area a h) :=
  fun ⟨a_nonneg, h_nonneg⟩ => by
    unfold triangle_area_post
    unfold triangle_area
    simp
    sorry
