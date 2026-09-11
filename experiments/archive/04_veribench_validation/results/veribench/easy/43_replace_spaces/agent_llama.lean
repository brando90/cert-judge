```lean
import Lean
import Std.Data.String.Basic

structure ReplaceSpacesInput where
  s : String
  deriving Repr

structure ReplaceSpacesOutput where
  result : String
  deriving Repr

def ReplaceSpacesSpec (input : ReplaceSpacesInput) (output : ReplaceSpacesOutput) : Prop :=
  output.result = input.s.replace " " "_"

def replaceSpaces (input : ReplaceSpacesInput) : ReplaceSpacesOutput :=
  { result := input.s.replace " " "_" }

theorem replaceSpaces_correct (input : ReplaceSpacesInput) :
  ReplaceSpacesSpec input (replaceSpaces input) := sorry

-- Tests
def test_replaceSpaces : IO Unit := do
  -- Basic test
  let input1 : ReplaceSpacesInput := { s := "hello world" }
  let output1 := replaceSpaces input1
  assert! output1.result == "hello_world"
  
  -- Edge case: empty string
  let input2 : ReplaceSpacesInput := { s := "" }
  let output2 := replaceSpaces input2
  assert! output2.result == ""
  
  -- No spaces
  let input3 : ReplaceSpacesInput := { s := "no-spaces" }
  let output3 := replaceSpaces input3
  assert! output3.result == "no-spaces"
  
  IO.println "All tests passed!"

#eval test_replaceSpaces
```
