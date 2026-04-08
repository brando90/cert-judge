```lean
def duplicateChars (s : String) : String :=
  let rec duplicate (cs : List Char) : List Char :=
    match cs with
    | [] => []
    | c::cs' => c::c::(duplicate cs')
  String.mk (duplicate s.toList)

/-- Specification for duplicateChars -/
def duplicateCharsSpec (s : String) : String :=
  s.fold (init := "") (fun acc c => acc ++ String.mk [c, c])

/-- Precondition: input is a string (always true in Lean) -/
def duplicateCharsPre (_s : String) : Prop :=
  True

/-- Postcondition: each character in the input is duplicated in the output -/
def duplicateCharsPost (s : String) (result : String) : Prop :=
  result = duplicateCharsSpec s

theorem duplicateChars_correct (s : String) (h : duplicateCharsPre s) :
  duplicateCharsPost s (duplicateChars s) := sorry

-- Tests
#eval duplicateChars "abc" -- "aabbcc"
#eval duplicateChars "" -- ""
#eval duplicateChars "!a " -- "!!aa  "

example : duplicateChars "abc" = "aabbcc" := rfl
example : duplicateChars "" = "" := rfl
example : duplicateChars "!a " = "!!aa  " := rfl
```
