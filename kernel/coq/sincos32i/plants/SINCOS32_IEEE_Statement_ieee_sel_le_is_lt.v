(* DRAFT 3 (2026-11-16), a scratch candidate: the model-to-binary64 correspondence of sinturn32 and costurn32, its
   statement only. Author: the assistant. Definitions only: this file holds no proof script and assumes nothing.
   It is the counterpart, for the two turns functions, of ieee64/IEEE64_Statement.v, and follows its method.

   THE GAP. g_sinturn32 and g_costurn32 (sincos32/Graph.v) are operation graphs over the real numbers in Flocq's FLT
   model of binary64, which has no overflow, no sign of zero, no NaN and no infinity. SINCOS32_ALL is about those
   graphs. Nothing says that IEEE 754 binary64 arithmetic computes their values. SINCOS32_IEEE below says so, for
   every finite binary64 input that is a binary32 number, of Flocq.IEEE754.BinarySingleNaN.

   HOW. Each graph is written once more as a shape T_...: the graph's own expression tree with every operation
   replaced by a field of the record TOPS, for any type T of values. tmodel_ops gives the fields at T = R as the
   graph files write the operations; tieee_ops gives them at T = b64 as Flocq's IEEE operations in round to nearest
   even. For each shape a definition ..._model with eq_refl for its body is accepted by the kernel only if the
   shape at the model is convertible with the graph (IEEE64_Statement.v, section 6, says why a term is given to
   eq_refl in some of them and why nothing rests on that term).

   WHY A SECOND RECORD. IEEE64_Statement.v is frozen. Its record OPS has no exact negation, which these graphs use,
   and its constants are not these. TOPS is OPS without the square root and with t_neg; b64 and the two facts about
   53 and 1024 are IEEE64_Statement.v's, imported.

   WHAT IT DOES NOT SAY.
   - Nothing about the sign of a zero result: B2R of +0 and of -0 is the real number 0. The sign of zero at exact
     zeros, and the result for an infinite or NaN input, are not stated here.
   - Nothing about inputs that are not binary32 numbers.
   - Nothing about the value a selection does not return, nor about the values in between, nor about flags.
   - Nothing about a compiler, a processor or a program.
   - Nothing about what the graphs' values are: that is SINCOS32_ALL, about the graphs.
   WHAT IT TRUSTS. That Flocq's Bplus, Bminus, Bmult and Bdiv at mode_NE, Babs, Bopp, Bleb and Bltb are IEEE 754's. *)
From Coq Require Import Reals.
From Flocq Require Import Core BinarySingleNaN.
From MKF.f32 Require Import F32_Statement.
From MKF.p32 Require Import Graphs.
From MKF.sin32 Require Import Graph.
From MKF.cos32 Require Import Graph.
From MKF.sincos32 Require Import Graph.
From MKF.ieee64 Require Import IEEE64_Statement.
Open Scope R_scope.

(* 1. The constants the two graphs use, as names, and the operations, as a record over any type T of values.
   t_sel_le o a b c d is "c if a <= b, otherwise d"; t_sel_lt o a b c d is "c if a < b, otherwise d". *)
Inductive tconst : Set :=
  | K_KK | K_MM | K_TT | K_HH | K_0 | K_1 | K_4 | K_CN | K_BIG | K_PH
  | K_6 | K_20 | K_42 | K_72 | K_110 | K_156 | K_210.

Record TOPS (T : Type) : Type := Build_TOPS {
  t_add : T -> T -> T;
  t_sub : T -> T -> T;
  t_mul : T -> T -> T;
  t_div : T -> T -> T;
  t_abs : T -> T;
  t_neg : T -> T;
  t_sel_le : T -> T -> T -> T -> T;
  t_sel_lt : T -> T -> T -> T -> T;
  t_cst : tconst -> T }.
Arguments t_add {T} _ _ _.
Arguments t_sub {T} _ _ _.
Arguments t_mul {T} _ _ _.
Arguments t_div {T} _ _ _.
Arguments t_abs {T} _ _.
Arguments t_neg {T} _ _.
Arguments t_sel_le {T} _ _ _ _ _.
Arguments t_sel_lt {T} _ _ _ _ _.
Arguments t_cst {T} _ _.

