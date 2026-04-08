import VeriBench

/-!
# Triple Sum to Zero
-/

def triples_sum_to_zero (l: List Int) : Bool :=
  let len := l.length
  let rec loop (i: Nat) : Bool :=
    if i >= len then false
    else
      let rec loop_j (j: Nat) : Bool :=
        if j >= len then loop (i + 1)
        else
          let rec loop_k (k: Nat) : Bool :=
            if k >= len then loop_j (j + 1)
            else if l[i]! + l[j]! + l[k]! == 0 then true
            else loop_k (k + 1)
          if j + 1 >= len then loop (i + 1)
          else loop_k (j + 1)
      if i + 1 >= len then false
      else loop_j (i + 1)
  loop 0

/-- Specification for `triples_sum_to_zero`: Returns true if there are three distinct elements 
in the list that sum to zero, and false otherwise. -/
def triples_sum_to_zero_spec (l: List Int) : Bool :=
  l.enum.any fun (i, vi) => 
    l.enum.any fun (j, vj) => 
      l.enum.any fun (k, vk) => 
        i != j && i != k && j != k && vi + vj + vk = 0

/-- Precondition for `triples_sum_to_zero`: None -/
def triples_sum_to_zero_pre (_l: List Int) : Prop := True

/-- Postcondition for `triples_sum_to_zero`: The function returns true if and only if
there are three distinct elements in the list that sum to zero. -/
def triples_sum_to_zero_post (l: List Int) (result: Bool) : Prop :=
  result = triples_sum_to_zero_spec l

theorem triples_sum_to_zero_correct (l: List Int) 
    (h: triples_sum_to_zero_pre l) : 
    triples_sum_to_zero_post l (triples_sum_to_zero l) := by
  sorry

def main : IO Unit := do
  VeriBench.check "triples_sum_to_zero" triples_sum_to_zero
    #[
      [1, 3, 5, 0], -- false
      [1, 3, 5, -1], -- false
      [1, 3, -2, 1], -- true
      [1, 2, 3, 7], -- false
      [1, 2, 5, 7], -- false
      [2, 4, -5, 3, 9, 7], -- true
      [1], -- false
      [1, 3, 5, -100], -- false
      [100, 3, 5, -100] -- false
    ]
    #[false, false, true, false, false, true, false, false, false]
