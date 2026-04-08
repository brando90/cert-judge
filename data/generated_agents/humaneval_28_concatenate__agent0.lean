```lean
def concatenate (strings : List String) : String :=
  match strings with
  | [] => ""
  | s :: rest => s ++ concatenate rest

/-- Concatenate list of strings into a single string -/
theorem concatenate_spec (strings : List String) :
  concatenate strings = String.join strings :=
  sorry

/-- Test cases for concatenate -/
def concatenate_tests : List (List String × String) := [
  ([], ""),
  (["x", "y", "z"], "xyz"),
  (["x", "y", "z", "w", "k"], "xyzwk")
]

/-- Verify that all test cases pass -/
example : List.all concatenate_tests (fun (test : List String × String) =>
  concatenate test.1 = test.2) = true :=
  by native_decide
```
