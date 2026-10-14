# PRACH root-sequence and preamble design

## Scope

This repository describes UE-specific, AI/ML-driven PRACH root generation as a
possible 6G direction. The supplied `PRACHPreambleDesignfor6GWirelessSystems_final.pdf`
provides that motivation and the network/UE workflow. The initial code here is
deliberately a deterministic, standards-inspired reference baseline: it uses
classical Zadoff–Chu (ZC) roots and cyclic shifts so that the sequence
construction and allocation can be inspected and tested before introducing a
learned generator. It is not a complete 3GPP PRACH implementation.

## Terms and inputs

- **Sequence length** `N`: number of complex samples in a root sequence. NR
  long preambles use `N = 839`; short preambles use `N = 139`.
- **Root index** `u`: integer from 1 through `N - 1` that is relatively prime
  to `N`. Such a root generates a ZC sequence with constant magnitude and
  ideal periodic autocorrelation.
- **Cyclic-shift spacing** `N_CS`: the number of sequence samples between
  cyclically shifted candidates from the same root. Its standards-based choice
  depends on preamble format and cell/propagation conditions; this example
  accepts it as an explicit input.
- **Preamble ID**: ordered index assigned to a root/shift pair (IDs 0–63 in
  the default example).

## Generation and allocation flow

1. **Choose parameters.** Select an odd sequence length, a starting root, an
   `N_CS`, and the number of preambles required. In an operational system,
   `N_CS` and root restrictions must come from the selected PRACH format and
   its timing/Doppler assumptions, not from a universal fixed value.
2. **Generate a root.** For odd `N`, the code evaluates
   `x_u[n] = exp(-j π u n(n + 1) / N)`, for `n = 0, ..., N - 1`. The root
   index must be coprime to `N`. Each sample has unit magnitude.
3. **Make cyclic shifts.** For shift `C`, the reference uses
   `x_(u,C)[n] = x_u[(n + C) mod N]`. It creates
   `floor(N / N_CS)` shifts per root at `C = 0, N_CS, ...`. Preamble IDs are
   filled in shift order for one root before advancing to the next valid root.
4. **Return the preamble set.** Every generated entry includes its ID, root
   index, cyclic shift, and complex sequence. This makes the allocation
   inspectable and gives future detectors/training pipelines explicit labels.
5. **Check before deployment.** Verify correlation under the intended channel,
   timing uncertainty, Doppler, and multi-cell reuse assumptions. A cyclic-shift
   count alone does not establish a valid cell plan.

## Base implementation and extension points

The Python and C++ implementations perform the same four operations: validate
parameters, generate a ZC root, cyclically shift it, and allocate preamble IDs
across valid roots. They intentionally use only standard libraries.

The PDF's AI/ML direction can later replace or augment root generation and
network selection using learned models, codebooks, or channel context. Such an
extension must preserve a UE/gNB-agreed mapping and be evaluated against
physical-layer constraints (including correlation, transmit energy, timing,
Doppler, and legacy coexistence). No learned model, training data, signaling
format, or receiver is implemented here; those require separate design and
standards validation.

This example omits format-specific restricted sets, unrestricted-set
special-cases, cyclic-prefix/guard-time construction, PRACH resource mapping,
detector processing, and normative 3GPP configuration rules. Consult the
applicable 3GPP TS 38.211 and RACH configuration specifications for those
details.