(* 2. The model: every field as the graph files write the operation. KK, MM, TT, HH are p32/Graphs.v's own;
   turn_CN (1.5 * 2^52) and turn_BIG (2^23) are sincos32/Graph.v's; cos32_PH is cos32/Graph.v's (the binary64
   number nearest pi/2); the others are numerals. The absolute value and the negation are not rounded. *)
Definition tmodel_cst (c : tconst) : R :=
  match c with
  | K_KK => KK
  | K_MM => MM
  | K_TT => TT
  | K_HH => HH
  | K_0 => 0
  | K_1 => 1
  | K_4 => 4
  | K_CN => turn_CN
  | K_BIG => turn_BIG
  | K_PH => cos32_PH
  | K_6 => 6
  | K_20 => 20
  | K_42 => 42
  | K_72 => 72
  | K_110 => 110
  | K_156 => 156
  | K_210 => 210
  end.

Definition tmodel_ops : TOPS R := {|
  t_add := fun a b => RN64 (a + b);
  t_sub := fun a b => RN64 (a - b);
  t_mul := fun a b => RN64 (a * b);
  t_div := fun a b => RN64 (a / b);
  t_abs := Rabs;
  t_neg := Ropp;
  t_sel_le := fun a b c d => if Rle_dec a b then c else d;
  t_sel_lt := fun a b c d => if Rlt_dec a b then c else d;
  t_cst := tmodel_cst |}.

(* 3. IEEE binary64. Each constant is an explicit binary64 value: sign, mantissa, exponent, and the term that says
   the pair is a binary64 number, which computes (eq_refl). A value is mantissa * 2^exponent:
     KK, MM, TT, HH, 0, 1 as in IEEE64_Statement.v     4 = 2^52 * 2^-50
     CN = 3 * 2^51 = 6755399441055744                  BIG = 2^52 * 2^-29 = 2^23
     PH = 7074237752028440 * 2^-52                     6, 20, 42, 72, 110, 156, 210 as written. *)
Definition tieee_cst (c : tconst) : b64 :=
  match c with
  | K_KK => @B754_finite 53 1024 false (536870913 * 2 ^ 23) (-23) eq_refl
  | K_MM => @B754_finite 53 1024 false (3 * 2 ^ 51) (-149) eq_refl
  | K_TT => @B754_finite 53 1024 false (2 ^ 52) (-178) eq_refl
  | K_HH => @B754_finite 53 1024 false (2 ^ 52) (-202) eq_refl
  | K_0 => @B754_zero 53 1024 false
  | K_1 => @B754_finite 53 1024 false (2 ^ 52) (-52) eq_refl
  | K_4 => @B754_finite 53 1024 false (2 ^ 52) (-50) eq_refl
  | K_CN => @B754_finite 53 1024 false (3 * 2 ^ 51) 0 eq_refl
  | K_BIG => @B754_finite 53 1024 false (2 ^ 52) (-29) eq_refl
  | K_PH => @B754_finite 53 1024 false 7074237752028440 (-52) eq_refl
  | K_6 => @B754_finite 53 1024 false (6 * 2 ^ 50) (-50) eq_refl
  | K_20 => @B754_finite 53 1024 false (20 * 2 ^ 48) (-48) eq_refl
  | K_42 => @B754_finite 53 1024 false (42 * 2 ^ 47) (-47) eq_refl
  | K_72 => @B754_finite 53 1024 false (72 * 2 ^ 46) (-46) eq_refl
  | K_110 => @B754_finite 53 1024 false (110 * 2 ^ 46) (-46) eq_refl
  | K_156 => @B754_finite 53 1024 false (156 * 2 ^ 45) (-45) eq_refl
  | K_210 => @B754_finite 53 1024 false (210 * 2 ^ 45) (-45) eq_refl
  end.

