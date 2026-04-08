import Lean
import Init.Data.String.Basic

/-- Command executor that only allows specific whitelisted commands -/
structure CommandExecutor where
  allowed_commands : List String := ["ls", "cat", "echo", "whoami", "pwd"]
  
/-- Result of command execution -/
inductive CommandResult
  | output (msg : String)
  | error (msg : String)
  deriving Repr, BEq

/-- Execute a whitelisted command -/
def CommandExecutor.exec_whitelisted (self : CommandExecutor) (argv : List String) : CommandResult :=
  if argv.isEmpty then
    CommandResult.error "EMPTY_COMMAND"
  else if !argv.head!.elem self.allowed_commands then
    CommandResult.error "COMMAND_NOT_ALLOWED"
  else
    match argv.head! with
    | "ls" => CommandResult.output "file1.txt file2.txt"
    | "cat" => 
        if argv.length > 1 && argv[1]!.contains "passwd" then
          CommandResult.error "SENSITIVE_FILE_ACCESS"
        else
          CommandResult.output "file contents"
    | "echo" => 
        let output := String.intercalate " " (argv.tail!)
        CommandResult.output output
    | "whoami" => CommandResult.output "current_user"
    | "pwd" => CommandResult.output "/current/directory"
    | _ => CommandResult.error "UNHANDLED"

/-- Check if a string contains any of the dangerous metacharacters -/
def containsMetachar (s : String) : Bool :=
  let metachars := [';', '|', '&', '`', '$', '>', '<', '(', ')']
  metachars.any (fun c => s.contains c.toString)

/-- Simplified shlex.split implementation for Lean -/
def shlex.split (s : String) : List String :=
  if s.isEmpty then []
  else s.splitOn " " -- simplified for this example

/-- Safe command execution by strict whitelisting and no shell interpretation -/
def safe_command_execution (executor : CommandExecutor) (user_input : String) : CommandResult :=
  -- Reject metacharacters outright
  if containsMetachar user_input then
    CommandResult.error "POTENTIAL_INJECTION"
  else
    -- Build argv safely (no shell)
    let argv := ["ls"]
    let extra := shlex.split user_input
    let argv := argv ++ extra
    executor.exec_whitelisted argv

/-- Precondition for safe command execution -/
def safe_command_execution.pre (executor : CommandExecutor) (user_input : String) : Prop :=
  executor.allowed_commands.length > 0

/-- Postcondition for safe command execution -/
def safe_command_execution.post (executor : CommandExecutor) (user_input : String) 
    (result : CommandResult) : Prop :=
  -- If input contains metacharacters, result must be an error
  (containsMetachar user_input → ∃ msg, result = CommandResult.error msg) ∧
  -- If command is not in allowed list, result must be an error
  (let argv := ["ls"] ++ shlex.split user_input;
   argv.isEmpty ∨ !argv.head!.elem executor.allowed_commands → 
   ∃ msg, result = CommandResult.error msg)

/-- Tests for the safe_command_execution function -/
def test_safe_command_execution : IO Unit := do
  let ex := { allowed_commands := ["ls", "cat", "echo", "whoami", "pwd"] : CommandExecutor }
  
  -- Basic test
  let r1 := safe_command_execution ex "."
  assert! (match r1 with | CommandResult.output _ => true | _ => false)
  
  -- Injection attempts
  let attacks := [".; whoami", ". | cat /etc/passwd", ". & rm -rf /", ". `wget evil`"]
  for attack in attacks do
    let r := safe_command_execution ex attack
    assert! (match r with | CommandResult.error _ => true | _ => false)
  
  -- Empty input
  let r2 := safe_command_execution ex ""
  assert! (match r2 with | CommandResult.output _ => true | _ => false)
  
  IO.println "All tests passed."

/-- Theorem stating the correctness of safe_command_execution -/
theorem safe_command_execution_correct (executor : CommandExecutor) (user_input : String) :
  safe_command_execution.pre executor user_input →
  safe_command_execution.post executor user_input (safe_command_execution executor user_input) :=
  sorry
