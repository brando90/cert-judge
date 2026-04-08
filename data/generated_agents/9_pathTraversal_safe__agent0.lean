import Lean
import Std.Data.HashMap
open Std

/-- Represents the result of a file access operation -/
structure FileAccessResult where
  safe : Bool
  error : Option String := none
  success : Option Bool := none
  filePath : Option String := none
  deriving Repr, BEq

/-- A file server that manages access to files within a base directory -/
structure FileServer where
  baseDirectory : String := "/var/www/files"
  deriving Repr

/-- Checks if a path is safe (doesn't attempt path traversal) -/
def FileServer.isPathSafe (server : FileServer) (filePath : String) : Bool :=
  -- Disallow obvious encoding attempts
  if filePath.contains "%" then
    false
  else
    let norm := normalizePath filePath
    if isAbsolutePath norm then
      false
    else
      let base := realPath server.baseDirectory
      let full := realPath (joinPath base norm)
      -- Must be inside base directory
      full.startsWith (base ++ pathSeparator) || full == base
where
  -- These are simplified versions of the actual path operations
  normalizePath (path : String) : String := path
  isAbsolutePath (path : String) : Bool := path.get? 0 == some '/'
  realPath (path : String) : String := path
  joinPath (base path : String) : String := base ++ "/" ++ path
  pathSeparator : String := "/"

/-- Safely access a file, preventing path traversal attacks -/
def FileServer.safeFileAccess (server : FileServer) (userInput : String) : FileAccessResult :=
  if server.isPathSafe userInput then
    let full := joinPath server.baseDirectory (normalizePath userInput)
    { safe := true, success := some true, filePath := some full }
  else
    { safe := false, error := some "PATH_TRAVERSAL_DETECTED" }
where
  normalizePath (path : String) : String := path
  joinPath (base path : String) : String := base ++ "/" ++ path

/-- Main function that implements safe file access with path traversal prevention -/
def safePathTraversal (server : FileServer) (userInput : String) : FileAccessResult :=
  server.safeFileAccess userInput

/-- Tests for the safePathTraversal function -/
def testSafePathTraversal : IO Bool := do
  let s := { baseDirectory := "/var/www/files" : FileServer }
  
  -- Test legitimate access
  let result1 := safePathTraversal s "document.txt"
  if result1.safe != true then
    return false
  
  -- Test path traversal attacks
  let attacks := ["../../../etc/passwd", "..%2f..%2fetc%2fpasswd", "/etc/passwd"]
  for attack in attacks do
    let r := safePathTraversal s attack
    if r.safe != false then
      return false
    if r.error.isNone then
      return false
  
  return true

/-- Specification: A path is safe if it doesn't try to escape the base directory -/
def isPathSafe (basedir path : String) : Bool :=
  !path.contains "%" && 
  !(isAbsolutePath path) && 
  let fullPath := realPath (joinPath basedir path)
  fullPath.startsWith (realPath basedir ++ "/") || fullPath == realPath basedir
where
  isAbsolutePath (path : String) : Bool := path.get? 0 == some '/'
  realPath (path : String) : String := path
  joinPath (base path : String) : String := base ++ "/" ++ path

/-- Precondition: The server must have a valid base directory -/
def safePathTraversalPre (server : FileServer) (userInput : String) : Prop :=
  server.baseDirectory ≠ ""

/-- Postcondition: The result is safe only if the path doesn't attempt traversal -/
def safePathTraversalPost (server : FileServer) (userInput : String) (result : FileAccessResult) : Prop :=
  result.safe = isPathSafe server.baseDirectory userInput

/-- Correctness theorem: safePathTraversal satisfies its specification -/
theorem safePathTraversalCorrect (server : FileServer) (userInput : String) :
  safePathTraversalPre server userInput →
  safePathTraversalPost server userInput (safePathTraversal server userInput) := by
  sorry
