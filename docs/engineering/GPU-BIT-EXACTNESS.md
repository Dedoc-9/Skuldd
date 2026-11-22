# Bit-exact results on Direct3D GPUs

An engineering note, written by the assistant at the owner's request of 2026-11-18. Nothing in it is proved in this
tree, and no GPU result is part of the guarantee of `docs/paper/SYSTEM-GUARANTEES.md`. Every claim carries its grade:
READ (a source was read), MEASURED (a run produced the number), REPORTED (an agent of the assistant's model family read
or ran it, not checked again), DECLARED (a vendor's promise not measured here), ARGUED (reasoned, not run or
proved), NOT_MEASURED.

## The statement it answers

> Microsoft's Direct3D documents confirm that 32-bit GPU shaders may truncate rather than round, flush denormals to
> zero, and allow 1-ULP error on sqrt and rcp, so a GPU result can be checked against the reference but never
> guaranteed bit-exact.

The first half is true of Direct3D's 32-bit floating-point instructions: their rules allow truncation, flush
denormals, allow sqrt and rcp to be 1 ULP off, leave fused operations loose and give no rounding control (REPORTED:
the truncation allowance from Microsoft's page "Floating-point rules (Direct3D 11)" on learn.microsoft.com, read by
a research agent on 2026-11-21; the other rules from the Direct3D 11.3 functional specification, section 3.1, read
by two research agents). The second half does not follow for every kernel. Those rules bind fp32 instructions only.
A kernel in which **no fp32 instruction decides an output bit** is outside them.

## How a kernel stays exact

Direct3D specifies its integer instructions exactly: 32-bit results wrap modulo 2^32, there is no ULP allowance, no
truncation option and no flush (REPORTED: Microsoft's assembly reference pages for iadd, umul, udiv, uaddc and ishl,
and DXC's DXIL.rst; the integer chapter of the D3D11.3 specification was not read). Two kinds of kernel use only that:

- **An integer kernel** computes the correctly rounded binary32 result with 32-bit integer operations alone.
- **A proposal and an exact decision.** The device's own fp32 result is a candidate only. An integer test compares
  the candidate with the exact value and accepts it, corrects it within a bounded number of steps, or falls back to
  the integer kernel. The device's fp32 accuracy then changes the speed, never the answer.

Either way the output bits rest on the integer semantics and on the kernel's own logic, not on the device's
floating-point accuracy. That is ARGUED, and for one function it is MEASURED below; it is not proved.

Three things a compiled shader must also be held to, each found in this work (MEASURED unless marked):

- **The exact operation list.** DXC's default compile folded the binary64 narrowing step
  `c = (2^29 + 1) * v; r = c - (c - v)` to the identity, which no "forbidden instruction" rule would catch. So a gate
  compares every compiled shader's DXIL operations with a pinned list, and refuses any difference.
- **LLVM's undefined behaviour.** DXIL's integer code is LLVM IR: division by zero is undefined and `nsw` overflow is
  poison. The gate refuses the `nsw`, `nuw` and `exact` flags and every integer division; the kernels use unsigned
  integers only. DXC releases before late 2026 could emit wrong no-wrap flags (REPORTED), so the gate refuses the
  flags instead of trusting them.
- **Intrinsics that replace user code.** HLSL's float intrinsic `normalize` silently replaced a user function of that
  name, with no warning under `-WX`. The gate's float rule caught it on the first disassembly; every kernel name is
  now prefixed and linted.

## What was measured: sqrt32 on Direct3D 12

- The reference: the output for every one of the 2^32 binary32 input patterns, computed from the operation sequence
  of the frozen sqrt32 graph (`kernel/coq/p32/Graphs.v`), with 512 chunk hashes fixed before any GPU run. MEASURED.
- Four kernels, two integer kernels and two proposal-and-decision kernels, returned output bits equal to the reference
  on all 4,294,967,296 input patterns on one hardware GPU (not named here). All four also did so on Microsoft's WARP
  software device, the first integer kernel and the first proposal kernel in their build at DXC's -O0. The output
  streams' sha256 equal the reference stream's. MEASURED: exhaustive, one host, one driver, one DXC release.
- The checks see a kernel that is not exact. A kernel with one planted bit error was reported at exactly that input.
  On the 2,139,095,039 positive finite inputs, the device's native fp32 sqrt differed from the reference on 330,391,011
  (denormal inputs flushed, results 1 ULP off), so that device does use the latitude the rules give. A proposal kernel
  with its integer decision removed returns the proposal and differed on the same 330,391,011. The gate accepted the
  four kernels and refused the native-sqrt kernel and the kernel without its decision. MEASURED.
- The CPU twins of the proposal kernels, given proposals that are wrong on purpose (one below, one above, two above,
  zero, with subnormals flushed, scrambled bits), gave 0 mismatches over the 2^32 inputs in every mode. MEASURED.

## What it does not show

- No proof. The kernels' correctness on all inputs is MEASURED on one device. That is a certificate of those runs on
  that device, driver and compiled shader: not a theorem, and not a guarantee for later runs. A Coq model of the
  integer subset the kernels use, and proofs about it, are in progress outside this tree; none of it is part of this
  tree.
- One GPU, one driver, one DXC release, and WARP. Other vendors and drivers: NOT_MEASURED. The exhaustive check must be
  run again for each device and driver.
- Not fault or tamper resistance. Every result here assumes hardware that executes its instructions as specified, in
  runs whose kernel, inputs and outputs no one alters. A hardware fault, transient or induced, can change any output,
  integer or float: unprivileged GPU code has flipped bits in GDDR6 memory and used them to read and write other
  processes' GPU memory (GPUHammer, USENIX Security 2025; GPUBreach, IEEE S&P 2026; REPORTED). A mismatch with the
  reference shows that a run was wrong, not whether a fault or a person made it wrong (ARGUED).
- One function. rsqrt32, hypot32, exp32 and the turns kernel have not run on a GPU. hypot32's frozen graph is faithful,
  not correctly rounded, so it needs binary64 arithmetic emulated in integers, or native doubles. Direct3D's doubles
  are optional and specified as IEEE 754 (DECLARED); the specification contradicts itself on double denormals and on
  the rounding of `dtof`, so neither is relied on here.
- Other routes were not run here: Vulkan's float controls (round to nearest even, denormals preserved, no contraction)
  and CUDA's `_rn` intrinsics give specified rounding for fp32 add, sub, mul and fma. NOT_MEASURED.
- The run records name the device and are kept outside this tree. The reference's hashes and the kernels' sources
  can be given.
