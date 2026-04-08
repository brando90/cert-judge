```lean
import Lean
import Std.Data.List.Basic

def parseMusic (musicString : String) : List Nat := 
  let noteMap := fun (note : String) =>
    match note with
    | "o" => 4
    | "o|" => 2
    | ".|" => 1
    | _ => 0  -- This shouldn't happen with valid input
  
  let notes := musicString.split (· == ' ')
  notes.filter (fun s => !s.isEmpty).map noteMap

/-- Specification for parseMusic: Maps each note in a music string to its duration in beats
    - 'o' - whole note, lasts four beats
    - 'o|' - half note, lasts two beats
    - '.|' - quarter note, lasts one beat
-/
def parseMusicSpec (musicString : String) : List Nat :=
  let noteMap := fun (note : String) =>
    match note with
    | "o" => 4
    | "o|" => 2
    | ".|" => 1
    | _ => 0
  
  let notes := musicString.split (· == ' ')
  notes.filter (fun s => !s.isEmpty).map noteMap

theorem parseMusicCorrect (musicString : String) : 
  parseMusic musicString = parseMusicSpec musicString := by
  sorry

#eval parseMusic "" -- []
#eval parseMusic "o o o o" -- [4, 4, 4, 4]
#eval parseMusic ".| .| .| .|" -- [1, 1, 1, 1]
#eval parseMusic "o| o| .| .| o o o o" -- [2, 2, 1, 1, 4, 4, 4, 4]
#eval parseMusic "o| .| o| .| o o| o o|" -- [2, 1, 2, 1, 4, 2, 4, 2]

example : parseMusic "" = [] := rfl
example : parseMusic "o o o o" = [4, 4, 4, 4] := rfl
example : parseMusic ".| .| .| .|" = [1, 1, 1, 1] := rfl
example : parseMusic "o| o| .| .| o o o o" = [2, 2, 1, 1, 4, 4, 4, 4] := rfl
example : parseMusic "o| .| o| .| o o| o o|" = [2, 1, 2, 1, 4, 2, 4, 2] := rfl
```
