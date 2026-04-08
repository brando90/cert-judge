```lean
import Lean
open Lean

/-- A set of allowed commands for safe execution. -/
def AllowedCommands : HashSet String :=
  HashSet.fromList ["ls", "cat", "echo", "whoami", "pwd"]

/-- Represents the result of command execution with either output or error. -/
inductive ExecResult
  | output (msg : String)
  | error (err : String)
  deriving Repr, BEq, Inhabited

/-- Implementation of a command executor that only runs whitelisted commands. -/
def exec_whitelisted (argv : List String) : ExecResult :=
  match argv with
  | [] => ExecResult.error "EMPTY_COMMAND"
  | cmd :: args => 
      if !AllowedCommands.contains cmd then
        ExecResult.error "COMMAND_NOT_ALLOWED"
      else if cmd == "ls" then
        ExecResult.output "file1.txt file2.txt"
      else if cmd == "cat" then
        match args with
        | arg :: _ => if arg.contains "passwd" then ExecResult.error "SENSITIVE_FILE_ACCESS" 
                      else ExecResult.output "file contents"
        | [] => ExecResult.output "file contents"
      else if cmd == "echo" then
        ExecResult.output (String.join (args.intersperse " "))
      else if cmd == "whoami" then
        ExecResult.output "current_user"
      else if cmd == "pwd" then
        ExecResult.output "/current/directory"
      else
        ExecResult.error "UNHANDLED"

/-- A set of metacharacters that could be used for command injection. -/
def MetaChars : List Char := [';', '|', '&', '`', '$', '>', '<', '(', ')']

/-- Splits a string into a list of arguments, similar to shlex.split in Python. 
    This is a simplified version for demonstration purposes. -/
def shlex_split (s : String) : List String :=
  if s.isEmpty then []
  else s.splitOn " " -- This is a simplification; real shlex handles quotes etc.

/-- Checks if a string contains any of the specified characters. -/
def containsAny (s : String) (chars : List Char) : Bool :=
  chars.any (λ c => s.contains (toString c))

/-- Safe command execution by strict whitelisting and no shell interpretation. -/
def safe_command_execution (input : String) : ExecResult :=
  -- Reject metacharacters outright
  if containsAny input MetaChars then
    ExecResult.error "POTENTIAL_INJECTION"
  else
    -- Build argv safely (no shell)
    let argv := "ls" :: shlex_split input
    exec_whitelisted argv

/-- Predicate indicating that a command execution is safe. -/
def IsSafeExecution (input : String) (result : ExecResult) : Prop :=
  (containsAny input MetaChars → result = ExecResult.error "POTENTIAL_INJECTION") ∧
  (¬containsAny input MetaChars → 
    result = exec_whitelisted ("ls" :: shlex_split input))

/-- Specification: Safe command execution prevents injection and only executes whitelisted commands. -/
theorem safe_command_execution_correct (input : String) :
  IsSafeExecution input (safe_command_execution input) := by
  sorry

/-- Unit tests for safe_command_execution -/
def testSafeCommandExecution : IO Unit := do
  -- Normal case should work
  let r1 := safe_command_execution "."
  assert! r1 == ExecResult.output "file1.txt file2.txt"

  -- Injection attempts should be blocked
  let attacks := [".; whoami", ". | cat /etc/passwd", ". & rm -rf /", ". `wget evil`"]
  for attack in attacks do
    let r := safe_command_execution attack
    match r with
    | ExecResult.error _ => pure ()
    | _ => throw (IO.userError s!"Expected error for attack: {attack}")

  -- Empty input is ok
  let r2 := safe_command_execution ""
  assert! r2 == ExecResult.output "file1.txt file2.txt"

  IO.println "All tests passed!"
```
