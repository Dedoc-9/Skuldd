<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Third-party components

What this repository uses from other authors, and how. Nine fdlibm 5.3 source files are copied into the repository, in `verdandi/mathkernel/ORACLE/src/` (Copyright Sun Microsystems, Inc.; their notice permits use, copying, modification and distribution if it is preserved). Verðandi's graybox re-implements fdlibm 5.3's sine, cosine and atan2 algorithms, with fdlibm's constants and FreeBSD's later correction to atan2, in `verdandi/graybox/web/sim.js` and `verdandi/graybox/rules_ref.py`. Verðandi's characterization tooling (`verdandi/mathkernel/CHARACTERIZATION/tooling/`) imports gmpy2, python-flint and mpmath. None of these is in the table below, and nothing in the table is copied into the repository.

| Component | Licence | How it is used | In this tree |
|---|---|---|---|
| Coq 8.20.1 and its standard library | LGPL-2.1 (some parts BSD-3-Clause, Expat or LGPL-2+) | compiles and checks `kernel/coq` (coqc, coqchk), inside a pinned container image | no |
| Flocq 4.2.1 | LGPL-3 | the IEEE 754 formalisation the kernel's statements and proofs import | no |
| GNU MPFR 4.2.2 | LGPL-3.0-or-later (its manual GFDL-1.2-or-later) | the correctly rounded oracle of the exhaustive sweep of the turns kernel's law, linked at run time (the sweep's sources are withheld until the reviewer's blind formalisation exists) | no |
| GCC, Clang, rustc, CPython | their own licences | compile and run generated and measurement programs | no |
| CoqInterval 4.11.1 | CeCILL-C | its pattern (an operations record with integer constants, a program with sharing, one simulation theorem) was studied for the design; no code was copied | no |
| Engine content named by `verdandi/art` | that engine's EULA | named by path for an optional engine integration (36 entries in `verdandi/art/director/vectors.json`); no file of such content is in the tree | no |

From the Debian copyright files inside the container image of the kernel's runs, the licences of Coq, Flocq, MPFR and CoqInterval were read (DECLARED; no record of the reading is in this tree)
on 2026-11-17. What was checked in the tree (2026-11-17, by search over the assembled tree; no record of these searches is in this tree, and two of their results, the SPDX count and the copyright holders, were corrected after an audit of the same day): every SPDX tag in the tree reads
`AGPL-3.0-only` (245 files in the import); copyright lines name only the owner, apart from Sun Microsystems, Inc. in the nine fdlibm 5.3 files of `verdandi/mathkernel/ORACLE/src/` (and in three records of `verdandi/mathkernel/` that cite those lines) and the Free Software
Foundation's lines inside the licence text; no JavaScript or HTML file carries another licence; no mesh, texture or
engine asset file is in `verdandi/`. A search shows what it searched for, not that nothing else exists.
