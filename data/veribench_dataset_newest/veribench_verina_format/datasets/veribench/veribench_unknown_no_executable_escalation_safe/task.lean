-- !benchmark @start import type=solution
import Mathlib
namespace SafeExecution
-- !benchmark @end import

-- !benchmark @start solution_aux
/--
Whitelisted program specification.

Represents a validated program that can be safely executed.
Each program in the whitelist has known, safe behavior patterns.
-/
structure ProgramSpec where
  name : String
  description : String
  deriving Repr, DecidableEq

/--
Safe program execution structure.

Represents the exact argv vector that will be passed to execve().
Combines whitelisted program with validated user arguments.
-/
structure SafeProgramExecution where
  prog : String
  args : List String
  deriving Repr, DecidableEq
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
/--
Secure whitelist of allowed programs.

Only these programs are permitted for execution:
- "cat" → safe file reading utility
- "ls" → safe directory listing utility
- "echo" → safe text output utility
- "wc" → safe word/line counting utility
-/
def program_whitelist : List ProgramSpec := [
  { name := "cat", description := "Safe file reading" },
  { name := "ls", description := "Safe directory listing" },
  { name := "echo", description := "Safe text output" },
  { name := "wc", description := "Safe word/line counting" }
]

/--
Validate program name against whitelist.
-/
def is_program_whitelisted (prog_name : String) : Bool :=
  program_whitelist.any (fun spec => spec.name = prog_name)

/--
Safely tokenize user arguments.
-/
def tokenize_arguments (args : String) : List String :=
  if args.trim.isEmpty then []
  else args.splitOn " " |>.filter (· ≠ "")
-- !benchmark @end precond_aux

@[reducible, simp]
def execute_program_safe_precond (prog_name : String) (args : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def execute_program_safe (prog_name : String) (args : String)
    (h_precond : execute_program_safe_precond (prog_name) (args)) : Option SafeProgramExecution :=
  -- !benchmark @start code
  if is_program_whitelisted prog_name then
    let user_args := tokenize_arguments args
    some { prog := prog_name, args := user_args }
  else
    none
  -- !benchmark @end code

-- !benchmark @start postcond_aux

-- !benchmark @end postcond_aux

@[reducible, simp]
def execute_program_safe_postcond (prog_name : String) (args : String)
    (result : Option SafeProgramExecution)
    (h_precond : execute_program_safe_precond (prog_name) (args)) :=
  -- !benchmark @start postcond
  (whitelist_enforcement_prop prog_name args) ∧
  (program_isolation_prop prog_name args) ∧
  (dangerous_program_rejection_prop prog_name args) ∧
  (injection_containment_prop prog_name args)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Whitelist enforcement property**: Only whitelisted programs can execute -/
def whitelist_enforcement_prop (prog_name : String) (args : String) : Prop :=
  (∃ exec, execute_program_safe prog_name args (by simp) = some exec) →
    is_program_whitelisted prog_name = true

/-- **Whitelist enforcement theorem**: Only whitelisted programs can execute -/
theorem whitelist_enforcement_thm (prog_name : String) (args : String) :
    whitelist_enforcement_prop prog_name args := by
  sorry

/-- **Program isolation property**: Executed program matches exactly what was requested -/
def program_isolation_prop (prog_name : String) (args : String) : Prop :=
  ∀ exec, execute_program_safe prog_name args (by simp) = some exec → exec.prog = prog_name

/-- **Program isolation theorem**: Executed program matches exactly what was requested -/
theorem program_isolation_thm (prog_name : String) (args : String) :
    program_isolation_prop prog_name args := by
  sorry

/-- **Dangerous program rejection property**: Dangerous binaries are never executed -/
def dangerous_program_rejection_prop (dangerous_prog : String) (args : String) : Prop :=
  is_program_whitelisted dangerous_prog = false →
    execute_program_safe dangerous_prog args (by simp) = none

/-- **Dangerous program rejection theorem**: Dangerous binaries are never executed -/
theorem dangerous_program_rejection_thm (dangerous_prog : String) (args : String) :
    dangerous_program_rejection_prop dangerous_prog args := by
  sorry

/-- **Injection containment property**: Shell metacharacters become literal arguments -/
def injection_containment_prop (prog_name : String) (attack : String) : Prop :=
  is_program_whitelisted prog_name = true →
    ∀ exec, execute_program_safe prog_name attack (by simp) = some exec →
      ∀ token ∈ tokenize_arguments attack, token ∈ exec.args

/-- **Injection containment theorem**: Shell metacharacters become literal arguments -/
theorem injection_containment_thm (prog_name : String) (attack : String) :
    injection_containment_prop prog_name attack := by
  sorry
-- !benchmark @end proof_aux

theorem execute_program_safe_spec_satisfied (prog_name : String) (args : String)
    (h_precond : execute_program_safe_precond (prog_name) (args)) :
    execute_program_safe_postcond (prog_name) (args)
      (execute_program_safe (prog_name) (args) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof