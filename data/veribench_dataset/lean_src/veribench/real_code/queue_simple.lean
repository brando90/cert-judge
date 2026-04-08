/-
# Benchmark Task: Simple, Unbounded FIFO Queue

This file provides a pure Lean model of a simple, unbounded FIFO queue,
mirroring the sliced implementation from Python's standard `queue` library.

The primary task is to verify the `SimpleQueue` class and its operations,
capturing FIFO ordering and the behaviour of the non-blocking interfaces.
-/

import Std

namespace VeriBenchSimpleQueue

/-
# Implementation
-/

open Std

inductive QueueError
| empty
| invalidTimeout
deriving DecidableEq, Inhabited

structure SimpleQueue (α : Type u) where
  data : List α
deriving Inhabited, DecidableEq

namespace SimpleQueue

variable {α : Type u}

/-- Create an empty queue. -/
def mkEmpty : SimpleQueue α :=
  ⟨[]⟩

/-- Number of items currently stored. -/
def qsize (q : SimpleQueue α) : Nat :=
  q.data.length

/-- Boolean flag indicating emptiness. -/
def empty (q : SimpleQueue α) : Bool :=
  q.data.isEmpty

/-- Enqueue an item; parameters `block` and `timeout` are ignored (API compatibility). -/
def put (q : SimpleQueue α) (item : α) (_block : Bool := true) (_timeout? : Option Nat := none) :
    SimpleQueue α :=
  ⟨q.data ++ [item]⟩

/-- Non-blocking enqueue (alias for `put`). -/
def putNowait (q : SimpleQueue α) (item : α) : SimpleQueue α :=
  put q item false (some 0)

/-- Dequeue an item, returning either a value/queue pair or an error. -/
def get (q : SimpleQueue α) (block : Bool := true) (timeout? : Option Int := none) :
    Except QueueError (α × SimpleQueue α) :=
  match timeout? with
  | some t =>
      if t < 0 then
        Except.error QueueError.invalidTimeout
      else
        match q.data with
        | [] => Except.error QueueError.empty
        | x :: xs => Except.ok (x, ⟨xs⟩)
  | none =>
      match q.data with
      | [] =>
          if block then
            Except.error QueueError.empty
          else
            Except.error QueueError.empty
      | x :: xs => Except.ok (x, ⟨xs⟩)

/-- Non-blocking dequeue. -/
def getNowait (q : SimpleQueue α) : Except QueueError (α × SimpleQueue α) :=
  get q false (some 0)

end SimpleQueue

def benchmark_simple_queue := SimpleQueue


/-
# Tests
-/

open SimpleQueue

/-- Basic queue operations mirror the Python unit tests. -/
example :
    let q₀ : SimpleQueue Nat := mkEmpty
    let q₁ := put q₀ 1
    let q₂ := putNowait q₁ 2
    (empty q₀ = true) ∧ q₀.qsize = 0 ∧
    (empty q₂ = false) ∧ q₂.qsize = 2 := by
  simp [SimpleQueue.mkEmpty, SimpleQueue.put, SimpleQueue.putNowait,
        SimpleQueue.empty, SimpleQueue.qsize, List.isEmpty]

/-- Dequeue operations respect FIFO order. -/
example :
    let q₀ : SimpleQueue Nat := mkEmpty
    let q₁ := put (put q₀ 1) 2
    let q₂ := put q₁ 3
    get q₂ = Except.ok (1, ⟨[2, 3]⟩) := by
  simp [SimpleQueue.mkEmpty, SimpleQueue.put, SimpleQueue.get]

/-- Non-blocking dequeue mirrors Python's `get_nowait`. -/
example :
    let q₀ : SimpleQueue Nat := ⟨[10, 20]⟩
    getNowait q₀ = Except.ok (10, ⟨[20]⟩) := by
  simp [SimpleQueue.getNowait, SimpleQueue.get]

/-- Dequeue from an empty queue signals the `empty` error. -/
example :
    get (mkEmpty : SimpleQueue Nat) false (some 0) = Except.error QueueError.empty := by
  rfl

/-- Negative timeout raises the `invalidTimeout` error. -/
example :
    get (mkEmpty : SimpleQueue Nat) true (some (-1)) = Except.error QueueError.invalidTimeout := by
  rfl


/-
# Pre-condition
-/

def Pre_get (q : SimpleQueue α) (timeout? : Option Int) : Prop :=
  (timeout?.map (· ≥ 0) |>.getD True) ∧ ¬ q.data.isEmpty

def Pre_getNowait (q : SimpleQueue α) : Prop :=
  ¬ q.data.isEmpty

/-- Negative timeout violates `Pre_get`. -/
example : ¬ Pre_get (mkEmpty : SimpleQueue Nat) (some (-1)) := by
  simp [Pre_get, SimpleQueue.mkEmpty]

/-- Empty queue violates the non-blocking precondition. -/
example : ¬ Pre_getNowait (mkEmpty : SimpleQueue Nat) := by
  simp [Pre_getNowait, SimpleQueue.mkEmpty]


/-
# Property Theorems
-/

def fifo_prop (q : SimpleQueue α) : Prop :=
  ∀ x xs, q.data = x :: xs → get q = Except.ok (x, ⟨xs⟩)

def size_after_put_prop (q : SimpleQueue α) (x : α) : Prop :=
  (put q x).qsize = q.qsize + 1

theorem fifo_thm (q : SimpleQueue α) :
    fifo_prop q := by
  cases q with
  | mk data =>
      intro x xs h
      cases h
      simp [SimpleQueue.get]

theorem size_after_put_thm (q : SimpleQueue α) (x : α) :
    size_after_put_prop q x := by
  simp [size_after_put_prop, SimpleQueue.put, SimpleQueue.qsize, List.length_append]


/-
# Post-condition
-/

def Post (q : SimpleQueue α) (x : α) : Prop :=
  fifo_prop q ∧ size_after_put_prop q x


/-
# Correctness Theorem
-/

theorem correctness_thm (q : SimpleQueue α) (x : α)
    (h : q.data ≠ []) :
    Post q x := by
  have _ := h
  exact And.intro (fifo_thm q) (size_after_put_thm q x)

end VeriBenchSimpleQueue
