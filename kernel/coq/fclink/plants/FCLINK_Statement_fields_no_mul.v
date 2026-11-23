(* FCLINK_Statement.v, 2026-11-21. Author: the assistant. Status: a statement only, written before any proof of it; this
   file holds no proof script and assumes nothing.

   THE MODEL. It imports Coq's String library, the frozen statements IEEE64_Statement of MKF.ieee64,
   SINCOS32_IEEE_Statement of MKF.sincos32i, FLOOR32_Statement of MKF.floor32 and CEIL32_Statement of MKF.ceil32, and
   CPrint and KernelText of MKF.fclink. From the six it uses, in that order: b64; TOPS, its fields t_cst, t_add, t_sub,
   t_mul, t_abs, t_sel_le and t_sel_lt, the constants K_0, K_1, K_CN and K_BIG, and tieee_ops; T_floor32 and FLOOR32;
   T_ceil32 and CEIL32; tprint and c_fun1; and floor32_c_text and ceil32_c_text.

   WHAT IT SAYS.
   - FC_TEXT: c_fun1 of the literal mk_floor32 and of T_floor32 string tprint applied to the literal x equals
     floor32_c_text, and c_fun1 of the literal mk_ceil32 and of T_ceil32 string tprint applied to the literal x equals
     ceil32_c_text.
   - FC_FIELDS A B oa ob rel: rel relates t_cst oa K_0 to t_cst ob K_0, and likewise at K_1, K_CN and K_BIG; and for all
     a, b, c and d of A and a', b', c' and d' of B, if rel relates a to a' and b to b', it relates t_add oa a b to t_add
     ob a' b', t_sub oa a b to t_sub ob a' b' and t_mul oa a b to t_mul ob a' b'; if rel relates a to a', it relates
     t_abs oa a to t_abs ob a'; and if rel relates a to a', b to b', c to c' and d to d', it relates t_sel_le oa a b c d
     to t_sel_le ob a' b' c' d' and t_sel_lt oa a b c d to t_sel_lt ob a' b' c' d'.
   - FC_PARAM: for every rel of type string -> b64 -> Prop and every v of b64, if FC_FIELDS string b64 tprint tieee_ops
     rel holds and rel relates the literal x to v, then rel relates T_floor32 string tprint applied to the literal x to
     T_floor32 b64 tieee_ops applied to v, and T_ceil32 string tprint applied to the literal x to T_ceil32 b64 tieee_ops
     applied to v.
   - FCLINK is the conjunction of FC_TEXT, FC_PARAM, FLOOR32 and CEIL32.

   WHERE ITS PROOF STOPS AND WHAT IT TRUSTS. TRUSTED.md sets out where a proof of FCLINK stops and what is trusted
   beyond it, and PLANTS.md which changes such a proof would and would not notice. It trusts Coq's kernel; the four
   axioms sig_not_dec, sig_forall_dec, functional_extensionality_dep and classic; Coq's standard library (its Reals,
   NArith, ZArith and String libraries); Flocq; the frozen statements named in THE MODEL and the frozen files they
   import; and the meaning of the printed C forms, DECLARED in TRUSTED.md. *)
From Coq Require Import String.
From MKF.ieee64 Require Import IEEE64_Statement.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement.
From MKF.ceil32 Require Import CEIL32_Statement.
From MKF.fclink Require Import CPrint KernelText.
Local Open Scope string_scope.

(* 1. The text: each frozen shape at the record over C text, its input the text x, inside its function line. *)
Definition FC_TEXT : Prop :=
  c_fun1 "mk_floor32" (T_floor32 string tprint "x") = floor32_c_text /\
  c_fun1 "mk_ceil32" (T_ceil32 string tprint "x") = ceil32_c_text.

(* 2. A relation kept by the fields the two shapes use, and the two shapes, at tprint on the text x and at tieee_ops
   on an input v, related by every such relation that relates the text x to v. *)
Definition FC_FIELDS (A B : Type) (oa : TOPS A) (ob : TOPS B) (rel : A -> B -> Prop) : Prop :=
  rel (t_cst oa K_0) (t_cst ob K_0) /\ rel (t_cst oa K_1) (t_cst ob K_1) /\
  rel (t_cst oa K_CN) (t_cst ob K_CN) /\ rel (t_cst oa K_BIG) (t_cst ob K_BIG) /\
  (forall (a : A) (a' : B) (b : A) (b' : B), rel a a' -> rel b b' -> rel (t_add oa a b) (t_add ob a' b')) /\
  (forall (a : A) (a' : B) (b : A) (b' : B), rel a a' -> rel b b' -> rel (t_sub oa a b) (t_sub ob a' b')) /\
  (forall (a : A) (a' : B), rel a a' -> rel (t_abs oa a) (t_abs ob a')) /\
  (forall (a : A) (a' : B) (b : A) (b' : B) (c : A) (c' : B) (d : A) (d' : B),
     rel a a' -> rel b b' -> rel c c' -> rel d d' -> rel (t_sel_le oa a b c d) (t_sel_le ob a' b' c' d')) /\
  (forall (a : A) (a' : B) (b : A) (b' : B) (c : A) (c' : B) (d : A) (d' : B),
     rel a a' -> rel b b' -> rel c c' -> rel d d' -> rel (t_sel_lt oa a b c d) (t_sel_lt ob a' b' c' d')).

Definition FC_PARAM : Prop :=
  forall (rel : string -> b64 -> Prop) (v : b64),
  FC_FIELDS string b64 tprint tieee_ops rel -> rel "x" v ->
  rel (T_floor32 string tprint "x") (T_floor32 b64 tieee_ops v) /\
  rel (T_ceil32 string tprint "x") (T_ceil32 b64 tieee_ops v).

(* 3. The link. *)
Definition FCLINK : Prop := FC_TEXT /\ FC_PARAM /\ FLOOR32 /\ CEIL32.
