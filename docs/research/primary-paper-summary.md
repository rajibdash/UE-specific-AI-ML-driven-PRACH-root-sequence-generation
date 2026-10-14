# Primary paper summary: PRACH Preamble Design for 6G Wireless Systems

## Source and scope

**Paper:** Fan Zhang, Hanyu Liu, Zihan Liu, Tianqi Mao, Christos Masouros, and
Zhaocheng Wang, “PRACH Preamble Design for 6G Wireless Systems.” The six-page
PDF is the repository's primary research source:

- [Local copy](../../references/primary/PRACHPreambleDesignfor6GWirelessSystems_final.pdf)
- [Source PDF pinned to the supplied repository commit
  `eaff8f6f317f1ad6d7f26549832cc16b5a3f4b09`](https://github.com/rajibdash/UE-specific-AI-ML-driven-PRACH-root-sequence-generation/blob/eaff8f6f317f1ad6d7f26549832cc16b5a3f4b09/PRACHPreambleDesignfor6GWirelessSystems_final.pdf)

I extracted all six pages from the tracked binary with `pdftotext -layout` and
reviewed the extracted text, equations, and figure captions page by page.
Page numbers below refer to the printed PDF page sequence (1–6). This summary
paraphrases the paper; the paper's findings are not results produced by this
repository.

## Verified design points and terminology

The paper's motivation is massive random access under capacity, Doppler, and
detection-complexity constraints. It notes that conventional Zadoff–Chu (ZC)
sequences and restricted sets face a capacity/robustness trade-off at high
mobility. The contribution is **not** a learned or UE-specific generator. It
proposes a **Kronecker-product-structured (KPS)** sequence family and a
low-complexity two-stage receiver.

The paper's construction is summarized below using its notation:

- Let $P_O=\{p_i\}$ and $P_I=\{q_j\}$ be outer and inner sequence sets,
  with lengths $L_O$ and $L_I$. The KPS set is
  $P=\{p_i\otimes q_j\}$, with $N=N_O N_I$ sequences (p. 3, Eq. 10).
- A KPS sequence is segmented: its samples satisfy
  $s_{iN_I+j}[n_1L_I+n_2]=p_i[n_1]q_j[n_2]$ (p. 3, Eqs. 11–12).
  Each outer-sequence sample scales one inner-sequence segment.
- Cyclic shifts indexed by $\delta$ are applied to create preambles
  (p. 3, Eq. 13). The sequence-set size and allowable shifts jointly determine
  the number of preambles; this is not the same allocation rule as the
  repository's simple `floor(length / n_cs)` model.
- Two examples are **m-ZC KPS** (M-sequence outer component, ZC inner
  component) and **m-Alltop KPS** (M-sequence outer component, Alltop inner
  component). The paper gives their sequence-set capacities in Eqs. 16 and 18
  (p. 4): respectively
  $(L_I-1)\phi(L_O)/\log_2(L_O+1)$ and
  $L_I^2\phi(L_O)/\log_2(L_O+1)$, where $\phi$ is Euler's totient function.
- Its design guidance (pp. 3–4) asks both component sets to have suitable
  auto-/cross-correlation; favors Doppler robustness in the outer component;
  and notes that a binary outer sequence can avoid multiplications in the
  corresponding correlation stage.

**Receiver workflow:** the conventional PRACH signal model and receiver appear
in Section II (pp. 2–3; Figs. 1–2). The proposed detector in Section IV
(pp. 4–5; Fig. 4) first correlates against inner sequences, reshapes/reuses
those results for outer-sequence correlations with Doppler compensation, and
retains candidate users. A second stage performs finer Doppler-compensated
correlations and a threshold test on the candidates. Equations 19–30 describe
the correlation, candidate selection, and timing/sequence identification.
This is a base-station detection algorithm, not a UE-side learned encoder.

## Evaluation reported in the paper

Section V (pp. 5–6; Figs. 5–6) reports numerical/simulation comparisons for
m-ZC and m-Alltop KPS. The stated setup uses DFT-s-OFDM, 2048 subcarriers,
6.7 GHz carrier frequency, 1.25 kHz subcarrier spacing, a CDL-C channel, one
transmit and four receive antennas, and a Doppler range of $[-5,5]$ kHz.
The two-stage evaluation uses 10 candidates; the paper fixes false-alarm
probability at $10^{-3}$. The authors report an 80% computational-complexity
reduction at 6400 supported UEs and say the finer second stage brings
detection performance close to the conventional detector after a small
increase over the one-stage method.

These values are **the paper's reported simulation results**, not measurements
from this code. The six-page paper presents numerical results, not a
deployment or over-the-air validation of the proposed KPS receiver. Its
conclusion (p. 6) describes KPS and the two-stage detector as a design for
large-capacity, lower-complexity PRACH. The result should be read within the
paper's stated system, channel, parameter, and threshold assumptions; the
repository does not reproduce its experiments.

## Other PDFs in the repository

- [`2401.12803v1.pdf`](../../references/supporting/2401.12803v1.pdf) is
  Rohit Singh, Anil Kumar Yerrapragada, Jeeva Keshav S, and Radha Krishna
  Ganti, “Enhancements for 5G NR PRACH Reception: An AI/ML Approach”
  (arXiv:2401.12803v1, 12 January 2024; six pages). It studies parallel
  neural-network RAPID detection and timing-advance estimation for a
  single-base-sequence receiver using simulated and over-the-air captures.
  It is receiver research, not the KPS sequence-design source. Its neural
  networks are not implemented here; the separate `python/receiver/` prototype
  uses its receiver tasks as motivation only. Its conclusion identifies more base sequences, scenarios,
  and multi-user collision detection as future work.
- [`6G AI-Driven Air Interface.pdf`](../../references/supporting/6G%20AI-Driven%20Air%20Interface.pdf)
  is Hamed Farhadi et al., “6G AI-Driven Air Interface — Hexa-X-II View”
  (IEEE Communications Magazine, 2025; eight pages). It surveys motivations,
  selected PHY applications, standardization, and adoption challenges for an
  AI-driven air interface. It is general 6G context, not a PRACH sequence
  design or evidence for this project's proposed signaling/model choices.

## Paper-to-project traceability

| PDF page / section | Paper concept | Python / C++ relationship | Relevant tests | Project status |
| --- | --- | --- | --- | --- |
| p. 1, Abstract and Section I | Massive-access motivation; KPS family and two-stage detector are the paper's contributions | No corresponding KPS or KPS detector implementation; see [architecture scope](../architecture.md#scope-and-implemented-flow) | None for KPS | Research context; not implemented |
| pp. 2–3, Section II, Figs. 1–2, Eqs. 1–9 | DFT-s-OFDM transmitter, channel, and conventional receiver model | The ZC sample generator is at `python/prach_reference.py::zadoff_chu_root_sequence` and `cpp/prach_reference.cpp::zadoff_chu_root_sequence`; the separate toy receiver has no DFT-s-OFDM chain or paper channel model | `test_root_sequence_has_constant_amplitude_and_zero_cyclic_autocorrelation` | ZC root math is implemented; paper PRACH physical-layer chain is out of scope |
| pp. 3–4, Section III, Fig. 3, Eqs. 10–18 | KPS outer/inner construction; M-sequence × ZC/Alltop examples and capacity | No KPS, M-sequence, Alltop, or capacity code in either language | None | Proposed research method; not implemented |
| p. 3, Section III, Eq. 13 | Cyclically shifted KPS preambles | `python/prach_reference.py::cyclically_shift` / `generate_preambles`; `cpp/prach_reference.hpp::cyclically_shift` / `generate_preambles` provide a simpler ZC cyclic-shift mapping, not Eq. 13's full KPS procedure | `test_cyclic_shift_uses_documented_direction`; `test_preamble_ids_fill_shifts_then_advance_to_next_root` | Related primitive is implemented; KPS allocation is not |
| pp. 4–5, Section IV, Fig. 4, Eqs. 19–30 | Two-stage inner/outer correlation, Doppler compensation, candidate refinement, and detection | No KPS detector in either language; `python/receiver/baseline.py` is an unrelated ordinary-ZC correlator | None for KPS | Out of scope; requires separate system and signal model |
| pp. 5–6, Section V, Figs. 5–6 | Complexity and missed-detection simulation results under the paper's stated setup | Not run or reproduced by this repository | None | Reported paper evidence only; not a project benchmark |
| p. 6, Section VI | Authors' conclusion on KPS and the proposed detector | No direct executable mapping | None | Paper conclusion, not an implemented or standardized feature |

## Distinguishing proposals from implementation

### Supporting receiver paper to prototype

The supporting PDF was also checked with `pdftotext -layout`. Section III
(pp. 3–4, Figs. 3–5) describes parallel independent ResNet-like networks for
RAPID and TA classification, using frequency-domain samples extracted from
the OFDM resource grid. Sections III–IV compare simulated TDL-channel and
OTA captures; Section V (p. 6) leaves additional base sequences, channel
scenarios, and multi-user collision detection to future work.

| Supporting-paper idea | Actual project code | Status / validation |
| --- | --- | --- |
| RAPID and TA receiver tasks, Section III | `python/receiver/dataset.py` labels; `baseline.py` ID and integer sample-delay estimates | Toy ZC-sample model, not resource-grid input or physical TA; `tests/test_receiver.py` |
| Correlation comparison, Section IV | Exhaustive template/delay correlation in `baseline.py`; accuracy and conditional delay metrics in `evaluate.py` | Deterministic research reference, not a reproduction of the paper's correlator/results |
| Parallel neural networks, Section III, Fig. 3 | `model.py::ReceiverModel` and `iq_features` | Interface/features only; no ResNet, training, inference, or performance claim |
| Multi-user collision detection, Section V future work | Synthetic superposition labels and residual-correlation heuristic | Project research choice, not a completed paper result; tests include an unidentifiable same-ID/same-delay case |

The prototype's small bank, linear padding/delay, AWGN, normalized Doppler,
collision thresholds, and metrics are **project choices**, not the paper's
experimental configuration. No simulated or OTA gains reported by the paper
are claimed for this code. See the [receiver architecture](../architecture.md#receiver-research-prototype).

The current **implemented baseline** is deterministic odd-length ZC root
generation, cyclic shifting, and sequential ID allocation across roots. It is
not the paper's KPS family. The paper's KPS design is a **research proposal in
the primary source**, not part of this code.

An older project sketch mentioned UE-specific neural generation and
diffusion/transformer models. Those are separate **unvalidated project
ideas**; they are neither proposed in the primary KPS paper nor implemented
here. There are no trained models, fixed training datasets, UE/gNB signaling
protocol, complete PHY transmitter/receiver, or standards-compliant 6G
implementation. The new synthetic dataset and deterministic receiver research
path do not change the implemented generator baseline.
