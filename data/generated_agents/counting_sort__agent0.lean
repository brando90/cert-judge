import Mathlib.Data.List.Basic
import Mathlib.Data.List.Sort
import Mathlib.Data.Int.Basic
import Mathlib.Tactic

namespace CountingSort

def pre (arr : List Int) : Prop := True

/-- 
Sorts a list using the counting sort algorithm.
It counts the occurrences of each element and uses this information
to place elements in their correct sorted positions.
-/
def countingSort (arr : List Int) : List Int :=
  if arr.isEmpty then
    []
  else
    let maxVal := arr.maximum?.get!
    let minVal := arr.minimum?.get!
    
    let rangeSize := maxVal - minVal + 1
    
    -- Create count array initialized with zeros
    let count := List.replicate rangeSize 0
    
    -- Count occurrences of each element
    let count := arr.foldl (fun counts num => 
      let idx := (num - minVal).toNat
      counts.set! idx (counts.get! idx + 1)) count
    
    -- Build the sorted array
    let result := List.foldl (fun result i =>
      let val := i + minVal
      let count := count.get! i.toNat
      result ++ List.replicate count val
    ) [] (List.range rangeSize.toNat)
    
    result

def post (arr : List Int) (result : List Int) : Prop :=
  result.isSorted (· ≤ ·) ∧ result.Perm arr

theorem countingSort_correct (arr : List Int) (h : pre arr) : 
  post arr (countingSort arr) := by
  sorry

-- Tests
#eval countingSort [3, 1, 2] -- [1, 2, 3]
#eval countingSort [] -- []
#eval countingSort [1] -- [1]
#eval countingSort [5, 2, 4, 6, 1, 3] -- [1, 2, 3, 4, 5, 6]
#eval countingSort [9, 8, 7, 6, 5, 4, 3, 2, 1] -- [1, 2, 3, 4, 5, 6, 7, 8, 9]
#eval countingSort [2, 1] -- [1, 2]
#eval countingSort [3, 1, 4, 1, 2, 3] -- [1, 1, 2, 3, 3, 4]
#eval countingSort [5, 5, 5, 5, 5] -- [5, 5, 5, 5, 5]
#eval countingSort [0, 3, 1, 0, 2] -- [0, 0, 1, 2, 3]
#eval countingSort [64, 34, 25, 12, 22, 11, 90, 88, 76, 50, 42] -- [11, 12, 22, 25, 34, 42, 50, 64, 76, 88, 90]
#eval countingSort [-3, 1, -2, 0] -- [-3, -2, 0, 1]

end CountingSort
