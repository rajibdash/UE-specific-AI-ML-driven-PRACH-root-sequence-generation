# Repository and file guide

## Tracked tree

```text
.
├── .gitignore
├── DESIGN.md
├── LICENSE
├── README.md
├── cpp/
│   ├── prach_reference.cpp
│   └── prach_reference.hpp
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── repository-guide.md
│   ├── research/
│   │   └── primary-paper-summary.md
│   └── validation.md
├── examples/
│   ├── cpp/
│   │   └── main.cpp
│   └── python/
│       ├── receiver_demo.py
│       └── reference_demo.py
├── python/
│   ├── prach_reference.py
│   └── receiver/
│       ├── __init__.py
│       ├── baseline.py
│       ├── dataset.py
│       ├── evaluate.py
│       └── model.py
├── references/
│   ├── primary/
│   │   └── PRACHPreambleDesignfor6GWirelessSystems_final.pdf
│   └── supporting/
│       ├── 2401.12803v1.pdf
│       └── 6G AI-Driven Air Interface.pdf
└── tests/
    ├── test_examples.py
    ├── test_markdown_links.py
    ├── test_prach_reference.py
    └── test_receiver.py
```

This lists tracked project files, not generated executables, Python bytecode,
or build/cache output. No package/build configuration is needed.

## Tracked-file guide

| File | Role | Purpose and what to edit |
| --- | --- | --- |
| `.gitignore` | Configuration | Ignores generated Python caches, build artifacts, test output, and local environments. Adjust only for new generated artifacts; never use it to hide source files. |
| `LICENSE` | License | Preserved GNU GPL v3 text for the repository's code. Each included paper/PDF remains subject to its own rights; do not assume this license relicenses the PDFs. |
| `README.md` | Entry point | Scope, prerequisites, exact example/test commands, limitations, and links to designer docs. Update if commands or project status change. |
| `DESIGN.md` | Compatibility overview | Root-level link/summary retained for existing references. The detailed design lives in `docs/architecture.md`. |
| `docs/README.md` | Reading guide | Recommends the designer reading order and identifies primary versus supporting research. |
| `docs/research/primary-paper-summary.md` | Primary-source summary and traceability | Page-grounded summary of the KPS paper, supporting-PDF roles, and PDF-page-to-code/test/status map. Update only after checking the cited PDF. |
| `docs/architecture.md` | Implemented baseline and design boundary | Documents actual API behavior, parameters, UE/gNB boundary, tests, and future extension points. Update alongside implementation changes. |
| `docs/repository-guide.md` | File inventory | This tree and purpose table cover every tracked file. Update whenever files are added, removed, or moved. |
| `docs/validation.md` | Reproducibility workflow | Exact test/build/run, paper extraction, checksum, link-check, and Python/C++ comparison conventions. Keep commands synchronized with code paths. |
| `references/primary/PRACHPreambleDesignfor6GWirelessSystems_final.pdf` | **Primary research source** | Six-page paper proposing KPS preambles and a two-stage detector. Ground paper claims and page references here; this is not a code artifact. |
| `references/supporting/2401.12803v1.pdf` | Supporting research source | 5G NR receiver AI/ML study on parallel RAPID and timing-advance estimation. It does not describe the implemented generator or the primary KPS proposal. |
| `references/supporting/6G AI-Driven Air Interface.pdf` | Supporting research source | Broad Hexa-X-II AI-driven 6G air-interface overview. Background only; not evidence for the project's specific PRACH sequence or signaling design. |
| `python/prach_reference.py` | Implemented Python baseline | `Preamble`, ZC root generation, cyclic shifting, and root/shift ID allocation. Edit this for Python behavior; keep tests and C++ semantics aligned. The module remains directly runnable. |
| `python/receiver/__init__.py` | Research package boundary | Marks the independent receiver prototype, not a standards-compliant PHY. |
| `python/receiver/dataset.py` | Synthetic research data | Seeded AWGN, bounded sample delays, normalized Doppler, user superposition, and per-user/collision labels. |
| `python/receiver/baseline.py` | Deterministic research receiver | Template correlation, sample-delay estimation, and residual collision heuristic; does not change sequence generation. |
| `python/receiver/evaluate.py` | Research metrics | Primary/top-k ID accuracy, conditional sample-delay MAE/RMSE, and collision precision/recall. |
| `python/receiver/model.py` | ML scaffolding only | Raw I/Q features and a prediction protocol; no trained model or inference implementation. |
| `cpp/prach_reference.hpp` | Implemented C++ interface | Public `prach::Preamble` structure and function declarations. Change with the `.cpp` implementation and example. |
| `cpp/prach_reference.cpp` | Implemented C++ baseline | C++ equivalent of Python input checks, ZC root generation, cyclic shifts, and allocation. Edit alongside Python when changing shared behavior. |
| `examples/python/reference_demo.py` | Runnable Python example | Calls the Python baseline with defaults and prints its count and first/last root-shift metadata. |
| `examples/python/receiver_demo.py` | Research example | Generates a small seeded dataset, runs the correlator, and prints parameters, metrics, and runtime. |
| `examples/cpp/main.cpp` | Runnable C++ example | Calls the C++ baseline with defaults and prints the same metadata. |
| `tests/test_prach_reference.py` | Baseline tests | Tests root amplitude/autocorrelation, shift direction, allocation ordering/default, and invalid inputs. Extend when baseline behavior changes. |
| `tests/test_receiver.py` | Receiver research tests | Checks synthetic signals/labels, reproducibility, correlation/delay/collision behavior, metric arithmetic, features, and the new example. |
| `tests/test_examples.py` | Example smoke test | Runs the Python module example from the repository root and checks its output. |
| `tests/test_markdown_links.py` | Documentation layout test | Checks local Markdown link targets so file moves do not leave broken paths. |

## Which files to edit

- **Change sequence math or allocation:** edit `python/prach_reference.py`
  and `cpp/prach_reference.cpp`; update the C++ declaration if necessary;
  add or update tests in `tests/test_prach_reference.py`; then update the
  [architecture](architecture.md) and [validation](validation.md) docs.
- **Change runnable output or commands:** update the example(s), root README,
  validation commands, and `tests/test_examples.py`.
- **Change receiver research:** edit `python/receiver/`, its demo, and
  `tests/test_receiver.py`; keep generator behavior and existing examples intact.
- **Add a paper-grounded method:** retain the PDF and page references, add a
  distinct implementation rather than silently changing the baseline, then
  update the traceability table, architecture, and file guide. Do not describe
  unimplemented or unevaluated methods as project results.
- **Move or add any tracked file:** update this tree/table and repair links.

Python and C++ are intended to have equivalent formulas, input bounds,
allocation order, IDs, roots, and shifts. See the documented tolerance and
comparison procedure in [validation notes](validation.md#python-and-c-equivalence).
