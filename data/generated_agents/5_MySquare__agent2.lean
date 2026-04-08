def pre (n : Int) : Bool :=
  n ≥ 0

def post (n : Int) (result : Int) : Bool :=
  result = n * n

def square (n : Int) : Int :=
  if pre n then
    n * n
  else
    panic! s!"Input must be a non-negative integer (got n={n})"

theorem square_correct (n : Int) : pre n → post n (square n) := by
  intro h
  unfold square
  simp [h]
  unfold post
  simp
  sorry

def test : IO Unit := do
  -- Basic unit test
  assert! (square 3 = 9)

  -- Edge unit test
  assert! (square 0 = 0)

  -- Negative (pre-violations must raise panic)
  let badInputs := [-1]
  for n in badInputs do
    let success ← IO.catchExceptions
      (do
        let _ := square n
        pure false)
      (fun _ => pure true)
    assert! success

  IO.println "All tests passed."
