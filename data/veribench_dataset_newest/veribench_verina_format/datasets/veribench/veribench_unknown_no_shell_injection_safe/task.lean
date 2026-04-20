-- !benchmark @start import type=solution
import Mathlib
namespace SafeLS
-- !benchmark @end import

-- !benchmark @start solution_aux
structure Command where
  prog : String
  args : List String
deriving Repr, DecidableEq
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def listFilesSafe_precond (path : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def listFilesSafe (path : String) (h_precond : listFilesSafe_precond (path)) : SafeLS.Command :=
  -- !benchmark @start code
  { prog := "ls", args := ["--", path] }
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def listFilesSafe_postcond (path : String) (result : SafeLS.Command) (h_precond : listFilesSafe_precond (path)) : Prop :=
  -- !benchmark @start postcond
  result.prog = "ls" ∧
    result.args.head? = some "--" ∧
    result.args.length = 2 ∧
    result.args.getD 1 "" = path
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
def executable_isolation_prop (arbitrary_input : String) : Prop :=
  (listFilesSafe arbitrary_input (by simp)).prog = "ls"

@[simp] theorem executable_isolation_thm (arbitrary_input : String) : executable_isolation_prop arbitrary_input := by
  sorry

def argument_sentinel_prop (arbitrary_input : String) : Prop :=
  (listFilesSafe arbitrary_input (by simp)).args.head? = some "--"

@[simp] theorem argument_sentinel_thm (arbitrary_input : String) : argument_sentinel_prop arbitrary_input := by
  sorry

def argument_count_prop (arbitrary_input : String) : Prop :=
  (listFilesSafe arbitrary_input (by simp)).args.length = 2

@[simp] theorem argument_count_thm (arbitrary_input : String) : argument_count_prop arbitrary_input := by
  sorry

def path_isolation_prop (arbitrary_input : String) : Prop :=
  (listFilesSafe arbitrary_input (by simp)).args.getD 1 "" = arbitrary_input

@[simp] theorem path_isolation_thm (arbitrary_input : String) : path_isolation_prop arbitrary_input := by
  sorry
-- !benchmark @end proof_aux

theorem listFilesSafe_spec_satisfied (path : String) (h_precond : listFilesSafe_precond (path)) :
    listFilesSafe_postcond (path) (listFilesSafe (path) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof