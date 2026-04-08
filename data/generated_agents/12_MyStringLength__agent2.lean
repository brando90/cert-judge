/-
# VeriBench Artifact: String Length
-/

def stringLength (s : String) : Nat :=
  s.length

def stringLengthPre (s : String) : Prop := True

def stringLengthPost (s : String) (result : Nat) : Prop :=
  result = s.length

theorem stringLengthCorrect (s : String) (h : stringLengthPre s) :
  stringLengthPost s (stringLength s) := by
  simp [stringLengthPost, stringLength]
  sorry

-- Tests
def testStringLength : IO Unit := do
  let test1 := stringLength "hello"
  IO.println s!"Test 1: {test1}"
  assert! test1 = 5

  let test2 := stringLength ""
  IO.println s!"Test 2: {test2}"
  assert! test2 = 0

  IO.println "All tests passed!"

#eval testStringLength
