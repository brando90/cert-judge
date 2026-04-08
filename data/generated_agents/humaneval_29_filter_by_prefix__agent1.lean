import VeriBench

namespace HumanEval29

/-- Filter an input list of strings only for ones that start with a given prefix. -/
def filter_by_prefix (strings : List String) (prefix : String) : List String :=
  strings.filter (fun x => x.startsWith prefix)

/-- Specification for filter_by_prefix -/
def filter_by_prefix_spec (strings : List String) (prefix : String) : List String :=
  strings.filter (fun x => x.startsWith prefix)

/-- Precondition for filter_by_prefix -/
def filter_by_prefix_pre (_strings : List String) (_prefix : String) : Prop :=
  True

/-- Postcondition for filter_by_prefix -/
def filter_by_prefix_post (strings : List String) (prefix : String) (result : List String) : Prop :=
  result = filter_by_prefix_spec strings prefix

theorem filter_by_prefix_correct (strings : List String) (prefix : String)
    (h_pre : filter_by_prefix_pre strings prefix) :
    filter_by_prefix_post strings prefix (filter_by_prefix strings prefix) := by
  simp [filter_by_prefix_post, filter_by_prefix, filter_by_prefix_spec]
  
/-- Tests for filter_by_prefix -/
def tests : IO Unit := do
  VeriBench.verify "filter_by_prefix empty list" (filter_by_prefix [] "john" = [])
  VeriBench.verify "filter_by_prefix with prefix 'xxx'" 
    (filter_by_prefix ["xxx", "asd", "xxy", "john doe", "xxxAAA", "xxx"] "xxx" = ["xxx", "xxxAAA", "xxx"])
  VeriBench.verify "filter_by_prefix with prefix 'a'" 
    (filter_by_prefix ["abc", "bcd", "cde", "array"] "a" = ["abc", "array"])
  VeriBench.verify "filter_by_prefix with empty prefix" 
    (filter_by_prefix ["abc", "bcd"] "" = ["abc", "bcd"])

end HumanEval29
