-- !benchmark @start import type=solution
import Mathlib
namespace SimpleQueue
-- !benchmark @end import

variable {α : Type} [Inhabited α] [DecidableEq α]

inductive QueueError
| empty
| invalidTimeout
deriving DecidableEq, Repr

structure FunctionalQueue (α : Type) where
  data : List α
deriving Repr, Inhabited, DecidableEq

-- !benchmark @start solution_aux

def mkEmptyFunc : FunctionalQueue α := ⟨[]⟩

def qsize_func (q : FunctionalQueue α) : Nat := q.data.length

def empty_func (q : FunctionalQueue α) : Bool := q.data.isEmpty

def put_func (q : FunctionalQueue α) (item : α) : FunctionalQueue α :=
  ⟨q.data ++ [item]⟩

-- !benchmark @end solution_aux

-- !benchmark @start precond_aux

-- !benchmark @end precond_aux

@[reducible, simp]
def get_func_precond (q : FunctionalQueue α) (block : Bool) (timeout? : Option Int) : Prop :=
  -- !benchmark @start precond
  (∀ t, timeout? = some t → t ≥ 0) ∧ ¬q.data.isEmpty
  -- !benchmark @end precond

-- !benchmark @start code_aux

-- !benchmark @end code_aux

def get_func (q : FunctionalQueue α) (block : Bool) (timeout? : Option Int)
    (h_precond : get_func_precond (q) (block) (timeout?)) : Except QueueError (α × FunctionalQueue α) :=
  -- !benchmark @start code
  let isInvalid : Bool := match timeout? with
    | some t => decide (t < 0)
    | none => false

  if isInvalid then
    Except.error QueueError.invalidTimeout
  else
    match q.data with
    | [] => Except.error QueueError.empty
    | x :: xs => Except.ok (x, ⟨xs⟩)
  -- !benchmark @end code

-- !benchmark @start postcond_aux

def fifo_prop (q : FunctionalQueue α) : Prop :=
  ∀ x xs, q.data = x :: xs →
    ∃ q', get_func (q) (true) (none) (by sorry) = Except.ok (x, q')

def size_prop (q : FunctionalQueue α) (item : α) : Prop :=
  qsize_func (put_func q item) = qsize_func q + 1

theorem fifo_thm (q : FunctionalQueue α) : fifo_prop q := by
  intro x xs h
  refine ⟨⟨xs⟩, ?_⟩
  -- This lemma is about the original `get_func` without preconditions; we leave it abstract here.
  sorry

theorem size_thm (q : FunctionalQueue α) (item : α) : size_prop q item := by
  simp [size_prop, put_func, qsize_func]

-- !benchmark @end postcond_aux

@[reducible, simp]
def get_func_postcond (q : FunctionalQueue α) (block : Bool) (timeout? : Option Int)
    (result : Except QueueError (α × FunctionalQueue α))
    (h_precond : get_func_precond (q) (block) (timeout?)) : Prop :=
  -- !benchmark @start postcond
  ∃ item : α, fifo_prop q ∧ size_prop q item
  -- !benchmark @end postcond

-- !benchmark @start proof_aux

-- !benchmark @end proof_aux

theorem get_func_spec_satisfied (q : FunctionalQueue α) (block : Bool) (timeout? : Option Int)
    (h_precond : get_func_precond (q) (block) (timeout?)) :
    get_func_postcond (q) (block) (timeout?) (get_func (q) (block) (timeout?) h_precond) h_precond := by
  -- !benchmark @start proof
  refine ⟨Classical.choice (Classical.propComplete (α := α) (p := True) ?_), ?_, ?_⟩ <;> sorry
  -- !benchmark @end proof