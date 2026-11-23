# SPDX-License-Identifier: AGPL-3.0-only
# The image the Linux CI's gates run in (.github/workflows/mathkernel-linux.yml): Ubuntu 24.04, OCaml 4.14.2, Coq
# 8.20.1 and Flocq 4.2.1 from opam. It is not the image behind THEOREMS.md's verdicts, which were made in a Debian image
# whose recipe is not in this tree. Coq is in opam's default repository; coq-flocq is not (opam.ocaml.org has no
# coq-flocq page: HTTP 404, read 2026-11-17). It is in the Rocq/Coq "released" repository, added below as that
# repository's README says. Its release build needs a C++ compiler (build-essential); autoconf is installed as a
# precaution, needed only for development builds. The base image is pinned by its digest: the one the ubuntu:24.04
# tag resolved to in the four CI image builds that ci/mathkernel/EXPECTED-TOOLCHAIN.txt names. The install line pins
# the two packages it names, coq and coq-flocq, by version. The apt packages, both opam repositories and every
# dependency below those two are as they stand at build time. No dependency is named on the install line: opam would
# make it a root of the switch, and the switch export the record holds would change. Instead
# ci/mathkernel/EXPECTED-TOOLCHAIN.txt records the version of every opam package the four builds installed, apart from
# the compiler's three base-* packages, which the check allows by name at version "base", so a dependency that drifts
# fails the toolchain check (a review event). So the build records what it got: the whole opam
# switch is exported to /opt/mk-switch.export, and the image job prints it, the repositories, the base image's digest,
# the image's id and the sha256 of coqc, coqchk and python3; tools/ci/check_toolchain.py compares what
# tools/ci/toolchain_probe.sh prints inside the image with
# ci/mathkernel/EXPECTED-TOOLCHAIN.txt. Before the image is kept, it must load Flocq and Coq's reals. No kernel source
# enters the image: the gate's tree is mounted at run time. The container runs as root, so a gate can write its out4
# folders into the mounted tree.
FROM ubuntu:24.04@sha256:73b999393d07f2bf65a40373778a44dc9a6d54ad7718d29247d8ff9413c4d6a8

ENV DEBIAN_FRONTEND=noninteractive \
    OPAMROOT=/opt/opam \
    OPAMYES=1

RUN apt-get update \
 && apt-get install --yes --no-install-recommends \
      autoconf ca-certificates curl git build-essential libgmp-dev m4 opam patch pkg-config python3 unzip \
 && rm -rf /var/lib/apt/lists/*

RUN opam init --bare --disable-sandboxing --yes default https://opam.ocaml.org \
 && opam switch create 4.14.2 ocaml-base-compiler.4.14.2 --yes \
 && opam repo add --switch=4.14.2 rocq-released https://rocq-prover.org/opam/released \
 && opam install --switch=4.14.2 --yes coq.8.20.1 coq-flocq.4.2.1 \
 && opam switch export --switch=4.14.2 /opt/mk-switch.export \
 && opam clean --all-switches --download-cache --logs

ENV OPAMSWITCH=4.14.2 \
    PATH=/opt/opam/4.14.2/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN coqc --version \
 && command -v coqchk \
 && python3 --version \
 && mkdir /tmp/smoke \
 && printf 'From Coq Require Import Reals Lia.\nFrom Flocq Require Import Core.\nCheck generic_format.\n' > /tmp/smoke/Smoke.v \
 && coqc -Q /tmp/smoke Smoke /tmp/smoke/Smoke.v \
 && rm -rf /tmp/smoke \
 && opam list --installed --columns=name,version coq coq-core coq-stdlib coq-flocq
