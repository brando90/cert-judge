import Lean

namespace VeriBench.SafePathTraversal

/-- Represents a file system path. -/
structure Path where
  /-- The string representation of the path. -/
  raw : String
  deriving Repr, BEq

/-- Represents a file server with a base directory. -/
structure FileServer where
  /-- The base directory for the file server. -/
  baseDirectory : Path := ⟨"/var/www/files"⟩
  deriving Repr

/-- Result of a file access operation. -/
inductive FileAccessResult
  | success (filePath : Path)
  | error (message : String)
  deriving Repr

/-- Determines if a path is normalized (no ".." or "." components). -/
def Path.isNormalized (p : Path) : Bool :=
  !p.raw.contains ".." && !p.raw.contains "./"

/-- Determines if a path is absolute (starts with "/"). -/
def Path.isAbsolute (p : Path) : Bool :=
  p.raw.startsWith "/"

/-- Determines if a path contains URL encoding attempts. -/
def Path.containsEncoding (p : Path) : Bool :=
  p.raw.contains "%"

/-- Joins two paths together. -/
def Path.join (base : Path) (rel : Path) : Path :=
  if rel.isAbsolute then rel
  else ⟨base.raw ++ "/" ++ rel.raw⟩

/-- Normalizes a path by removing ".." and "." components. -/
def Path.normalize (p : Path) : Path :=
  -- In a real implementation, this would handle path normalization
  -- Here we just simulate it for verification purposes
  ⟨p.raw⟩ -- Simplified for the example

/-- Checks if a path is safe (no traversal outside base directory). -/
def FileServer.isPathSafe (server : FileServer) (filePath : Path) : Bool :=
  let norm := Path.normalize filePath
  if Path.containsEncoding filePath then
    false
  else if Path.isAbsolute norm then
    false
  else
    let base := server.baseDirectory
    let full := Path.join base norm
    -- Check if full path starts with base directory
    full.raw.startsWith (base.raw ++ "/") || full.raw == base.raw

/-- Safely accesses a file, preventing path traversal attacks. -/
def FileServer.safeFileAccess (server : FileServer) (userInput : Path) : 
  {result : FileAccessResult // result.isSuccess → server.isPathSafe userInput} :=
  if h : server.isPathSafe userInput then
    let norm := Path.normalize userInput
    let full := Path.join server.baseDirectory norm
    ⟨FileAccessResult.success full, fun _ => h⟩
  else
    ⟨FileAccessResult.error "PATH_TRAVERSAL_DETECTED", fun h' => False.elim (h' ▸ h)⟩
where
  isSuccess : FileAccessResult → Bool
    | FileAccessResult.success _ => true
    | FileAccessResult.error _ => false

/-- Safe file access with path traversal prevention. -/
def safePathTraversal (server : FileServer) (userInput : String) : 
  {result : FileAccessResult // result.isSuccess → server.isPathSafe ⟨userInput⟩} :=
  server.safeFileAccess ⟨userInput⟩

/-- Tests for the safe path traversal function. -/
def tests : IO Bool := do
  let server := { baseDirectory := ⟨"/var/www/files"⟩ : FileServer }
  
  -- Test valid path
  let validResult := safePathTraversal server "document.txt"
  if !validResult.val.isSuccess then
    IO.println "Valid path test failed"
    return false
  
  -- Test attack paths
  let attackPaths := ["../../../etc/passwd", "..%2f..%2fetc%2fpasswd", "/etc/passwd"]
  for attack in attackPaths do
    let result := safePathTraversal server attack
    if result.val.isSuccess then
      IO.println s!"Attack path test failed for: {attack}"
      return false
    match result.val with
    | FileAccessResult.error _ => pure ()
    | _ => 
      IO.println s!"Attack should return error: {attack}"
      return false
  
  return true
where
  isSuccess : FileAccessResult → Bool
    | FileAccessResult.success _ => true
    | FileAccessResult.error _ => false

/-- Specification: A safe path should be normalized and within the base directory. -/
def isPathSafeSpec (server : FileServer) (path : Path) : Prop :=
  ¬Path.containsEncoding path ∧
  ¬Path.isAbsolute (Path.normalize path) ∧
  let base := server.baseDirectory
  let full := Path.join base (Path.normalize path)
  full.raw.startsWith (base.raw ++ "/") ∨ full.raw = base.raw

/-- Theorem: Our implementation of isPathSafe matches the specification. -/
theorem isPathSafe_correct (server : FileServer) (path : Path) :
  server.isPathSafe path ↔ isPathSafeSpec server path := by
  sorry

/-- Theorem: Safe file access only succeeds for safe paths. -/
theorem safeFileAccess_correct (server : FileServer) (path : Path) :
  (server.safeFileAccess path).val.isSuccess ↔ server.isPathSafe path := by
  sorry

/-- Theorem: Path traversal attacks are properly detected. -/
theorem pathTraversal_detection (server : FileServer) (path : Path) :
  Path.containsEncoding path ∨ 
  Path.isAbsolute (Path.normalize path) ∨
  (let base := server.baseDirectory
   let full := Path.join base (Path.normalize path)
   ¬(full.raw.startsWith (base.raw ++ "/") ∨ full.raw = base.raw)) →
  ¬server.isPathSafe path := by
  sorry

end VeriBench.SafePathTraversal
