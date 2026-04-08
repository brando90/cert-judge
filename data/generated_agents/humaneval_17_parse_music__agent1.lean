import Std.Data.List.Basic

/-- 
  Input to this function is a string representing musical notes in a special ASCII format.
  Your task is to parse this string and return a list of integers corresponding to how many beats does each
  note last.

  Here is a legend:
  'o' - whole note, lasts four beats
  'o|' - half note, lasts two beats
  '.|' - quater note, lasts one beat
-/
def parse_music (music_string : String) : List Nat :=
  let notes := music_string.splitOn " "
  notes.filterMap fun note =>
    if note == "" then
      none
    else if note == "o" then
      some 4
    else if note == "o|" then
      some 2
    else if note == ".|" then
      some 1
    else
      none

/-- Specification: parse_music should convert notes to their beat durations -/
def parse_music_spec (music_string : String) (result : List Nat) : Prop :=
  let notes := music_string.splitOn " " |>.filter (· ≠ "")
  result.length = notes.length ∧
  notes.zipWith (fun note duration => 
    (note = "o" ∧ duration = 4) ∨ 
    (note = "o|" ∧ duration = 2) ∨ 
    (note = ".|" ∧ duration = 1)
  ) result |> List.all id

/-- Correctness theorem: parse_music satisfies its specification -/
theorem parse_music_correct (music_string : String) : 
  parse_music_spec music_string (parse_music music_string) := by
  sorry

/-- Tests for parse_music -/
def test_parse_music : IO Unit := do
  assert! (parse_music "" == [])
  assert! (parse_music "o o o o" == [4, 4, 4, 4])
  assert! (parse_music ".| .| .| .|" == [1, 1, 1, 1])
  assert! (parse_music "o| o| .| .| o o o o" == [2, 2, 1, 1, 4, 4, 4, 4])
  assert! (parse_music "o| .| o| .| o o| o o|" == [2, 1, 2, 1, 4, 2, 4, 2])
  IO.println "All tests passed!"

def main : IO Unit :=
  test_parse_music
