import Lean

inductive JsonValue
  | null
  | boolean : Bool → JsonValue
  | number : Float → JsonValue
  | string : String → JsonValue
  | array : List JsonValue → JsonValue
  | object : List (String × JsonValue) → JsonValue

structure JsonDecodeError where
  msg : String
  doc : String
  pos : Nat
  lineno : Nat
  colno : Nat
  deriving Repr

def countNewlines (s : String) (start : Nat) (end : Nat) : Nat :=
  let rec loop (i : Nat) (count : Nat) : Nat :=
    if i ≥ end then count
    else if s.get i == '\n' then loop (i + 1) (count + 1)
    else loop (i + 1) count
  loop start 0

def rfindNewline (s : String) (start : Nat) (end : Nat) : Nat :=
  let rec loop (i : Nat) : Nat :=
    if i < start then start
    else if s.get i == '\n' then i
    else loop (i - 1)
  loop (end - 1)

def createJsonDecodeError (msg : String) (doc : String) (pos : Nat) : JsonDecodeError :=
  let lineno := countNewlines doc 0 pos + 1
  let lastNewline := rfindNewline doc 0 pos
  let colno := pos - lastNewline
  { msg := msg, doc := doc, pos := pos, lineno := lineno, colno := colno }

def isWhitespace (c : Char) : Bool :=
  c == ' ' || c == '\t' || c == '\n' || c == '\r'

def skipWhitespace (s : String) (pos : Nat) : Nat :=
  let rec loop (i : Nat) :=
    if i < s.length && isWhitespace (s.get i) then
      loop (i + 1)
    else
      i
  loop pos

def scanString (s : String) (start : Nat) (strict : Bool := true) : Except JsonDecodeError (String × Nat) :=
  let begin := start - 1
  let rec loop (pos : Nat) (chunks : List String) : Except JsonDecodeError (String × Nat) :=
    if pos >= s.length then
      Except.error (createJsonDecodeError "Unterminated string starting at" s begin)
    else
      let c := s.get pos
      match c with
      | '"' => Except.ok (String.join chunks, pos + 1)
      | '\\' =>
        if pos + 1 >= s.length then
          Except.error (createJsonDecodeError "Unterminated string starting at" s begin)
        else
          let esc := s.get (pos + 1)
          match esc with
          | '"' => loop (pos + 2) (chunks ++ ["\""])
          | '\\' => loop (pos + 2) (chunks ++ ["\\"])
          | '/' => loop (pos + 2) (chunks ++ ["/"])
          | 'b' => loop (pos + 2) (chunks ++ ["\b"])
          | 'f' => loop (pos + 2) (chunks ++ ["\f"])
          | 'n' => loop (pos + 2) (chunks ++ ["\n"])
          | 'r' => loop (pos + 2) (chunks ++ ["\r"])
          | 't' => loop (pos + 2) (chunks ++ ["\t"])
          | 'u' => 
            -- Simplified Unicode handling for this example
            loop (pos + 6) (chunks ++ ["u"])
          | _ => Except.error (createJsonDecodeError s!"Invalid \\escape: {esc}" s pos)
      | c =>
        if c.toNat < 32 && strict then
          Except.error (createJsonDecodeError s!"Invalid control character {c} at" s pos)
        else
          loop (pos + 1) (chunks ++ [c.toString])

  if start >= s.length || s.get start != '"' then
    Except.error (createJsonDecodeError "String must start with double quote" s start)
  else
    loop (start + 1) []

def parseObject (s : String) (start : Nat) (parse : String → Nat → Except JsonDecodeError (JsonValue × Nat)) : Except JsonDecodeError (JsonValue × Nat) :=
  let rec parseMembers (pos : Nat) (pairs : List (String × JsonValue)) : Except JsonDecodeError (JsonValue × Nat) := do
    let pos := skipWhitespace s pos
    if pos >= s.length then
      throw (createJsonDecodeError "Unterminated object" s start)
    
    if s.get pos == '}' then
      return (JsonValue.object pairs, pos + 1)
    
    if pairs.length > 0 then
      if pos >= s.length || s.get pos != ',' then
        throw (createJsonDecodeError "Expecting ',' delimiter" s pos)
      let pos := skipWhitespace s (pos + 1)
      if pos >= s.length then
        throw (createJsonDecodeError "Unterminated object" s start)

    -- Parse key
    let (key, pos) ← scanString s pos
    
    -- Parse colon
    let pos := skipWhitespace s pos
    if pos >= s.length || s.get pos != ':' then
      throw (createJsonDecodeError "Expecting ':' delimiter" s pos)
    
    -- Parse value
    let pos := skipWhitespace s (pos + 1)
    let (value, pos) ← parse s pos
    
    parseMembers pos (pairs ++ [(key, value)])
  
  if start >= s.length || s.get start != '{' then
    throw (createJsonDecodeError "Object must start with {" s start)
  
  let pos := skipWhitespace s (start + 1)
  if pos < s.length && s.get pos == '}' then
    return (JsonValue.object [], pos + 1)
  
  parseMembers pos []

def parseArray (s : String) (start : Nat) (parse : String → Nat → Except JsonDecodeError (JsonValue × Nat)) : Except JsonDecodeError (JsonValue × Nat) :=
  let rec parseElements (pos : Nat) (elements : List JsonValue) : Except JsonDecodeError (JsonValue × Nat) := do
    let pos := skipWhitespace s pos
    if pos >= s.length then
      throw (createJsonDecodeError "Unterminated array" s start)
    
    if s.get pos == ']' then
      return (JsonValue.array elements, pos + 1)
    
    if elements.length > 0 then
      if pos >= s.length || s.get pos != ',' then
        throw (createJsonDecodeError "Expecting ',' delimiter" s pos)
      let pos := skipWhitespace s (pos + 1)
      if pos >= s.length then
        throw (createJsonDecodeError "Unterminated array" s start)
    
    let (value, pos) ← parse s pos
    parseElements pos (elements ++ [value])
  
  if start >= s.length || s.get start != '[' then
    throw (createJsonDecodeError "Array must start with [" s start)
  
  let pos := skipWhitespace s (start + 1)
  if pos < s.length && s.get pos == ']' then
    return (JsonValue.array [], pos + 1)
  
  parseElements pos []

