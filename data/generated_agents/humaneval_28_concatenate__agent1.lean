```lean
/--
  Concatenate list of strings into a single string.
-/
def concatenate (strings : List String) : String :=
  String.join strings

/--
  Tests for the concatenate function.
-/
def concatenateTests : IO Unit := do
  assert! (concatenate [] == "")
  assert! (concatenate ["x", "y", "z"] == "xyz")
  assert! (concatenate ["x", "y", "z", "w", "k"] == "xyzwk")
  IO.println "All tests passed!"

/--
  Specification: concatenate should join all strings in the list.
-/
theorem concatenate_spec (strings : List String) : 
  concatenate strings = String.join strings := by
  unfold concatenate
  rfl

#eval concatenateTests
```
