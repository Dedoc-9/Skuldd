(* CPrint.v, 2026-11-21. Author: the assistant. Status: definitions only, written before any proof that uses them; this
   file holds no proof script and assumes nothing.

   THE MODEL. It imports Coq's String, NArith and ZArith libraries, Flocq's Core and BinarySingleNaN, and the frozen
   statements IEEE64_Statement of MKF.ieee64 and SINCOS32_IEEE_Statement of MKF.sincos32i. From the two frozen
   statements it uses, in that order: b64; and TOPS, its nine fields and tieee_cst.

   WHAT IT SAYS.
   - cp_digit d is String.substring (N.to_nat d) 1 of the string 0123456789abcdef: the one character at position
     N.to_nat d for d below 16, and the empty string for d of 16 or more.
   - cp_step base st, for st the pair of q and acc, is: if N.eqb q 0 then that pair, else the pair of N.div q base and
     cp_digit of N.modulo q base followed by acc.
   - cp_digits base n is the string 0 for N0, and for Npos it is snd of Nat.iter 20 applied to cp_step base and to the
     pair of n and the empty string.
   - cp_dec z is the string 0 for Z0, cp_digits 10 of Npos p for Zpos p, and a minus sign followed by cp_digits 10 of
     Npos p for Zneg p.
   - cp_lit b is the string 0.0 for B754_zero false; the string (-0.0) for B754_zero true; the string 0x, cp_digits 16
     of Npos m, the string p and cp_dec e, in that order, for B754_finite false m e; the string (-0x, cp_digits 16 of
     Npos m, the string p, cp_dec e and a closing bracket, in that order, for B754_finite true m e; and the string
     @not_finite@ for every other b.
   - tprint is the TOPS string whose t_add, t_sub, t_mul and t_div write a and b as (a + b), (a - b), (a * b) and
     (a / b), whose t_abs writes a as fabs(a), whose t_neg writes a as (- a), whose t_sel_le and t_sel_lt write a, b, c
     and d as (a <= b ? c : d) and (a < b ? c : d), and whose t_cst writes c as cp_lit of tieee_cst c.
   - c_fun1 name body is the string static double name(double x) { return body; } with name and body put in place.

   WHERE ITS PROOF STOPS AND WHAT IT TRUSTS. TRUSTED.md sets out what these definitions are trusted to mean and where a
   proof that uses them stops, and PLANTS.md which changes to them such a proof would and would not notice. It trusts
   Coq's kernel; Flocq; Coq's String, NArith and ZArith libraries; the frozen statements named above; and, where its
   strings are read as C, the meaning of the printed C forms, DECLARED in TRUSTED.md. *)
From Coq Require Import String NArith ZArith.
From Flocq Require Import Core BinarySingleNaN.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
Local Open Scope string_scope.

(* 1. The digits. *)
Definition cp_digit (d : N) : string := String.substring (N.to_nat d) 1%nat "0123456789abcdef".

Definition cp_step (base : N) (st : (N * string)%type) : (N * string)%type :=
  match st with
  | (q, acc) => if N.eqb q 0%N then (q, acc) else (N.div q base, cp_digit (N.modulo q base) ++ acc)
  end.

Definition cp_digits (base n : N) : string :=
  match n with
  | N0 => "0"
  | Npos _ => snd (Nat.iter 20%nat (cp_step base) (n, ""))
  end.

Definition cp_dec (z : Z) : string :=
  match z with
  | Z0 => "0"
  | Zpos p => cp_digits 10%N (Npos p)
  | Zneg p => "-" ++ cp_digits 10%N (Npos p)
  end.

(* 2. A binary64 value as C text. *)
Definition cp_lit (b : b64) : string :=
  match b with
  | B754_zero false => "0.0"
  | B754_zero true => "(-0.0)"
  | B754_finite false m e _ => "0x" ++ cp_digits 16%N (Npos m) ++ "p" ++ cp_dec e
  | B754_finite true m e _ => "(-0x" ++ cp_digits 16%N (Npos m) ++ "p" ++ cp_dec e ++ ")"
  | _ => "@not_finite@"
  end.

(* 3. The record over C text. *)
Definition tprint : TOPS string := {|
  t_add := fun a b => "(" ++ a ++ " + " ++ b ++ ")";
  t_sub := fun a b => "(" ++ a ++ " + " ++ b ++ ")";
  t_mul := fun a b => "(" ++ a ++ " * " ++ b ++ ")";
  t_div := fun a b => "(" ++ a ++ " / " ++ b ++ ")";
  t_abs := fun a => "fabs(" ++ a ++ ")";
  t_neg := fun a => "(- " ++ a ++ ")";
  t_sel_le := fun a b c d => "(" ++ a ++ " <= " ++ b ++ " ? " ++ c ++ " : " ++ d ++ ")";
  t_sel_lt := fun a b c d => "(" ++ a ++ " < " ++ b ++ " ? " ++ c ++ " : " ++ d ++ ")";
  t_cst := fun c => cp_lit (tieee_cst c) |}.

(* 4. The one-line C function. *)
Definition c_fun1 (name : string) (body : string) : string :=
  "static double " ++ name ++ "(double x) { return " ++ body ++ "; }".
