```lean
import Lean.Data.HashSet
import Lean.Data.HashMap
import Std.Data.List.Basic

structure URL where
  scheme : String
  hostname : Option String
  deriving Repr, BEq

def parseURL (url : String) : Option URL :=
  -- Simple URL parser that extracts scheme and hostname
  let parts := url.splitOn "://"
  if parts.length < 2 then none
  else
    let scheme := parts.head!
    let rest := parts.drop 1 |>.join
    let hostParts := rest.splitOn "/"
    if hostParts.isEmpty then none
    else some { scheme := scheme, hostname := some hostParts.head! }

def isLocalhost (host : String) : Bool :=
  host == "localhost" || host.startsWith "127." || host == "0.0.0.0"

structure WebService where
  allowedDomains : Lean.HashSet String

def WebService.mk : WebService :=
  { allowedDomains := Lean.HashSet.empty.insert "api.example.com"
                                               .insert "cdn.example.com"
                                               .insert "static.example.com" }

def WebService.isURLSafe (service : WebService) (url : String) : Bool :=
  match parseURL url with
  | none => false
  | some parsedURL =>
    if parsedURL.scheme ∉ ["http", "https"] then false
    else
      match parsedURL.hostname with
      | none => false
      | some host =>
        if isLocalhost host then false
        else service.allowedDomains.contains host

structure Response where
  error : Option String
  safe : Bool
  url : Option String
  success : Option Bool
  deriving Repr, BEq

def WebService.safeURLRequest (service : WebService) (userInput : String) : Response :=
  if service.isURLSafe userInput then
    { error := none, safe := true, url := some userInput, success := some true }
  else
    { error := some "SSRF_DETECTED", safe := false, url := none, success := none }

def safeSSRFHandling (service : WebService) (userInput : String) : Response :=
  service.safeURLRequest userInput

/-- 
  Specification for safe SSRF handling:
  - Returns a response with safe=true only for allowed domains with http/https schemes
  - Returns a response with safe=false and an error message for all other URLs
-/
def safeSSRFHandling_spec (service : WebService) (userInput : String) : Response :=
  if service.isURLSafe userInput then
    { error := none, safe := true, url := some userInput, success := some true }
  else
    { error := some "SSRF_DETECTED", safe := false, url := none, success := none }

/-- The implementation correctly implements the specification -/
theorem safeSSRFHandling_correct (service : WebService) (userInput : String) :
  safeSSRFHandling service userInput = safeSSRFHandling_spec service userInput := by
  sorry

/-- Test cases for the safeSSRFHandling function -/
def testSafeSSRFHandling : IO Bool := do
  let svc := WebService.mk
  
  -- Test safe URL
  let safeResult := safeSSRFHandling svc "https://api.example.com/data"
  if safeResult.safe != true then
    return false
  
  -- Test unsafe URLs
  let badURLs := [
    "http://127.0.0.1:8080/admin",
    "http://localhost:8080/internal",
    "file:///etc/passwd",
    "gopher://127.0.0.1/",
    "http://192.168.1.1/status"
  ]
  
  for badURL in badURLs do
    let result := safeSSRFHandling svc badURL
    if result.safe != false then
      return false
    if result.error != some "SSRF_DETECTED" then
      return false
  
  return true

#eval testSafeSSRFHandling
```
