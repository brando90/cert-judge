-- !benchmark @start import type=solution
import Mathlib
namespace SumProduct
-- !benchmark @end import

-- !benchmark @start solution_aux
def helper (nums : List Int) (sum prod : Int) : Int × Int :=
  match nums with
  | [] => (sum, prod)
  | n :: rest => helper rest (sum + n) (prod * n)

def empty_list_prop : Prop := sumProduct [] = (0, 1)

@[simp] theorem empty_list_thm : empty_list_prop := by
  sorry

def singleton_prop (n : Int) : Prop := sumProduct [n] = (n, n)

@[simp] theorem singleton_thm (n : Int) : singleton_prop n := by
  sorry

def cons_prop (x : Int) (xs : List Int) : Prop :=
  let (s, p) := sumProduct xs
  sumProduct (x :: xs) = (x + s, x * p)

@[simp] theorem cons_thm (x : Int) (xs : List Int) : cons_prop x xs := by
  sorry

def zero_product_prop (numbers : List Int) : Prop :=
  (0 ∈ numbers) → (sumProduct numbers).2 = 0

@[simp] theorem zero_product_thm (numbers : List Int) : zero_product_prop numbers := by
  sorry

def append_prop (xs ys : List Int) : Prop :=
  let (s1, p1) := sumProduct xs
  let (s2, p2) := sumProduct ys
  sumProduct (xs ++ ys) = (s1 + s2, p1 * p2)

@[simp] theorem append_thm (xs ys : List Int) : append_prop xs ys := by
  sorry
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def sumProduct_precond (numbers : List Int) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def sumProduct (numbers : List Int) (h_precond : sumProduct_precond (numbers)) : Int × Int :=
  -- !benchmark @start code
  helper numbers 0 1
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def sumProduct_postcond (numbers : List Int) (result : Int × Int)
    (h_precond : sumProduct_precond (numbers)) : Prop :=
  -- !benchmark @start postcond
  (empty_list_prop) ∧
    (∀ n, singleton_prop n) ∧
    (∀ x xs, cons_prop x xs) ∧
    (zero_product_prop numbers) ∧
    (∀ xs ys, append_prop xs ys)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem sumProduct_spec_satisfied (numbers : List Int) (h_precond : sumProduct_precond (numbers)) :
    sumProduct_postcond (numbers) (sumProduct (numbers) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof