(**
  Translation of the Lean "hasCloseElements" to Coq, including all unit tests,
  with the fix that each decimal literal is suffixed by %R to ensure it is an R.
*)

Require Import Coq.Lists.List.
Import ListNotations.

Require Import Coq.Reals.Reals.
Open Scope R_scope.  (* Also ensures +, -, etc. work on R by default *)

Require Import PeanoNat.

(**
  Compare two real numbers x < y as a bool.
  In Coq's standard library, real inequalities return Prop, not bool.
*)
Definition Rltb (x y : R) : bool :=
  if Rlt_dec x y then true else false.

(**
  Check if, in a given list of real numbers [numbers], there exist
  two distinct elements whose absolute difference is < [threshold].
*)
Definition hasCloseElements (numbers : list R) (threshold : R) : bool :=
  let enumerated := combine (seq 0 (length numbers)) numbers in
  existsb
    (fun '(i, x) =>
       existsb
         (fun '(j, y) =>
            andb (negb (Nat.eqb i j)) (Rltb (Rabs (x - y)) threshold)
         )
         enumerated
    )
    enumerated.

(*** 
  Unit Tests (translated from the Lean examples).
  Each "Example" ensures that the function returns the expected bool.
***)

(* 1) [1.0; 2.0; 3.9; 4.0; 5.0; 2.2], threshold=0.3 => true *)
Compute (hasCloseElements [1.0%R; 2.0%R; 3.9%R; 4.0%R; 5.0%R; 2.2%R] 0.3%R).
Example test1 :
  hasCloseElements [1.0%R; 2.0%R; 3.9%R; 4.0%R; 5.0%R; 2.2%R] 0.3%R = true.
Proof. reflexivity. Qed.

(* 2) threshold=0.05 => false *)
Compute (hasCloseElements [1.0%R; 2.0%R; 3.9%R; 4.0%R; 5.0%R; 2.2%R] 0.05%R).
Example test2 :
  hasCloseElements [1.0%R; 2.0%R; 3.9%R; 4.0%R; 5.0%R; 2.2%R] 0.05%R = false.
Proof. reflexivity. Qed.

(* 3) [1.0; 2.0; 5.9; 4.0; 5.0], threshold=0.95 => true *)
Compute (hasCloseElements [1.0%R; 2.0%R; 5.9%R; 4.0%R; 5.0%R] 0.95%R).
Example test3 :
  hasCloseElements [1.0%R; 2.0%R; 5.9%R; 4.0%R; 5.0%R] 0.95%R = true.
Proof. reflexivity. Qed.

(* 4) threshold=0.8 => false *)
Compute (hasCloseElements [1.0%R; 2.0%R; 5.9%R; 4.0%R; 5.0%R] 0.8%R).
Example test4 :
  hasCloseElements [1.0%R; 2.0%R; 5.9%R; 4.0%R; 5.0%R] 0.8%R = false.
Proof. reflexivity. Qed.

(* 5) [1.0; 2.0; 3.0; 4.0; 5.0; 2.0], threshold=0.1 => true *)
Compute (hasCloseElements [1.0%R; 2.0%R; 3.0%R; 4.0%R; 5.0%R; 2.0%R] 0.1%R).
Example test5 :
  hasCloseElements [1.0%R; 2.0%R; 3.0%R; 4.0%R; 5.0%R; 2.0%R] 0.1%R = true.
Proof. reflexivity. Qed.

(* 6) [1.1; 2.2; 3.1; 4.1; 5.1], threshold=1.0 => true *)
Compute (hasCloseElements [1.1%R; 2.2%R; 3.1%R; 4.1%R; 5.1%R] 1.0%R).
Example test6 :
  hasCloseElements [1.1%R; 2.2%R; 3.1%R; 4.1%R; 5.1%R] 1.0%R = true.
Proof. reflexivity. Qed.

(* 7) threshold=0.5 => false *)
Compute (hasCloseElements [1.1%R; 2.2%R; 3.1%R; 4.1%R; 5.1%R] 0.5%R).
Example test7 :
  hasCloseElements [1.1%R; 2.2%R; 3.1%R; 4.1%R; 5.1%R] 0.5%R = false.
Proof. reflexivity. Qed.

(*** Extended Tests ***)

(* 1) Empty list => no pairs => false *)
Compute (hasCloseElements [] 0.1%R).
Example test8 : hasCloseElements [] 0.1%R = false.
Proof. reflexivity. Qed.

(* 2) Single element => no pairs => false *)
Compute (hasCloseElements [1.5%R] 0.1%R).
Example test9 : hasCloseElements [1.5%R] 0.1%R = false.
Proof. reflexivity. Qed.

(* 3a) Two identical elements => distance=0 < threshold => true if threshold>0 *)
Compute (hasCloseElements [3.14%R; 3.14%R] 0.1%R).
Example test10 : hasCloseElements [3.14%R; 3.14%R] 0.1%R = true.
Proof. reflexivity. Qed.

(* 3b) If threshold==0 => distance=0 NOT < 0 => false *)
Compute (hasCloseElements [3.14%R; 3.14%R] 0.0%R).
Example test11 : hasCloseElements [3.14%R; 3.14%R] 0.0%R = false.
Proof. reflexivity. Qed.

(* 4) Large threshold => with 2 elements, we get true (distance=100 => < 999.9) *)
Compute (hasCloseElements [100%R; 200%R] 999.9%R).
Example test12 : hasCloseElements [100%R; 200%R] 999.9%R = true.
Proof. reflexivity. Qed.

(* 5) Very close distinct floats: distance=1e-8 < 1e-5 => true *)
Compute (hasCloseElements [1.0%R; 1.00000001%R] 0.00001%R).
Example test13 : hasCloseElements [1.0%R; 1.00000001%R] 0.00001%R = true.
Proof. reflexivity. Qed.

(* 6) Distinct floats not close enough: distance=2e-4 > 1e-5 => false *)
Compute (hasCloseElements [1.0%R; 1.0002%R] 0.00001%R).
Example test14 : hasCloseElements [1.0%R; 1.0002%R] 0.00001%R = false.
Proof. reflexivity. Qed.
