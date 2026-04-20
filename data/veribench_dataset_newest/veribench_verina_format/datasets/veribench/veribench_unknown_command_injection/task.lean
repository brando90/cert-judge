-- !benchmark @start import type=solution
import Mathlib
namespace SafeCommand
-- !benchmark @end import

-- !benchmark @start solution_aux
/--
Whitelisted command specification.

Represents a validated command that can be safely executed.
Each command has a fixed program and base arguments.
-/
structure CommandSpec where
  prog : String
  base_args : List String
  deriving Repr, DecidableEq

/--
Safe command execution structure.

Represents the exact argv vector that will be passed to execve().
Combines whitelisted command with validated user arguments.
-/
structure SafeExecution where
  prog : String
  args : List String
  deriving Repr, DecidableEq

/--
Secure whitelist of allowed commands.
-/
def command_whitelist : List (String × CommandSpec) := [
  ("list", { prog := "ls", base_args := ["--"] }),
  ("count", { prog := "wc", base_args := ["-l", "--"] }),
  ("search", { prog := "grep", base_args := ["-r", "--"] })
]

/--
Validate command name against whitelist.
-/
def validate_command (cmd_name : String) : Option CommandSpec :=
  command_whitelist.lookup cmd_name

/--
Safely tokenize user arguments.
-/
def tokenize_args (args : String) : List String :=
  if args.trim.isEmpty then []
  else args.splitOn " " |>.filter (· ≠ "")
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def execute_command_safe_precond (cmd_name : String) (args : String) : Prop :=
  -- !benchmark @start precond
  True
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def execute_command_safe (cmd_name : String) (args : String)
    (h_precond : execute_command_safe_precond (cmd_name) (args)) : Option SafeExecution :=
  -- !benchmark @start code
  match validate_command cmd_name with
  | none => none
  | some spec =>
    let user_args := tokenize_args args
    let full_args := spec.base_args ++ user_args
    some { prog := spec.prog, args := full_args }
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def execute_command_safe_postcond (cmd_name : String) (args : String) (result : Option SafeExecution)
    (h_precond : execute_command_safe_precond (cmd_name) (args)) : Prop :=
  -- !benchmark @start postcond
  whitelist_validation_prop cmd_name ∧
    program_isolation_prop cmd_name args ∧
      dangerous_program_rejection_prop cmd_name args ∧ injection_containment_prop cmd_name args
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
/-- **Whitelist validation property**: Only whitelisted commands are executed -/
def whitelist_validation_prop (cmd_name : String) : Prop :=
  validate_command cmd_name ≠ none ↔ cmd_name ∈ command_whitelist.map (·.1)

/-- **Whitelist validation theorem**: Only whitelisted commands are executed -/
theorem whitelist_validation_thm (cmd_name : String) : whitelist_validation_prop cmd_name := by
  sorry

/-- **Program isolation property**: Executed program matches whitelist specification -/
def program_isolation_prop (cmd_name : String) (args : String) : Prop :=
  ∀ exec, execute_command_safe cmd_name args (by simp) = some exec →
    ∃ spec, validate_command cmd_name = some spec ∧ exec.prog = spec.prog

/-- **Program isolation theorem**: Executed program matches whitelist specification -/
theorem program_isolation_thm (cmd_name : String) (args : String) : program_isolation_prop cmd_name args := by
  sorry

/-- **Dangerous program rejection property**: Dangerous binaries are never executed -/
def dangerous_program_rejection_prop (dangerous_prog : String) (args : String) : Prop :=
  dangerous_prog ∉ command_whitelist.map (·.1) → execute_command_safe dangerous_prog args (by simp) = none

/-- **Dangerous program rejection theorem**: Dangerous binaries are never executed -/
theorem dangerous_program_rejection_thm (dangerous_prog : String) (args : String) :
    dangerous_program_rejection_prop dangerous_prog args := by
  sorry

/-- **Injection containment property**: Shell metacharacters become literal arguments -/
def injection_containment_prop (cmd_name : String) (attack : String) : Prop :=
  cmd_name ∈ command_whitelist.map (·.1) →
    ∀ exec,
      execute_command_safe cmd_name attack (by simp) = some exec →
        ∀ token ∈ tokenize_args attack, token ∈ exec.args

/-- **Injection containment theorem**: Shell metacharacters become literal arguments -/
theorem injection_containment_thm (cmd_name : String) (attack : String) : injection_containment_prop cmd_name attack := by
  sorry
-- !benchmark @end proof_aux

theorem execute_command_safe_spec_satisfied (cmd_name : String) (args : String)
    (h_precond : execute_command_safe_precond (cmd_name) (args)) :
    execute_command_safe_postcond (cmd_name) (args) (execute_command_safe (cmd_name) (args) h_precond) h_precond := by
  -- !benchmark @start proof
  sorry
  -- !benchmark @end proof