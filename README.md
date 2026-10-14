# PRACH sequence research baseline

This repository is a small, executable reference for generating Zadoff–Chu
(ZC) roots and cyclic-shift preambles in Python and C++. That educational
generator baseline remains unchanged. A separate Python receiver research
prototype adds synthetic samples and deterministic detection—not a learned
generator, production receiver, or complete 3GPP PRACH implementation.

## Start here

1. Read the [designer reading guide](docs/README.md).
2. Read the [verified primary-paper summary](docs/research/primary-paper-summary.md)
   and [baseline architecture](docs/architecture.md).
3. Use the [repository/file guide](docs/repository-guide.md) to find each
   tracked file and decide where to make a change.

The supplied primary paper proposes Kronecker-product-structured (KPS)
preambles and a two-stage detector. Those methods are research context only;
the generator implements ordinary deterministic ZC roots and cyclic shifts.
See the [paper-to-code traceability table](docs/research/primary-paper-summary.md#paper-to-project-traceability).

## Prerequisites

- Python 3 (3.8+ for the receiver's typing protocol; standard library only)
- A C++17 compiler such as `g++`

No Python packages, model weights, or build system are required.

## Run the examples

From the repository root:

```sh
python3 -m examples.python.reference_demo
```

Expected output:

```text
Generated 64 preambles
First preamble: root=1, shift=0
Last preamble: root=1, shift=819
```

Build and run the C++ equivalent:

```sh
g++ -std=c++17 -Wall -Wextra -pedantic -Icpp \
  cpp/prach_reference.cpp examples/cpp/main.cpp \
  -o /tmp/prach_reference
/tmp/prach_reference
```

The C++ output is the same as the Python example. The original direct Python
entry point also remains available: `python3 python/prach_reference.py`.

## Receiver research prototype

The separate [`python/receiver/`](python/receiver/) path is inspired by the
receiver tasks in [“Enhancements for 5G NR PRACH Reception: An AI/ML
Approach”](references/supporting/2401.12803v1.pdf). It does **not** reproduce
the paper's neural networks, frequency-domain inputs, or performance results.

```sh
python3 -m examples.python.receiver_demo
python3 -m examples.python.receiver_demo --seed 7 --snr-db 5 \
  --max-delay 3 --max-doppler 0.01 --collision-probability 0.5
```

- `dataset.py`: seeded complex AWGN, integer sample delays, normalized Doppler,
  and user superposition; per-user ID/root/shift/delay and collision labels.
- `baseline.py`: template correlation, sample-delay estimation, and a residual
  collision heuristic. Same-preamble/same-delay collisions are unidentifiable.
- `evaluate.py`: primary-ID/top-k accuracy, conditional delay MAE/RMSE, and
  collision precision/recall. The demo also reports runtime.
- `model.py`: I/Q feature adapter and learned-receiver interface **only**;
  no trained model, ML framework, or training/inference implementation.

The demo uses a small length-31 bank for speed. Metrics are toy experiments,
not standards validation or claimed gains. See the
[signal model and limitations](docs/architecture.md#receiver-research-prototype)
and [validation commands](docs/validation.md#receiver-research-validation).

## Tests and validation

```sh
python3 -m unittest discover -s tests -v
```

The suite checks ZC properties, shift/allocation behavior, receiver experiments,
runnable examples, and internal Markdown link targets. The repeatable workflow,
including PDF checksum verification and Python/C++ numerical comparison
conventions, is in [validation notes](docs/validation.md).

## Scope and limitations

The generator creates sequence samples and a simple root/shift-to-ID mapping. It
does not implement PRACH waveform/resource mapping, cyclic prefix or guard
time, format-specific restricted sets, a gNB detector, UE/gNB signaling,
collision handling, or normative configuration rules. The receiver prototype
is sample-domain research only, with no collision resolution or physical TA
commands. The repository contains no AI/ML training or inference code.
The proposed KPS waveform/detector, as well as
previously sketched diffusion/transformer ideas, must not be mistaken for
implemented functionality or standardized 6G behavior.

See [future work and extension points](docs/architecture.md#extension-points)
for the boundaries and next steps.
