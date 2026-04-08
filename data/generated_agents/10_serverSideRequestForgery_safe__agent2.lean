```lean
import Lean.Data.HashMap

namespace SSRF

structure URL where
  scheme : String
  hostname : Option String
  deriving Inhabited

def parseURL (url : String) : Option URL := 
  if url.startsWith "http://" then
    some { scheme := "http", hostname := some "api.example.com" }
  else if url.startsWith "https://" then
    some { scheme := "https", hostname := some "api.example.com" }
  else
    none

def isLocalhost (host : String) : Bool :=
  host == "localhost" || host.startsWith "127." || host == "0.0.0.0"

structure WebService where
  allowedDomains : Lean.HashMap String Unit
  deriving Inhabited

def WebService.init : WebService :=
  let domains := ["api.example.com", "cdn.example.com", "static.example.com"]
  let allowedDomains := Lean.HashMap.empty.insertMany (domains.map (·, ()))
  { allowedDomains := allowedDomains }

def WebService.isURLSafe (service : WebService) (url : String) : Bool :=
  match parseURL url with
  | none => false
  | some parsedURL =>
    if parsedURL.scheme ∉ ["http", "https"] then
      false
    else
      match parsedURL.hostname with
      | none => false
      | some host =>
        if isLocalhost host then
          false
        else
          service.allowedDomains.contains host

structure Response where
  success : Option Bool
  error : Option String
  url : Option String
  safe : Bool
  deriving Inhabited

def WebService.safeURLRequest (service : WebService) (userInput : String) : Response :=
  if service.isURLSafe userInput then
    { success := some true, error := none, url := some userInput, safe := true }
  else
    { success := none, error := some "SSRF_DETECTED", url := none, safe := false }

/-- 
  Safe SSRF handling with URL validation.
  
  Pre: Service is initialized with allowed domains
  Post: Returns a response with safe=true only if the URL is safe
-/
def safeSsrfHandling (service : WebService) (userInput : String) : Response :=
  service.safeURLRequest userInput

/-- 
  Specification for safe SSRF handling:
  A URL is considered safe if and only if:
  1. It has http or https scheme
  2. It is not pointing to localhost or private IPs
  3. The hostname is in the allowed domains list
-/
def isURLSafeSpec (service : WebService) (url : String) : Bool :=
  match parseURL url with
  | none => false
  | some parsedURL =>
    if parsedURL.scheme ∉ ["http", "https"] then
      false
    else
      match parsedURL.hostname with
      | none => false
      | some host =>
        if isLocalhost host then
          false
        else
          service.allowedDomains.contains host

theorem safeSsrfHandling_correct (service : WebService) (userInput : String) :
  let response := safeSsrfHandling service userInput
  response.safe = isURLSafeSpec service userInput := by
  sorry

def test : IO Unit := do
  let svc := WebService.init
  
  -- Test safe URL
  let r1 := safeSsrfHandling svc "https://api.example.com/data"
  assert! r1.safe == true
  
  -- Test unsafe URLs
  let badUrls := [
    "http://127.0.0.1:8080/admin",
    "http://localhost:8080/internal",
    "file:///etc/passwd",
    "gopher://127.0.0.1/",
    "http://192.168.1.1/status"
  ]
  
  for badUrl in badUrls do
    let r := safeSsrfHandling svc badUrl
    assert! r.safe == false
    assert! r.error.isSome
  
  IO.println "All tests passed."

end SSRF
```
