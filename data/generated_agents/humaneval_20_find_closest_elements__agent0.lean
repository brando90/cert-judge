/-
Implementation of find_closest_elements function in Lean 4
-/

def findClosestElements (numbers : List Float) : Float × Float :=
  let rec findClosest (idx : Nat) (remaining : List Float) (closestPair : Float × Float) (minDistance : Float) : Float × Float :=
    match idx, remaining with
    | _, [] => closestPair
    | i, elem::rest =>
      let (newPair, newDist) := numbers.foldlIdx
        (fun j (acc : (Float × Float) × Float) elem2 =>
          if i ≠ j then
            let (currPair, currDist) := acc
            let newDist := Float.abs (elem - elem2)
            if newDist < currDist then
              ((if elem < elem2 then (elem, elem2) else (elem2, elem)), newDist)
            else
              acc
          else
            acc)
        (closestPair, minDistance)
        (fun x => x)
      findClosest (i + 1) rest newPair newDist
  
  if numbers.length < 2 then
    (0.0, 0.0) -- Default for invalid input
  else
    let firstElem := numbers.get! 0
    let secondElem := numbers.get! 1
    let initialPair := if firstElem ≤ secondElem then (firstElem, secondElem) else (secondElem, firstElem)
    let initialDist := Float.abs (firstElem - secondElem)
    findClosest 0 numbers initialPair initialDist

/-- Specification for findClosestElements -/
def findClosestElementsSpec (numbers : List Float) : Float × Float :=
  let rec findMinPair (pairs : List (Float × Float)) (minPair : Option (Float × Float)) (minDist : Option Float) : Float × Float :=
    match pairs with
    | [] => 
      match minPair with
      | none => (0.0, 0.0) -- Should not happen if list has at least 2 elements
      | some pair => pair
    | (a, b)::rest =>
      let dist := Float.abs (a - b)
      match minDist with
      | none => findMinPair rest (some (a, b)) (some dist)
      | some currDist =>
        if dist < currDist then
          findMinPair rest (some (a, b)) (some dist)
        else
          findMinPair rest minPair minDist
  
  if numbers.length < 2 then
    (0.0, 0.0) -- Default for invalid input
  else
    let allPairs := numbers.foldlIdx
      (fun i acc elem1 =>
        numbers.foldlIdx
          (fun j acc' elem2 =>
            if i ≠ j then
              let pair := if elem1 ≤ elem2 then (elem1, elem2) else (elem2, elem1)
              pair :: acc'
            else
              acc')
          acc
          (fun x => x))
      []
      (fun x => x)
    
    findMinPair allPairs none none

/-- Precondition: The input list must have at least 2 elements -/
def findClosestElements_pre (numbers : List Float) : Prop :=
  numbers.length ≥ 2

/-- Postcondition: The output is a pair of elements from the input list,
    and there is no pair of distinct elements in the list with a smaller difference -/
def findClosestElements_post (numbers : List Float) (result : Float × Float) : Prop :=
  let (a, b) := result
  -- Both elements are in the list
  (a ∈ numbers ∧ b ∈ numbers) ∧
  -- Elements are ordered (smaller first)
  a ≤ b ∧
  -- No other pair has smaller difference
  ∀ (x y : Float), x ∈ numbers → y ∈ numbers → x ≠ y → Float.abs (a - b) ≤ Float.abs (x - y)

/-- Correctness theorem for findClosestElements -/
theorem findClosestElements_correct (numbers : List Float) :
  findClosestElements_pre numbers → 
  findClosestElements_post numbers (findClosestElements numbers) :=
  sorry

/-- Test cases for findClosestElements -/
def testFindClosestElements : IO Unit := do
  let test1 := findClosestElements [1.0, 2.0, 3.9, 4.0, 5.0, 2.2]
  IO.println s!"Test 1: {test1}"
  assert! test1 == (3.9, 4.0)
  
  let test2 := findClosestElements [1.0, 2.0, 5.9, 4.0, 5.0]
  IO.println s!"Test 2: {test2}"
  assert! test2 == (5.0, 5.9)
  
  let test3 := findClosestElements [1.0, 2.0, 3.0, 4.0, 5.0, 2.2]
  IO.println s!"Test 3: {test3}"
  assert! test3 == (2.0, 2.2)
  
  let test4 := findClosestElements [1.0, 2.0, 3.0, 4.0, 5.0, 2.0]
  IO.println s!"Test 4: {test4}"
  assert! test4 == (2.0, 2.0)
  
  let test5 := findClosestElements [1.1, 2.2, 3.1, 4.1, 5.1]
  IO.println s!"Test 5: {test5}"
  assert! test5 == (2.2, 3.1)
  
  IO.println "All tests passed!"

/-- Run the tests -/
#eval testFindClosestElements
