```lean
import Lean
import Std.Data.List.Basic

namespace VeriBench

structure User where
  id : Nat
  username : String
  password : String
  email : String
  deriving Repr

structure DatabaseSimulator where
  users : List User
  deriving Repr

def DatabaseSimulator.init : DatabaseSimulator :=
  { users := [
    { id := 1, username := "admin", password := "admin123", email := "admin@example.com" },
    { id := 2, username := "user1", password := "pass123", email := "user1@example.com" },
    { id := 3, username := "user2", password := "pass456", email := "user2@example.com" }
  ] }

/--
Safe user lookup without SQL string concatenation. No injection possible.
-/
def safe_sql_query (db : DatabaseSimulator) (username : String) : List User :=
  db.users.filter (fun u => u.username == username)

/-! Specification -/

/--
Predicate indicating that the result of a query contains only users with the specified username.
-/
def ResultsHaveUsername (results : List User) (username : String) : Prop :=
  ∀ user ∈ results, user.username = username

/--
Predicate indicating that the result of a query contains all users with the specified username.
-/
def ResultsContainAllMatches (db : DatabaseSimulator) (results : List User) (username : String) : Prop :=
  ∀ user ∈ db.users, user.username = username → user ∈ results

/-! Tests -/

def testNormalLookup : IO Bool := do
  let db := DatabaseSimulator.init
  let result := safe_sql_query db "admin"
  return result.length == 1 && (result[0]!).username == "admin"

def testInjectionAttempts : IO Bool := do
  let db := DatabaseSimulator.init
  let injections := [
    "admin' OR '1'='1",
    "admin'--",
    "admin' UNION SELECT * FROM users--",
    "admin'; DROP TABLE users;--",
    "admin'; SELECT * FROM users;--",
    ""
  ]
  
  for inj in injections do
    let result := safe_sql_query db inj
    -- Should return nothing, except exact username match
    if !(result == []) then
      return false
  
  return true

def runAllTests : IO Bool := do
  let test1 ← testNormalLookup
  let test2 ← testInjectionAttempts
  return test1 && test2

/-! Correctness theorem -/

theorem safe_sql_query_correct (db : DatabaseSimulator) (username : String) :
  let results := safe_sql_query db username
  ResultsHaveUsername results username ∧ ResultsContainAllMatches db results username := by
  sorry

end VeriBench
```
