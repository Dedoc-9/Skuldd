(* Link.v: the proofs of FC_TEXT and FC_PARAM, the first two parts of FCLINK (statement in FCLINK_Statement.v, with
   CPrint.v and KernelText.v, which this file does not change). Coq's String library and the frozen statements only;
   every theorem ends with Qed and nothing is assumed. Author: the assistant (2026-11-21).

   How it goes.
   - FC_FLOOR_TEXT and FC_CEIL_TEXT, the two halves of FC_TEXT: each side is a closed string, computed by Coq's
     virtual machine (vm_compute) and then compared by reflexivity; coqchk checks the same equality again by the
     kernel's conversion, without the virtual machine. A changed byte on either side leaves two different closed
     strings, which reflexivity refuses.
   - FC_PARAM: the two shapes are unfolded (T_floor32 and FL_y, T_ceil32 and CL_y, and T_N) into one term of the
     record's fields, constants and input, the same term at tprint and at tieee_ops. Each node is then closed by the
     premise of FC_FIELDS for that field or constant, chosen by the node's head and found among the premises by its
     form, and each leaf x by the premise that rel relates the text x to v. No recursion and no induction: a finite
     number of steps, fixed by the two terms. *)
From Coq Require Import String.
From MKF.sincos32i Require Import SINCOS32_IEEE_Statement.
From MKF.floor32 Require Import FLOOR32_Statement.
From MKF.ceil32 Require Import CEIL32_Statement.
From MKF.fclink Require Import CPrint KernelText FCLINK_Statement.
Local Open Scope string_scope.

(* 1. The text. *)
Theorem FC_FLOOR_TEXT : c_fun1 "mk_floor32" (T_floor32 string tprint "x") = floor32_c_text.
Proof.
  vm_compute. reflexivity.
Qed.

Theorem FC_CEIL_TEXT : c_fun1 "mk_ceil32" (T_ceil32 string tprint "x") = ceil32_c_text.
Proof.
  vm_compute. reflexivity.
Qed.

Theorem FC_TEXT_proof : FC_TEXT.
Proof. exact (conj FC_FLOOR_TEXT FC_CEIL_TEXT). Qed.

(* 2. The parametricity. One step closes one node of the goal rel s w, where s and w are the same term of the record's
   fields at tprint and at tieee_ops: a premise of FC_FIELDS whose conclusion has the node's head, or a premise that
   is the goal itself (the four constants and the input). *)
Ltac fc_step :=
  match goal with
  | H : ?R ?a ?b |- ?R ?a ?b => exact H
  | |- ?R (t_sel_le _ _ _ _ _) (t_sel_le _ _ _ _ _) =>
      match goal with
      | H : forall (a : _) (a' : _) (b : _) (b' : _) (c : _) (c' : _) (d : _) (d' : _),
            ?R a a' -> ?R b b' -> ?R c c' -> ?R d d' -> ?R (t_sel_le _ a b c d) (t_sel_le _ a' b' c' d') |- _ => apply H
      end
  | |- ?R (t_sel_lt _ _ _ _ _) (t_sel_lt _ _ _ _ _) =>
      match goal with
      | H : forall (a : _) (a' : _) (b : _) (b' : _) (c : _) (c' : _) (d : _) (d' : _),
            ?R a a' -> ?R b b' -> ?R c c' -> ?R d d' -> ?R (t_sel_lt _ a b c d) (t_sel_lt _ a' b' c' d') |- _ => apply H
      end
  | |- ?R (t_add _ _ _) (t_add _ _ _) =>
      match goal with
      | H : forall (a : _) (a' : _) (b : _) (b' : _),
            ?R a a' -> ?R b b' -> ?R (t_add _ a b) (t_add _ a' b') |- _ => apply H
      end
  | |- ?R (t_sub _ _ _) (t_sub _ _ _) =>
      match goal with
      | H : forall (a : _) (a' : _) (b : _) (b' : _),
            ?R a a' -> ?R b b' -> ?R (t_sub _ a b) (t_sub _ a' b') |- _ => apply H
      end
  | |- ?R (t_mul _ _ _) (t_mul _ _ _) =>
      match goal with
      | H : forall (a : _) (a' : _) (b : _) (b' : _),
            ?R a a' -> ?R b b' -> ?R (t_mul _ a b) (t_mul _ a' b') |- _ => apply H
      end
  | |- ?R (t_abs _ _) (t_abs _ _) =>
      match goal with
      | H : forall (a : _) (a' : _), ?R a a' -> ?R (t_abs _ a) (t_abs _ a') |- _ => apply H
      end
  end.

Theorem FC_PARAM_proof : FC_PARAM.
Proof.
  unfold FC_PARAM. intros rel v HF Hx. unfold FC_FIELDS in HF.
  repeat match goal with H : _ /\ _ |- _ => destruct H end.
  cbv beta delta [T_floor32 FL_y T_ceil32 CL_y T_N].
  split.
  - solve [repeat fc_step].
  - solve [repeat fc_step].
Qed.
