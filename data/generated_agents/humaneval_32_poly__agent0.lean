import Lean.Data.HashMap

namespace VeriBench.HumanEval32

def poly (xs : List Float) (x : Float) : Float :=
  let indices := List.range xs.length
  List.sum (List.zipWith (fun coeff i => coeff * x ^ i) xs indices)

/--
  Find a zero of a polynomial with coefficients `xs`.
  
  This function returns only one zero point, even if there are many.
  It only works on lists with an even number of coefficients and
  the largest non-zero coefficient guarantees a solution.
-/
def findZero (xs : List Float) : Float :=
  let rec binarySearch (begin end : Float) : Float :=
    if end - begin ≤ 1e-10 then
      begin
    else
      let center := (begin + end) / 2.0
      if poly xs center * poly xs begin > 0 then
        binarySearch center end
      else
        binarySearch begin center
  
  let rec expandInterval (begin end : Float) : Float × Float :=
    if poly xs begin * poly xs end ≤ 0 then
      (begin, end)
    else
      expandInterval (begin * 2.0) (end * 2.0)
  
  let (begin, end) := expandInterval (-1.0) 1.0
  binarySearch begin end

/-! ## Tests -/

#eval poly [1, 2] 0  -- Expected: 1
#eval poly [1, 2] 1  -- Expected: 3
#eval poly [1, 2, 3] 2  -- Expected: 1 + 2*2 + 3*4 = 17

#eval findZero [1, 2]  -- Expected: -0.5
#eval findZero [-6, 11, -6, 1]  -- Expected: 1.0 or close to it

/-! ## Verification -/

/-- Precondition for `findZero`: the list must have an even number of coefficients. -/
def findZeroPre (xs : List Float) : Prop :=
  xs.length % 2 = 0 ∧ xs.length > 0

/-- Postcondition for `findZero`: the polynomial evaluated at the result is close to zero. -/
def findZeroPost (xs : List Float) (result : Float) : Prop :=
  Float.abs (poly xs result) < 1e-4

theorem findZero_correct (xs : List Float) :
  findZeroPre xs → findZeroPost xs (findZero xs) := by
  sorry

end VeriBench.HumanEval32
