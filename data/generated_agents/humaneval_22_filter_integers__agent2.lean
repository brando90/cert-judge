import Lean.Data.HashMap

/- Specification for filter_integers:
   Filter given list of any python values only for integers
-/

inductive PyValue where
  | int : Int → PyValue
  | float : Float → PyValue
  | string : String → PyValue
  | list : List PyValue → PyValue
  | dict : Lean.HashMap PyValue PyValue → PyValue
  deriving Repr, BEq, Hashable

def PyValue.isInt (v : PyValue) : Bool :=
  match v with
  | PyValue.int _ => true
  | _ => false

def filter_integers (values : List PyValue) : List Int :=
  let filtered := values.filter PyValue.isInt
  filtered.map (λ v =>
    match v with
    | PyValue.int i => i
    | _ => 0 -- This case won't happen due to the filter
  )

-- Tests
def test_filter_integers : IO Unit := do
  let test1 := filter_integers [PyValue.string "a", PyValue.float 3.14, PyValue.int 5]
  IO.println s!"Test 1: {test1}"
  assert! test1 == [5]

  let test2 := filter_integers [PyValue.int 1, PyValue.int 2, PyValue.int 3, 
                                PyValue.string "abc", PyValue.dict {}, PyValue.list []]
  IO.println s!"Test 2: {test2}"
  assert! test2 == [1, 2, 3]

  let test3 := filter_integers []
  IO.println s!"Test 3: {test3}"
  assert! test3 == []

  let test4 := filter_integers [PyValue.int 4, PyValue.dict {}, PyValue.list [], 
                                PyValue.float 23.2, PyValue.int 9, PyValue.string "adasd"]
  IO.println s!"Test 4: {test4}"
  assert! test4 == [4, 9]

  let test5 := filter_integers [PyValue.int 3, PyValue.string "c", PyValue.int 3, 
                                PyValue.int 3, PyValue.string "a", PyValue.string "b"]
  IO.println s!"Test 5: {test5}"
  assert! test5 == [3, 3, 3]

  IO.println "All tests passed!"

-- Verification
theorem filter_integers_spec (values : List PyValue) :
  filter_integers values = values.filterMap (λ v => 
    match v with
    | PyValue.int i => some i
    | _ => none
  ) := by
  sorry

#eval test_filter_integers
