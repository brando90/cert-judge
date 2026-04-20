-- !benchmark @start import type=solution
import Mathlib
namespace FastFibonacci
-- !benchmark @end import

-- !benchmark @start solution_aux
def Matrix := Nat × Nat × Nat × Nat
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def fastFibonacci_precond (n : Nat) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
def matrixMultiply (a b : Matrix) : Matrix :=
  let (a11, a12, a21, a22) := a
  let (b11, b12, b21, b22) := b
  (a11 * b11 + a12 * b21,
   a11 * b12 + a12 * b22,
   a21 * b11 + a22 * b21,
   a21 * b12 + a22 * b22)

partial def matrixPower (matrix : Matrix) (n : Nat) : Matrix :=
  match n with
  | 0 => (1, 0, 0, 1)
  | 1 => matrix
  | n + 2 =>
    let half := matrixPower matrix ((n + 2) / 2)
    let result := matrixMultiply half half
    if (n + 2) % 2 == 0 then
      result
    else
      matrixMultiply result matrix
-- !benchmark @end code_aux

def fastFibonacci (n : Nat) (h_precond : fastFibonacci_precond (n)) : Nat :=
  -- !benchmark @start code
  match n with
  | 0 => 0
  | 1 => 1
  | n + 2 =>
    let fibMatrix : Matrix := (1, 1, 1, 0)
    let resultMatrix := matrixPower fibMatrix n
    resultMatrix.1
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def fastFibonacci_postcond (n : Nat) (result : Nat) (h_precond : fastFibonacci_precond (n)) :=
  -- !benchmark @start postcond
  (fastFibonacci 0 (by simp) = 0) ∧
  (fastFibonacci 1 (by simp) = 1) ∧
  (∀ a b c : Matrix, matrixMultiply (matrixMultiply a b) c = matrixMultiply a (matrixMultiply b c)) ∧
  (∀ m : Matrix, matrixPower m 0 = (1, 0, 0, 1)) ∧
  (result ≥ 0)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
def base_case_0_prop : Prop := fastFibonacci 0 (by simp) = 0
@[simp] theorem base_case_0_thm : base_case_0_prop := by
  sorry

def base_case_1_prop : Prop := fastFibonacci 1 (by simp) = 1
@[simp] theorem base_case_1_thm : base_case_1_prop := by
  sorry

def matrix_multiply_assoc_prop (a b c : Matrix) : Prop :=
  matrixMultiply (matrixMultiply a b) c = matrixMultiply a (matrixMultiply b c)
@[simp] theorem matrix_multiply_assoc_thm (a b c : Matrix) : matrix_multiply_assoc_prop a b c := by
  sorry

def matrix_power_zero_prop (m : Matrix) : Prop := matrixPower m 0 = (1, 0, 0, 1)
@[simp] theorem matrix_power_zero_thm (m : Matrix) : matrix_power_zero_prop m := by
  sorry

def fibonacci_nonneg_prop (n : Nat) : Prop := fastFibonacci n (by simp) ≥ 0
@[simp] theorem fibonacci_nonneg_thm (n : Nat) : fibonacci_nonneg_prop n := by
  sorry
-- !benchmark @end proof_aux

theorem fastFibonacci_spec_satisfied (n : Nat) (h_precond : fastFibonacci_precond (n)) :
    fastFibonacci_postcond (n) (fastFibonacci (n) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof