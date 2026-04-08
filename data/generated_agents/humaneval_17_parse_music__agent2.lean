```lean
import Lean
import Std.Data.List.Basic
import Mathlib.Tactic

/-- 
  `parse_music` takes a string representing musical notes in a special ASCII format
  and returns a list of integers corresponding to how many beats each note lasts.
  
  Legend:
  - 'o' - whole note, lasts four beats
  - 'o|' - half note, lasts two beats
  - '.|' - quater note, lasts one beat
-/
def parse_music (music_string : String) : List Nat :=
  let notes := music_string.split (· == ' ')
  notes.filterMap fun note => 
    if note == "" then none
    else if note == "o" then some 4
    else if note == "o|" then some 2
    else if note == ".|" then some 1
    else none

/-- Specification: parse_music maps each valid note to its duration -/
def parse_music_spec (music_string : String) : List Nat :=
  let notes := music_string.split (· == ' ')
  notes.filterMap fun note => 
    match note with
    | "o" => some 4
    | "o|" => some 2
    | ".|" => some 1
    | "" => none
    | _ => none

/-- Precondition: The input string should only contain valid notes or empty spaces -/
def parse_music_pre (music_string : String) : Prop :=
  let notes := music_string.split (· == ' ')
  notes.all fun note => note == "" || note == "o" || note == "o|" || note == ".|"

/-- Postcondition: The output list contains the correct durations for each valid note -/
def parse_music_post (music_string : String) (result : List Nat) : Prop :=
  result = parse_music_spec music_string

theorem parse_music_correct (music_string : String) 
  (h : parse_music_pre music_string) : 
  parse_music_post music_string (parse_music music_string) := by
  sorry

#eval parse_music "" -- []
#eval parse_music "o o o o" -- [4, 4, 4, 4]
#eval parse_music ".| .| .| .|" -- [1, 1, 1, 1]
#eval parse_music "o| o| .| .| o o o o" -- [2, 2, 1, 1, 4, 4, 4, 4]
#eval parse_music "o| .| o| .| o o| o o|" -- [2, 1, 2, 1, 4, 2, 4, 2]

def test_parse_music : IO Unit := do
  let test1 := parse_music "" == []
  let test2 := parse_music "o o o o" == [4, 4, 4, 4]
  let test3 := parse_music ".| .| .| .|" == [1, 1, 1, 1]
  let test4 := parse_music "o| o| .| .| o o o o" == [2, 2, 1, 1, 4, 4, 4, 4]
  let test5 := parse_music "o| .| o| .| o o| o o|" == [2, 1, 2, 1, 4, 2, 4, 2]
  
  if test1 && test2 && test3 && test4 && test5 then
    IO.println "All tests passed!"
  else
    IO.println "Tests failed!"

#eval test_parse_music
```
