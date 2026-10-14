# PRACH sequence research baseline

This repository is a small, executable reference for generating Zadoff–Chu
(ZC) roots and cyclic-shift preambles in Python and C++. It is an educational
baseline—not a learned generator, receiver, or complete 3GPP PRACH
implementation.

## Start here

1. Read the [designer reading guide](docs/README.md).
2. Read the [verified primary-paper summary](docs/research/primary-paper-summary.md)
   and [baseline architecture](docs/architecture.md).
3. Use the [repository/file guide](docs/repository-guide.md) to find each
   tracked file and decide where to make a change.

The supplied primary paper proposes Kronecker-product-structured (KPS)
preambles and a two-stage detector. Those methods are research context only;
the code here implements ordinary deterministic ZC roots and cyclic shifts.
See the [paper-to-code traceability table](docs/research/primary-paper-summary.md#paper-to-project-traceability).

## Prerequisites

- Python 3 (standard library only)
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

## Tests and validation

```sh
python3 -m unittest discover -s tests -v
```

The suite checks ZC properties, shift/allocation behavior, a runnable-example
smoke test, and internal Markdown link targets. The repeatable workflow,
including PDF checksum verification and Python/C++ numerical comparison
conventions, is in [validation notes](docs/validation.md).

## Scope and limitations

The code creates sequence samples and a simple root/shift-to-ID mapping. It
does not implement PRACH waveform/resource mapping, cyclic prefix or guard
time, format-specific restricted sets, a gNB detector, UE/gNB signaling,
collision handling, or normative configuration rules. It contains no AI/ML
training or inference code. The proposed KPS waveform/detector, as well as
previously sketched diffusion/transformer ideas, must not be mistaken for
implemented functionality or standardized 6G behavior.

See [future work and extension points](docs/architecture.md#extension-points)
for the boundaries and next steps.