Definition tieee_ops : TOPS b64 := {|
  t_add := @Bplus 53 1024 prec64_gt_0 prec64_lt_emax mode_NE;
  t_sub := @Bminus 53 1024 prec64_gt_0 prec64_lt_emax mode_NE;
  t_mul := @Bmult 53 1024 prec64_gt_0 prec64_lt_emax mode_NE;
  t_div := @Bdiv 53 1024 prec64_gt_0 prec64_lt_emax mode_NE;
  t_abs := @Babs 53 1024;
  t_neg := @Bopp 53 1024;
  t_sel_le := fun a b c d => if @Bltb 53 1024 a b then c else d;
  t_sel_lt := fun a b c d => if @Bltb 53 1024 a b then c else d;
  t_cst := tieee_cst |}.

(* 4. The shapes, in the graph file's own stages. *)
Definition T_narrow (T : Type) (o : TOPS T) (v : T) : T :=
  t_sel_le o (t_abs o v) (t_cst o K_HH) (t_mul o v (t_cst o K_0))
    (t_sel_lt o (t_abs o v) (t_cst o K_TT) (t_sub o (t_add o v (t_cst o K_MM)) (t_cst o K_MM))
      (t_sub o (t_mul o (t_cst o K_KK) v) (t_sub o (t_mul o (t_cst o K_KK) v) v))).

Definition T_N (T : Type) (o : TOPS T) (v : T) : T := t_sub o (t_add o v (t_cst o K_CN)) (t_cst o K_CN).
Definition T_f (T : Type) (o : TOPS T) (x : T) : T := t_sub o x (T_N T o x).
Definition T_q (T : Type) (o : TOPS T) (x : T) : T := t_mul o (t_cst o K_4) (T_f T o x).
Definition T_k (T : Type) (o : TOPS T) (x : T) : T := T_N T o (T_q T o x).
Definition T_r (T : Type) (o : TOPS T) (x : T) : T := t_sub o (T_q T o x) (T_k T o x).

Definition T_arg (T : Type) (o : TOPS T) (v : T) : T := t_mul o v (t_cst o K_PH).
Definition T_sq (T : Type) (o : TOPS T) (v : T) : T := t_mul o v v.
Definition T_poly (T : Type) (o : TOPS T) (u : T) : T :=
  t_sub o (t_cst o K_1) (t_div o (t_mul o u
  (t_sub o (t_cst o K_1) (t_div o (t_mul o u
  (t_sub o (t_cst o K_1) (t_div o (t_mul o u
  (t_sub o (t_cst o K_1) (t_div o (t_mul o u
  (t_sub o (t_cst o K_1) (t_div o (t_mul o u
  (t_sub o (t_cst o K_1) (t_div o (t_mul o u
  (t_sub o (t_cst o K_1) (t_div o u (t_cst o K_210))))
  (t_cst o K_156)))) (t_cst o K_110)))) (t_cst o K_72)))) (t_cst o K_42)))) (t_cst o K_20)))) (t_cst o K_6)).
Definition T_core (T : Type) (o : TOPS T) (v : T) : T :=
  t_mul o (T_arg T o v) (T_poly T o (T_sq T o (T_arg T o v))).
Definition T_S (T : Type) (o : TOPS T) (x : T) : T := T_core T o (T_r T o x).
Definition T_C (T : Type) (o : TOPS T) (x : T) : T :=
  T_core T o (t_sub o (t_cst o K_1) (t_abs o (T_r T o x))).

Definition T_sinpre (T : Type) (o : TOPS T) (x : T) : T :=
  t_sel_le o (t_cst o K_BIG) (t_abs o x) (t_mul o x (t_cst o K_0))
    (t_sel_le o (t_abs o (T_k T o x)) (t_cst o K_0) (T_S T o x)
      (t_sel_le o (t_abs o (T_k T o x)) (t_cst o K_1)
        (t_sel_le o (t_cst o K_0) (T_k T o x) (T_C T o x) (t_neg o (T_C T o x)))
        (t_neg o (T_S T o x)))).

Definition T_cospre (T : Type) (o : TOPS T) (x : T) : T :=
  t_sel_le o (t_cst o K_BIG) (t_abs o x) (t_cst o K_1)
    (t_sel_le o (t_abs o (T_k T o x)) (t_cst o K_0) (T_C T o x)
      (t_sel_le o (t_abs o (T_k T o x)) (t_cst o K_1)
        (t_sel_le o (t_cst o K_0) (T_k T o x) (t_neg o (T_S T o x)) (T_S T o x))
        (t_neg o (T_C T o x)))).

Definition T_sinturn32 (T : Type) (o : TOPS T) (x : T) : T := T_narrow T o (T_sinpre T o x).
Definition T_costurn32 (T : Type) (o : TOPS T) (x : T) : T := T_narrow T o (T_cospre T o x).

(* 5. Each shape at the model is its graph: eq_refl. Where a term is given it is the graph, by name for the
   polynomial and the core, and for the six definitions from T_S_model on written out: every rounding as RN64 and
   every value used more than once named once (with the graph's name for the term the check of T_S took 36 s and
   that of T_sinpre did not end in 40 s). Nothing rests on the term. *)
Definition T_narrow_model : forall v : R, T_narrow R tmodel_ops v = narrow v := fun v => eq_refl.
Definition T_N_model : forall v : R, T_N R tmodel_ops v = turn_N v := fun v => eq_refl.
Definition T_f_model : forall x : R, T_f R tmodel_ops x = turn_f x := fun x => eq_refl.
Definition T_q_model : forall x : R, T_q R tmodel_ops x = turn_q x := fun x => eq_refl.
Definition T_k_model : forall x : R, T_k R tmodel_ops x = turn_k x := fun x => eq_refl.
Definition T_r_model : forall x : R, T_r R tmodel_ops x = turn_r x := fun x => eq_refl.
Definition T_arg_model : forall v : R, T_arg R tmodel_ops v = turn_arg v := fun v => eq_refl.
Definition T_sq_model : forall v : R, T_sq R tmodel_ops v = sin32_sq v := fun v => eq_refl.
Definition T_poly_model : forall u : R, T_poly R tmodel_ops u = sin32_poly u := fun u => eq_refl (sin32_poly u).
Definition T_core_model : forall v : R, T_core R tmodel_ops v = turn_core v := fun v => eq_refl (turn_core v).
Definition T_S_model : forall x : R, T_S R tmodel_ops x = turn_S x := fun x => eq_refl
    (let n := RN64 (RN64 (x + turn_CN) - turn_CN) in
     let f := RN64 (x - n) in
     let q := RN64 (4 * f) in
     let k := RN64 (RN64 (q + turn_CN) - turn_CN) in
     let r := RN64 (q - k) in
     let a1 := RN64 (r * cos32_PH) in let u1 := RN64 (a1 * a1) in RN64 (a1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (u1 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))).
Definition T_C_model : forall x : R, T_C R tmodel_ops x = turn_C x := fun x => eq_refl
    (let n := RN64 (RN64 (x + turn_CN) - turn_CN) in
     let f := RN64 (x - n) in
     let q := RN64 (4 * f) in
     let k := RN64 (RN64 (q + turn_CN) - turn_CN) in
     let r := RN64 (q - k) in
     let w := RN64 (1 - Rabs r) in
     let a2 := RN64 (w * cos32_PH) in let u2 := RN64 (a2 * a2) in RN64 (a2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (u2 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))).
Definition T_sinpre_model : forall x : R, T_sinpre R tmodel_ops x = sinturn32_pre x :=
  fun x => eq_refl
    (let n := RN64 (RN64 (x + turn_CN) - turn_CN) in
     let f := RN64 (x - n) in
     let q := RN64 (4 * f) in
     let k := RN64 (RN64 (q + turn_CN) - turn_CN) in
     let r := RN64 (q - k) in
     let s := (let a1 := RN64 (r * cos32_PH) in let u1 := RN64 (a1 * a1) in RN64 (a1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (u1 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))) in
     let w := RN64 (1 - Rabs r) in
     let c := (let a2 := RN64 (w * cos32_PH) in let u2 := RN64 (a2 * a2) in RN64 (a2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (u2 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))) in
     if Rle_dec turn_BIG (Rabs x) then RN64 (x * 0)
     else if Rle_dec (Rabs k) 0 then s
     else if Rle_dec (Rabs k) 1 then (if Rle_dec 0 k then c else - c)
     else - s).
Definition T_cospre_model : forall x : R, T_cospre R tmodel_ops x = costurn32_pre x :=
  fun x => eq_refl
    (let n := RN64 (RN64 (x + turn_CN) - turn_CN) in
     let f := RN64 (x - n) in
     let q := RN64 (4 * f) in
     let k := RN64 (RN64 (q + turn_CN) - turn_CN) in
     let r := RN64 (q - k) in
     let s := (let a1 := RN64 (r * cos32_PH) in let u1 := RN64 (a1 * a1) in RN64 (a1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (u1 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))) in
     let w := RN64 (1 - Rabs r) in
     let c := (let a2 := RN64 (w * cos32_PH) in let u2 := RN64 (a2 * a2) in RN64 (a2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (u2 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))) in
     if Rle_dec turn_BIG (Rabs x) then 1
     else if Rle_dec (Rabs k) 0 then c
     else if Rle_dec (Rabs k) 1 then (if Rle_dec 0 k then - s else s)
     else - c).
Definition T_sinturn32_model : forall x : R, T_sinturn32 R tmodel_ops x = g_sinturn32 x :=
  fun x => eq_refl
    (narrow
    (let n := RN64 (RN64 (x + turn_CN) - turn_CN) in
     let f := RN64 (x - n) in
     let q := RN64 (4 * f) in
     let k := RN64 (RN64 (q + turn_CN) - turn_CN) in
     let r := RN64 (q - k) in
     let s := (let a1 := RN64 (r * cos32_PH) in let u1 := RN64 (a1 * a1) in RN64 (a1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (u1 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))) in
     let w := RN64 (1 - Rabs r) in
     let c := (let a2 := RN64 (w * cos32_PH) in let u2 := RN64 (a2 * a2) in RN64 (a2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (u2 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))) in
     if Rle_dec turn_BIG (Rabs x) then RN64 (x * 0)
     else if Rle_dec (Rabs k) 0 then s
     else if Rle_dec (Rabs k) 1 then (if Rle_dec 0 k then c else - c)
     else - s)).
Definition T_costurn32_model : forall x : R, T_costurn32 R tmodel_ops x = g_costurn32 x :=
  fun x => eq_refl
    (narrow
    (let n := RN64 (RN64 (x + turn_CN) - turn_CN) in
     let f := RN64 (x - n) in
     let q := RN64 (4 * f) in
     let k := RN64 (RN64 (q + turn_CN) - turn_CN) in
     let r := RN64 (q - k) in
     let s := (let a1 := RN64 (r * cos32_PH) in let u1 := RN64 (a1 * a1) in RN64 (a1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (RN64 (u1 * RN64 (1 - RN64 (u1 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))) in
     let w := RN64 (1 - Rabs r) in
     let c := (let a2 := RN64 (w * cos32_PH) in let u2 := RN64 (a2 * a2) in RN64 (a2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (RN64 (u2 * RN64 (1 - RN64 (u2 / 210))) / 156))) / 110))) / 72))) / 42))) / 20))) / 6)))) in
     if Rle_dec turn_BIG (Rabs x) then 1
     else if Rle_dec (Rabs k) 0 then c
     else if Rle_dec (Rabs k) 1 then (if Rle_dec 0 k then - s else s)
     else - c)).

(* 6. The statements. The real number of a binary64 value b is B2R b. *)
Definition IEEE_SINTURN32 : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (T_sinturn32 b64 tieee_ops b) = true /\
  B2R (T_sinturn32 b64 tieee_ops b) = g_sinturn32 (B2R b).

Definition IEEE_COSTURN32 : Prop :=
  forall b : b64, is_finite b = true -> format32 (B2R b) ->
  is_finite (T_costurn32 b64 tieee_ops b) = true /\
  B2R (T_costurn32 b64 tieee_ops b) = g_costurn32 (B2R b).

Definition IEEE_TCST : Prop :=
  forall c : tconst, is_finite (t_cst tieee_ops c) = true /\ B2R (t_cst tieee_ops c) = t_cst tmodel_ops c.

Definition SINCOS32_IEEE : Prop := IEEE_SINTURN32 /\ IEEE_COSTURN32 /\ IEEE_TCST.
