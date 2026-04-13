import VeriBench

namespace SelectionSort

def selectionSort (arr : List Int) : List Int :=
  if arr.isEmpty then
    []
  else
    let result := arr
    let n := result.length
    
    let rec loop (result : List Int) (i : Nat) : List Int :=
      if i ≥ n then 
        result
      else
        -- Find the minimum element in the remaining unsorted array
        let rec findMinIdx (j : Nat) (minIdx : Nat) : Nat :=
          if j ≥ n then 
            minIdx
          else if result.get! j < result.get! minIdx then
            findMinIdx (j + 1) j
          else
            findMinIdx (j + 1) minIdx
            
        let minIdx := findMinIdx (i + 1) i
        
        -- Swap the found minimum element with the first element
        let result := 
          if minIdx = i then 
            result
          else
            let minVal := result.get! minIdx
            let iVal := result.get! i
            result.set! minIdx iVal |>.set! i minVal
            
        loop result (i + 1)
        
    loop result 0

def pre (arr : List Int) : Prop := True

def post (arr : List Int) (result : List Int) : Prop :=
  result.isSorted (·≤·) ∧ result.perm arr

theorem selectionSort_correct (arr : List Int) (h : pre arr) : 
  post arr (selectionSort arr) := by
  sorry

def test : IO Unit := do
  -- Basic functionality tests
  assert! (selectionSort [3, 1, 2] == [1, 2, 3])
  assert! (selectionSort [1, 2, 3] == [1, 2, 3])
  assert! (selectionSort [2, 1, 3] == [1, 2, 3])
  
  -- Edge cases
  assert! (selectionSort ([] : List Int) == [])
  assert! (selectionSort [1] == [1])
  
  -- Larger arrays
  assert! (selectionSort [5, 2, 4, 6, 1, 3] == [1, 2, 3, 4, 5, 6])
  assert! (selectionSort [9, 8, 7, 6, 5, 4, 3, 2, 1] == [1, 2, 3, 4, 5, 6, 7, 8, 9])
  assert! (selectionSort [2, 6, 4, 3, 1, 5] == [1, 2, 3, 4, 5, 6])
  
  -- Two elements
  assert! (selectionSort [2, 1] == [1, 2])
  assert! (selectionSort [1, 2] == [1, 2])
  
  -- Duplicates
  assert! (selectionSort [3, 1, 4, 1, 2, 3] == [1, 1, 2, 3, 3, 4])
  assert! (selectionSort [5, 5, 5, 5, 5] == [5, 5, 5, 5, 5])
  
  -- Already sorted
  assert! (selectionSort [1, 2, 3, 4, 5] == [1, 2, 3, 4, 5])
  
  -- Reverse sorted
  assert! (selectionSort [5, 4, 3, 2, 1] == [1, 2, 3, 4, 5])
  
  -- Random order
  assert! (selectionSort [3, 7, 1, 9, 2, 8, 4, 6, 5] == [1, 2, 3, 4, 5, 6, 7, 8, 9])

end SelectionSort
