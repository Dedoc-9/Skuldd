<!-- SPDX-License-Identifier: AGPL-3.0-only -->
# Third-party components

What this repository uses from other authors, and how. Nothing below is copied into the repository.

| Component | Licence | How it is used | In this tree |
|---|---|---|---|
| Coq 8.20.1 and its standard library | LGPL-2.1 (some parts BSD-3-Clause, Expat or LGPL-2+) | compiles and checks `kernel/coq` (coqc, coqchk), inside a pinned container image | no |
| Flocq 4.2.1 | LGPL-3 | the IEEE 754 formalisation the kernel's statements and proofs import | no |
| GNU MPFR 4.2.2 | LGPL-3.0-or-later (its manual GFDL-1.2-or-later) | the correctly rounded oracle of the exhaustive sweep of the turns kernel's law, linked at run time (the sweep's sources are withheld until the reviewer's blind formalisation exists) | no |
| GCC, Clang, rustc, CPython | their own licences | compile and run generated and measurement programs | no |
| CoqInterval 4.11.1 | CeCILL-C | its pattern (an operations record with integer constants, a program with sharing, one simulation theorem) was studied for the design; no code was copied | no |
| Engine content named by `verdandi/art` | that engine's EULA | named by path for an optional engine integration (36 entries in `verdandi/art/director/vectors.json`); no file of such content is in the tree | no |

The licences of Coq, Flocq, MPFR and CoqInterval were read from the Debian copyright files inside the pinned image
on 2026-11-17. What was checked in the tree (2026-11-17, by search over the assembled tree): every SPDX tag in the tree reads
`AGPL-3.0-only` (238 files); no copyright line names a holder other than the owner, apart from the Free Software
Foundation's lines inside the licence text; no JavaScript or HTML file carries another licence; no mesh, texture or
engine asset file is in `verdandi/`. A search shows what it searched for, not that nothing else exists.
