```lean
def pre (s : String) : Bool :=
  true  -- In Lean, we don't need type checking as the type system enforces it

def reverseWord (word : String) : String :=
  String.mk (List.reverse (String.toList word))

def reverseWords (s : String) : String :=
  String.join (List.intersperse " " (List.map reverseWord (String.split s (· == ' '))))

def post (s : String) (result : String) : Bool :=
  let words := String.split s (· == ' ')
  let reversedWords := List.map reverseWord words
  result = String.join (List.intersperse " " reversedWords)

theorem reverseWords_correct (s : String) : post s (reverseWords s) := by
  sorry

-- Tests
example : reverseWords "hello world" = "olleh dlrow" := by
  rfl

example : reverseWords "" = "" := by
  rfl

example : reverseWords "lean is great" = "nael si taerg" := by
  rfl
```
