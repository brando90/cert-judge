import Lean

namespace VeriBench.BisectRight

inductive Option (α : Type u) where
  | none : Option α
  | some : α → Option α

def Option.map {α β : Type} (f : α → β) : Option α → Option β
  | Option.none => Option.none
  | Option.some a => Option.some (f a)

def Option.get {α : Type} (default : α) : Option α → α
  | Option.none => default
  | Option.some a => a

def bisect_right {T K : Type} [LT K] [DecidableRel (@LT.lt K _)]
    (a : List T) (x : K) (lo : Nat := 0) (hi : Option Nat := Option.none)
    (key : Option (T → K) := Option.none) : Nat :=
  if lo < 0 then
    panic! "lo must be non-negative"
  else
    let hi := hi.get a.length
    match key with
    | Option.none =>
      let rec loop (lo : Nat) (hi : Nat) : Nat :=
        if lo < hi then
          let mid := (lo + hi) / 2
          if x < a[mid]! then
            loop lo mid
          else
            loop (mid + 1) hi
        else
          lo
      loop lo hi
    | Option.some key =>
      let rec loop (lo : Nat) (hi : Nat) : Nat :=
        if lo < hi then
          let mid := (lo + hi) / 2
          if x < key (a[mid]!) then
            loop lo mid
          else
            loop (mid + 1) hi
        else
          lo
      loop lo hi

def insort_right {T K : Type} [LT K] [DecidableRel (@LT.lt K _)]
    (a : List T) (x : T) (lo : Nat := 0) (hi : Option Nat := Option.none)
    (key : Option (T → K) := Option.none) : List T :=
  if lo < 0 then
    panic! "lo must be non-negative"
  else
    let idx := match key with
      | Option.none => bisect_right a x lo hi Option.none
      | Option.some k => bisect_right a (k x) lo hi key
    a.take idx ++ (x :: a.drop idx)

/-- Specification for bisect_right: Return the index where to insert item x in list a, assuming a is sorted.
    The return value i is such that all e in a[:i] have e <= x, and all e in a[i:] have e > x. -/
def bisect_right_spec {T K : Type} [LT K] [DecidableRel (@LT.lt K _)]
    (a : List T) (x : K) (lo : Nat) (hi : Option Nat) (key : Option (T → K)) (result : Nat) : Prop :=
  let hi := hi.get a.length
  lo <= result ∧ result <= hi ∧
  (∀ i, lo <= i → i < result → 
    match key with
    | Option.none => ¬(x < a[i]!)
    | Option.some k => ¬(x < k (a[i]!))
  ) ∧
  (∀ i, result <= i → i < hi → 
    match key with
    | Option.none => x < a[i]!
    | Option.some k => x < k (a[i]!)
  )

/-- Specification for insort_right: Insert item x in list a, and keep it sorted assuming a is sorted. -/
def insort_right_spec {T K : Type} [LT K] [DecidableRel (@LT.lt K _)] [Ord T]
    (a : List T) (x : T) (lo : Nat) (hi : Option Nat) (key : Option (T → K)) (result : List T) : Prop :=
  let idx := match key with
    | Option.none => bisect_right a x lo hi Option.none
    | Option.some k => bisect_right a (k x) lo hi key
  result = a.take idx ++ (x :: a.drop idx)

theorem bisect_right_correct {T K : Type} [LT K] [DecidableRel (@LT.lt K _)]
    (a : List T) (x : K) (lo : Nat) (hi : Option Nat) (key : Option (T → K)) :
    bisect_right_spec a x lo hi key (bisect_right a x lo hi key) := by
  sorry

theorem insort_right_correct {T K : Type} [LT K] [DecidableRel (@LT.lt K _)] [Ord T]
    (a : List T) (x : T) (lo : Nat) (hi : Option Nat) (key : Option (T → K)) :
    insort_right_spec a x lo hi key (insort_right a x lo hi key) := by
  sorry

-- Tests
def test_bisect_right : IO Bool := do
  let a1 := [1, 2, 4, 4, 10]
  let r1 := bisect_right a1 4
  let r2 := bisect_right a1 0
  let r3 := bisect_right a1 99
  
  let a2 := ["A", "bb", "CC", "ddd"]
  let key := (fun s => s.length)
  let r4 := bisect_right a2 1 0 Option.none (Option.some key)
  let r5 := bisect_right a2 2 0 Option.none (Option.some key)
  let r6 := bisect_right a2 3 0 Option.none (Option.some key)
  
  return r1 == 4 && r2 == 0 && r3 == 5 && r4 == 1 && r5 == 3 && r6 == 4

def test_insort_right : IO Bool := do
  let a1 := [1, 2, 4, 4, 10]
  let r1 := insort_right a1 4
  
  let a2 := ["A", "bb", "CC", "ddd"]
  let key := (fun s => s.toLower)
  let r2 := insort_right a2 "cC" 0 Option.none (Option.some key)
  
  return r1 == [1, 2, 4, 4, 4, 10] && r2 == ["A", "bb", "CC", "cC", "ddd"]

def main : IO Unit := do
  let r1 ← test_bisect_right
  let r2 ← test_insort_right
  IO.println s!"Tests passed: {r1 && r2}"

end VeriBench.BisectRight
