-- !benchmark @start import type=solution
import Mathlib
namespace QueueThreadSafe
-- !benchmark @end import

-- !benchmark @start solution_aux
variable {α : Type} [Inhabited α] [DecidableEq α]

inductive QueueError
  | empty
  | full
  | shutdown
  | invalidTimeout
  | taskUnderflow
  deriving DecidableEq, Repr

structure QueueCore (α : Type) where
  data : List α
  maxsize : Nat
  unfinished : Nat
  isShutdown : Bool
  deriving Repr, DecidableEq

def qsize (q : QueueCore α) : Nat := q.data.length

def empty (q : QueueCore α) : Bool := q.data.isEmpty

def full (q : QueueCore α) : Bool :=
  if q.maxsize = 0 then false
  else qsize q >= q.maxsize

def canPut (q : QueueCore α) : Bool :=
  (!q.isShutdown) && (q.maxsize = 0 || qsize q < q.maxsize)

def putWith (push : List α → α → List α)
    (q : QueueCore α) (item : α) (timeout? : Option Int := none) :
    Except QueueError (QueueCore α) :=
  let isInvalid := match timeout? with | some t => decide (t < 0) | none => false
  if isInvalid then
    Except.error QueueError.invalidTimeout
  else if q.isShutdown then
    Except.error QueueError.shutdown
  else if canPut q then
    Except.ok { q with data := push q.data item, unfinished := q.unfinished + 1 }
  else
    Except.error QueueError.full

def fifoPush (xs : List α) (x : α) : List α := xs ++ [x]

-- NOTE: We keep a wrapper matching the original signature (no timeout exposed).
def fifoPut_raw (q : QueueCore α) (x : α) : Except QueueError (QueueCore α) :=
  putWith fifoPush q x
-- !benchmark @end solution_aux

-- !benchmark @start precond_aux
-- !benchmark @end precond_aux

@[reducible, simp]
def fifoPut_precond (q : QueueCore α) (x : α) : Prop :=
  -- !benchmark @start precond
  canPut q = true
  -- !benchmark @end precond

-- !benchmark @start code_aux
-- !benchmark @end code_aux

def fifoPut (q : QueueCore α) (x : α) (h_precond : fifoPut_precond (q) (x)) : Except QueueError (QueueCore α) :=
  -- !benchmark @start code
  fifoPut_raw q x
  -- !benchmark @end code

-- !benchmark @start postcond_aux
-- !benchmark @end postcond_aux

@[reducible, simp]
def fifoPut_postcond (q : QueueCore α) (x : α) (result : Except QueueError (QueueCore α))
    (h_precond : fifoPut_precond (q) (x)) : Prop :=
  -- !benchmark @start postcond
  (∀ q', result = Except.ok q' → q'.unfinished = q.unfinished + 1)
  -- !benchmark @end postcond

-- !benchmark @start proof_aux
theorem put_unfinished_thm (q : QueueCore α) (x : α) (h : canPut q = true) :
  match fifoPut_raw q x with
  | Except.ok q' => q'.unfinished = q.unfinished + 1
  | _ => False := by
  simp [fifoPut_raw, putWith, canPut] at *
  simp [h]

theorem shutdown_prevents_put_thm (q : QueueCore α) (x : α) :
  let q_sd : QueueCore α := { q with isShutdown := true }
  fifoPut_raw q_sd x = Except.error QueueError.shutdown := by
  simp [fifoPut_raw, putWith]
-- !benchmark @end proof_aux

theorem fifoPut_spec_satisfied (q : QueueCore α) (x : α) (h_precond : fifoPut_precond (q) (x)) :
    fifoPut_postcond (q) (x) (fifoPut (q) (x) h_precond) h_precond := by
  -- !benchmark @start proof
  intro q' heq
  -- unfold wrapper
  simp [fifoPut, fifoPut_postcond] at heq ⊢
  -- reduce to the known lemma about the raw definition
  have hmatch : match fifoPut_raw q x with
    | Except.ok q'' => q''.unfinished = q.unfinished + 1
    | _ => False := put_unfinished_thm (q := q) (x := x) (h := h_precond)
  -- use hmatch with heq
  simpa [heq] using hmatch
  -- !benchmark @end proof