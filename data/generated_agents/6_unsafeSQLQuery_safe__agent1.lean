import Lean
import Std.Data.List.Basic
import Std.Data.HashMap
import Std.Data.List.Lemmas
import Std.Classes.SetNotation

namespace VeriBench.SafeSQLQuery

structure User where
  id : Nat
  username : String
  password : String
  email : String
  deriving Repr, BEq

structure DatabaseSimulator where
  users : List User
  deriving Repr

def users_init : List User := [
  { id := 1, username := "admin", password := "admin123", email := "admin@example.com" },
  { id := 2, username := "user1", password := "pass123", email := "user1@example.com" },
  { id := 3, username := "user2", password := "pass456", email := "user2@example.com" }
]

/--
  Safe user lookup without SQL string concatenation. No injection possible.
-/
def safe_sql_query (db : DatabaseSimulator) (username : String) : List User :=
  db.users.filter (fun u => u.username == username)

/-- Tests for safe_sql_query -/
def test_safe_sql_query : Bool :=
  let db := { users := users_init }
  
  -- Normal query
  let r1 := safe_sql_query db "admin"
  let test1 := r1.length == 1 && r1[0]!.username == "admin"
  
  -- Injection attempts
  let injections := [
    "admin' OR '1'='1",
    "admin'--",
    "admin' UNION SELECT * FROM users--",
    "admin'; DROP TABLE users;--",
    "admin'; SELECT * FROM users;--",
    ""
  ]
  
  let inj_tests := injections.all (fun inj => 
    let r := safe_sql_query db inj
    r == [])
  
  test1 && inj_tests

#eval test_safe_sql_query -- Should return true

/-- Specification: safe_sql_query returns only users with the exact username match -/
theorem safe_sql_query_correct (db : DatabaseSimulator) (username : String) :
  ∀ user ∈ safe_sql_query db username, user.username = username :=
  fun user h => 
    have : user ∈ db.users.filter (fun u => u.username = username) := h
    List.mem_filter.mp this |>.2
    
/-- Specification: safe_sql_query is complete -/
theorem safe_sql_query_complete (db : DatabaseSimulator) (username : String) :
  ∀ user ∈ db.users, user.username = username → user ∈ safe_sql_query db username :=
  fun user h1 h2 => 
    List.mem_filter.mpr ⟨h1, h2⟩

/-- 
  Specification: safe_sql_query is immune to SQL injection since it uses 
  direct filtering instead of string concatenation
-/
theorem safe_sql_query_no_injection (db : DatabaseSimulator) (injection : String) :
  (∀ user ∈ db.users, user.username ≠ injection) → 
  safe_sql_query db injection = [] :=
  fun h => 
    List.filter_eq_nil_iff.mpr (fun user h_mem => 
      not_and_or.mpr (Or.inr (h user h_mem))
    )

end VeriBench.SafeSQLQuery
