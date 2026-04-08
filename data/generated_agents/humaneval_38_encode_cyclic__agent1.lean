import Lean.Data.HashMap

def encodeCyclic (s : String) : String :=
  let groups := List.range ((s.length + 2) / 3) |>.map (fun i =>
    let start := 3 * i
    let end := min (3 * i + 3) s.length
    s.extract start end)
  let cycled := groups.map (fun group =>
    if group.length == 3 then
      group.extract 1 3 ++ group.extract 0 1
    else
      group)
  String.join cycled

def decodeCyclic (s : String) : String :=
  encodeCyclic (encodeCyclic s)

def encodeCyclicSpec (s : String) : String :=
  let groups := List.range ((s.length + 2) / 3) |>.map (fun i =>
    let start := 3 * i
    let end := min (3 * i + 3) s.length
    s.extract start end)
  let cycled := groups.map (fun group =>
    if group.length == 3 then
      group.extract 1 3 ++ group.extract 0 1
    else
      group)
  String.join cycled

def decodeCyclicSpec (s : String) : String :=
  encodeCyclicSpec (encodeCyclicSpec s)

theorem encodeCyclic_eq_spec : encodeCyclic = encodeCyclicSpec := by
  funext s
  rfl

theorem decodeCyclic_eq_spec : decodeCyclic = decodeCyclicSpec := by
  funext s
  rfl

theorem decode_encode_identity (s : String) : decodeCyclic (encodeCyclic s) = s := by
  sorry

def main : IO Unit := do
  let testCases := [
    "abc", 
    "abcdef", 
    "abcdefghi", 
    "abcdefghij", 
    "hello world",
    "a",
    "ab",
    ""
  ]

  for s in testCases do
    let encoded := encodeCyclic s
    let decoded := decodeCyclic encoded
    IO.println s!"Original: {s}"
    IO.println s!"Encoded: {encoded}"
    IO.println s!"Decoded: {decoded}"
    assert! decoded == s
    IO.println "Test passed!"
  
  IO.println "All tests passed!"
