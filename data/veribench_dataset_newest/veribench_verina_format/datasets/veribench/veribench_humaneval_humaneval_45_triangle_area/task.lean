-- !benchmark @start import type=solution
import Mathlib
namespace TriangleArea
-- !benchmark @end import

-- !benchmark @start solution_aux

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def triangle_area_precond (a : Float) (h : Float) : Prop :=
  -- !benchmark @start precond
  a ≥ 0.0 ∧ h ≥ 0.0
  -- !benchmark @end precond


-- !benchmark @start code_aux

-- !benchmark @end code_aux


def triangle_area (a : Float) (h : Float) (h_precond : triangle_area_precond (a) (h)) : Float :=
  -- !benchmark @start code
  a * h / 2.0
  -- !benchmark @end code


-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux


-- Property definitions / theorems needed by the postcondition
def zero_base_prop (h : Float) : Prop := triangle_area (0.0) (h) (by sorry) = 0.0
@[simp] theorem zero_base_thm (h : Float) : zero_base_prop h := by sorry

def zero_height_prop (a : Float) : Prop := triangle_area (a) (0.0) (by sorry) = 0.0
@[simp] theorem zero_height_thm (a : Float) : zero_height_prop a := by sorry

def positive_area_prop (a h : Float) : Prop :=
  a > 0.0 → h > 0.0 → triangle_area (a) (h) (by sorry) > 0.0
@[simp] theorem positive_area_thm (a h : Float) : positive_area_prop a h := by sorry

def scaling_prop (a h k : Float) : Prop :=
  triangle_area (k * a) (k * h) (by sorry) = k * k * triangle_area (a) (h) (by sorry)
@[simp] theorem scaling_thm (a h k : Float) : scaling_prop a h k := by sorry


@[reducible, simp]
def triangle_area_postcond (a : Float) (h : Float) (result : Float) (h_precond : triangle_area_precond (a) (h)) :=
  -- !benchmark @start postcond
  (zero_base_prop h) ∧
  (zero_height_prop a) ∧
  (positive_area_prop a h) ∧
  (∀ k, scaling_prop a h k)
  -- !benchmark @end postcond


-- !benchmark @start proof_aux

-- !benchmark @end proof_aux


theorem triangle_area_spec_satisfied (a : Float) (h : Float) (h_precond : triangle_area_precond (a) (h)) :
    triangle_area_postcond (a) (h) (triangle_area (a) (h) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof