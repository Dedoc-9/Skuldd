# SPDX-License-Identifier: AGPL-3.0-only
# The image the Linux CI's gates run in (.github/workflows/mathkernel-linux.yml): Ubuntu 24.04, OCaml 4.14.2, Coq
# 8.20.1 and Flocq 4.2.1 from opam. Coq is in opam's default repository; coq-flocq is not (opam.ocaml.org has no
# coq-flocq page: HTTP 404, read 2026-11-17). It is in the Rocq/Coq "released" repository, added below as that
# repository's README says, and its build needs autoconf and a C++ compiler. The top-level versions are pinned; the
# base image is the ubuntu:24.04 tag and both opam repositories are as they stand at build time, so the build records
# what it got (the image job prints the versions and the sha256 of coqc, coqchk and python3). No kernel source enters
# the image: the gate's tree is mounted at run time. The container runs as root, so a gate can write its out4 folders
# into the mounted tree.
FROM ubuntu:24.04

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
 && opam clean --all-switches --download-cache --logs

ENV OPAMSWITCH=4.14.2 \
    PATH=/opt/opam/4.14.2/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN coqc --version \
 && python3 --version \
 && opam list --installed --columns=name,version coq coq-core coq-stdlib coq-flocq
