```lean
import Lean
import Std.Data.RBMap

namespace VeriBench

structure URL where
  scheme : String
  hostname : Option String
  deriving Repr

def parseURL (url : String) : Option URL :=
  if url.startsWith "http://" || url.startsWith "https://" then
    let scheme := if url.startsWith "http://" then "http" else "https"
    let domainStart := if url.startsWith "http://" then 7 else 8
    let pathStart := url.find (fun c => c == '/' || c == '?' || c == '#') domainStart
    let domain := if pathStart > domainStart then url.extract domainStart pathStart else url.extract domainStart url.length
    some { scheme := scheme, hostname := some domain }
  else
    none

structure WebService where
  allowedDomains : List String
  deriving Repr

def WebService.init : WebService :=
  { allowedDomains := ["api.example.com", "cdn.example.com", "static.example.com"] }

def isLocalhostOrPrivate (host : String) : Bool :=
  host == "localhost" || host.startsWith "127." || host == "0.0.0.0"

def WebService.isURLSafe (service : WebService) (url : String) : Bool :=
  match parseURL url with
  | none => false
  | some parsedURL => 
    if parsedURL.scheme ∉ ["http", "https"] then false
    else match parsedURL.hostname with
      | none => false
      | some host => 
        if isLocalhostOrPrivate host then false
        else service.allowedDomains.contains host

structure Response where
  error : Option String
  success : Option Bool
  url : Option String
  safe : Bool
  deriving Repr

def WebService.safeURLRequest (service : WebService) (userInput : String) : Response :=
  if service.isURLSafe userInput then
    { error := none, success := some true, url := some userInput, safe := true }
  else
    { error := some "SSRF_DETECTED", success := none, url := none, safe := false }

def safeSsrfHandling (service : WebService) (userInput : String) : Response :=
  service.safeURLRequest userInput

/-- Precondition: service must be initialized with proper allowed domains -/
def safeSsrfHandlingPre (service : WebService) (userInput : String) : Prop :=
  service.allowedDomains.length > 0

/-- Postcondition: if the URL is not safe, the response must indicate it's unsafe -/
def safeSsrfHandlingPost (service : WebService) (userInput : String) (response : Response) : Prop :=
  (¬service.isURLSafe userInput → response.safe = false) ∧
  (response.safe = false → response.error = some "SSRF_DETECTED") ∧
  (service.isURLSafe userInput → response.safe = true)

/-- The safe_ssrf_handling function correctly detects and blocks unsafe URLs -/
theorem safeSsrfHandlingCorrect (service : WebService) (userInput : String)
  (h : safeSsrfHandlingPre service userInput) :
  safeSsrfHandlingPost service userInput (safeSsrfHandling service userInput) := by
  sorry

def test : IO Unit := do
  let svc := WebService.init
  
  -- Test safe URL
  let safeResult := safeSsrfHandling svc "https://api.example.com/data"
  assert! safeResult.safe == true
  
  -- Test unsafe URLs
  let testUnsafeURL (url : String) : IO Unit := do
    let result := safeSsrfHandling svc url
    assert! result.safe == false
    assert! result.error == some "SSRF_DETECTED"
  
  testUnsafeURL "http://127.0.0.1:8080/admin"
  testUnsafeURL "http://localhost:8080/internal"
  testUnsafeURL "file:///etc/passwd"
  testUnsafeURL "gopher://127.0.0.1/"
  testUnsafeURL "http://192.168.1.1/status"
  
  IO.println "All tests passed."

end VeriBench

#eval VeriBench.test
```