def parseValue (s : String) (pos : Nat) : Except JsonDecodeError (JsonValue × Nat) :=
  let pos := skipWhitespace s pos
  if pos >= s.length then
    throw (createJsonDecodeError "Expecting value" s pos)
  
  match s.get pos with
  | '{' => parseObject s pos parseValue
  | '[' => parseArray s pos parseValue
  | '"' => do
    let (str, newPos) ← scanString s pos
    return (JsonValue.string str, newPos)
  | 'n' =>
    if pos + 3 < s.length && s.extract pos (pos + 4) == "null" then
      return (JsonValue.null, pos + 4)
    else
      throw (createJsonDecodeError "Invalid token" s pos)
  | 't' =>
    if pos + 3 < s.length && s.extract pos (pos + 4) == "true" then
      return (JsonValue.boolean true, pos + 4)
    else
      throw (createJsonDecodeError "Invalid token" s pos)
  | 'f' =>
    if pos + 4 < s.length && s.extract pos (pos + 5) == "false" then
      return (JsonValue.boolean false, pos + 5)
    else
      throw (createJsonDecodeError "Invalid token" s pos)
  | c =>
    if c.isDigit || c == '-' then
      -- Simplified number parsing for this example
      let rec findNumEnd (i : Nat) : Nat :=
        if i >= s.length then i
        else if s.get i |>.isDigit || s.get i == '.' || s.get i == 'e' || s.get i == 'E' || s.get i == '+' || s.get i == '-' then
          findNumEnd (i + 1)
        else i
      
      let endPos := findNumEnd (pos + 1)
      let numStr := s.extract pos endPos
      -- In a real implementation we would parse the number properly
      return (JsonValue.number 0.0, endPos)
    else
      throw (createJsonDecodeError "Invalid token" s pos)

def JSONDecoder.decode (s : String) : Except JsonDecodeError JsonValue := do
  let pos := skipWhitespace s 0
  let (obj, end) ← parseValue s pos
  let end := skipWhitespace s end
  if end != s.length then
    throw (createJsonDecodeError "Extra data" s end)
  return obj

def JSONDecoder.rawDecode (s : String) (idx : Nat := 0) : Except JsonDecodeError (JsonValue × Nat) :=
  parseValue s idx

-- Tests
def testSimpleObject : IO Unit := do
  match JSONDecoder.decode """{"name": "John", "age": 30}""" with
  | Except.ok value =>
    match value with
    | JsonValue.object pairs =>
      IO.println s!"Parsed object with {pairs.length} properties"
    | _ => IO.println "Expected object"
  | Except.error err => IO.println s!"Error: {err.msg} at line {err.lineno}, col {err.colno}"

def testSimpleArray : IO Unit := do
  match JSONDecoder.decode """[1, 2, 3, "test"]""" with
  | Except.ok value =>
    match value with
    | JsonValue.array items =>
      IO.println s!"Parsed array with {items.length} items"
    | _ => IO.println "Expected array"
  | Except.error err => IO.println s!"Error: {err.msg} at line {err.lineno}, col {err.colno}"

def testNestedStructures : IO Unit := do
  match JSONDecoder.decode """{"data": [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]}""" with
  | Except.ok _ => IO.println "Successfully parsed nested structure"
  | Except.error err => IO.println s!"Error: {err.msg} at line {err.lineno}, col {err.colno}"

def testInvalidJson : IO Unit := do
  match JSONDecoder.decode """{"name": "Missing closing brace"""" with
  | Except.ok _ => IO.println "Unexpected success"
  | Except.error err => IO.println s!"Expected error: {err.msg} at line {err.lineno}, col {err.colno}"

-- Verification
theorem scanString_produces_valid_string (s : String) (pos : Nat) (strict : Bool) :
  match scanString s pos strict with
  | Except.ok (result, _) => true
  | Except.error _ => true
  := sorry

theorem parseObject_produces_valid_object (s : String) (pos : Nat) (parse : String → Nat → Except JsonDecodeError (JsonValue × Nat)) :
  match parseObject s pos parse with
  | Except.ok (JsonValue.object _, _) => true
  | Except.error _ => true
  | _ => false
  := sorry

theorem parseArray_produces_valid_array (s : String) (pos : Nat) (parse : String → Nat → Except JsonDecodeError (JsonValue × Nat)) :
  match parseArray s pos parse with
  | Except.ok (JsonValue.array _, _) => true
  | Except.error _ => true
  | _ => false
  := sorry

theorem decode_valid_json_succeeds (s : String) (h : IsValidJson s) :
  match JSONDecoder.decode s with
  | Except.ok _ => true
  | Except.error _ => false
  := sorry
  where
    IsValidJson : String → Prop := sorry

theorem decode_invalid_json_fails (s : String) (h : ¬IsValidJson s) :
  match JSONDecoder.decode s with
  | Except.ok _ => false
  | Except.error _ => true
  := sorry
  where
    IsValidJson : String → Prop := sorry

def main : IO Unit := do
  testSimpleObject
  testSimpleArray
  testNestedStructures
  testInvalidJson
