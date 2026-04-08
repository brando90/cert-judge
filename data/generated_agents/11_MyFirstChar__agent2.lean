import VeriBench

namespace FirstChar

inductive Str where
  | string : String → Str
  deriving BEq, Repr

def pre (s : Str) : Prop :=
  match s with
  | Str.string str => str.length > 0

def prog (s : Str) : Option Str :=
  match s with
  | Str.string str => 
    if str.length > 0 then
      some (Str.string (str.get 0).toString)
    else
      none

def post (s : Str) (result : Str) : Prop :=
  match s with
  | Str.string str => result = Str.string (str.get 0).toString

theorem prog_correct (s : Str) : pre s → match prog s with
  | some result => post s result
  | none => ¬ pre s
  := by sorry

def test : IO Unit := do
  -- Basic test
  let hello := Str.string "hello"
  assert! prog hello == some (Str.string "h")
  
  -- Edge test
  let singleChar := Str.string "A"
  assert! prog singleChar == some (Str.string "A")
  
  -- Pre-violation test
  let empty := Str.string ""
  assert! prog empty == none
  
  IO.println "All tests passed"

end FirstChar
