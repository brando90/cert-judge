```lean
import Lean.Data.HashMap
import Std.Data.List.Basic

open Lean

namespace SafeCommandExecution

/-- Represents the result of command execution -/
inductive CommandResult
  | output : String → CommandResult
  | error : String → CommandResult

instance : ToString CommandResult where
  toString
    | CommandResult.output s => s"output: {s}"
    | CommandResult.error s => s"error: {s}"

/-- Converts CommandResult to a dictionary-like representation -/
def CommandResult.toDict (r : CommandResult) : HashMap String String :=
  match r with
  | CommandResult.output s => HashMap.empty.insert "output" s
  | CommandResult.error s => HashMap.empty.insert "error" s

/-- Checks if a CommandResult contains an output -/
def CommandResult.hasOutput (r : CommandResult) : Bool :=
  match r with
  | CommandResult.output _ => true
  | _ => false

/-- Checks if a CommandResult contains an error -/
def CommandResult.hasError (r : CommandResult) : Bool :=
  match r with
  | CommandResult.error _ => true
  | _ => false

/-- Class for executing whitelisted commands -/
structure CommandExecutor where
  allowedCommands : List String := ["ls", "cat", "echo", "whoami", "pwd"]

/-- Executes a whitelisted command -/
def CommandExecutor.execWhitelisted (executor : CommandExecutor) (argv : List String) : CommandResult :=
  match argv with
  | [] => CommandResult.error "EMPTY_COMMAND"
  | cmd :: args =>
    if !executor.allowedCommands.contains cmd then
      CommandResult.error "COMMAND_NOT_ALLOWED"
    else
      match cmd with
      | "ls" => CommandResult.output "file1.txt file2.txt"
      | "cat" =>
          match args with
          | arg :: _ => if arg.contains "passwd" then CommandResult.error "SENSITIVE_FILE_ACCESS"
                        else CommandResult.output "file contents"
          | [] => CommandResult.output "file contents"
      | "echo" => CommandResult.output (String.join (" " :: args))
      | "whoami" => CommandResult.output "current_user"
      | "pwd" => CommandResult.output "/current/directory"
      | _ => CommandResult.error "UNHANDLED"

/-- Splits a string into a list of arguments, similar to shlex.split -/
def shlex_split (s : String) : List String :=
  if s.isEmpty then []
  else s.split (· == ' ')

/-- Checks if a string contains any of the specified characters -/
def containsAny (s : String) (chars : List Char) : Bool :=
  chars.any (λ c => s.contains (toString c))

/-- Safely executes a command based on user input -/
def safeCommandExecution (executor : CommandExecutor) (userInput : String) : CommandResult :=
  -- Reject metacharacters outright
  if containsAny userInput [';', '|', '&', '`', '$', '>', '<', '(', ')'] then
    CommandResult.error "POTENTIAL_INJECTION"
  else
    -- Build argv safely (no shell)
    let argv := ["ls"] ++ shlex_split userInput
    executor.execWhitelisted argv

/-!
  Specification and Verification
-/

/-- Precondition: userInput should be a valid string -/
def safeCommandExecution.pre (executor : CommandExecutor) (userInput : String) : Prop := True

/-- Postcondition: If the input contains metacharacters, an error is returned -/
def safeCommandExecution.post (executor : CommandExecutor) (userInput : String) (result : CommandResult) : Prop :=
  (containsAny userInput [';', '|', '&', '`', '$', '>', '<', '(', ')'] → result.hasError) ∧
  (userInput.isEmpty → result.hasOutput)

/-- Correctness theorem for safeCommandExecution -/
theorem safeCommandExecution.correct (executor : CommandExecutor) (userInput : String) :
  safeCommandExecution.pre executor userInput →
  safeCommandExecution.post executor userInput (safeCommandExecution executor userInput) :=
  sorry

/-!
  Tests
-/

def testSafeCommandExecution : IO Unit := do
  let executor := { allowedCommands := ["ls", "cat", "echo", "whoami", "pwd"] : CommandExecutor }
  
  -- Normal case
  let result1 := safeCommandExecution executor "."
  assert! result1.hasOutput
  
  -- Injection attempts should be blocked
  let attacks := [".; whoami", ". | cat /etc/passwd", ". & rm -rf /", ". `wget evil`"]
  for attack in attacks do
    let result := safeCommandExecution executor attack
    assert! result.hasError
  
  -- Empty input is ok
  let result2 := safeCommandExecution executor ""
  assert! result2.hasOutput
  
  IO.println "All tests passed."

end SafeCommandExecution
```
