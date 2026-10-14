# Designer reading guide

This guide separates what is in the supplied research papers from what the
repository actually implements. Read in this order:

1. [Root README](../README.md) — scope, prerequisites, run commands, and tests.
2. [Primary-paper summary](research/primary-paper-summary.md) — a page-grounded
   account of the six-page KPS paper, its figures/results, and traceability to
   current code.
3. [Architecture and implementation](architecture.md) — sequence API,
   parameter meanings, allocation behavior, UE/gNB boundary, and extension
   points.
4. [Repository/file guide](repository-guide.md) — tree, role, and purpose of
   every tracked file.
5. [Validation workflow](validation.md) — repeatable tests, PDF checksum
   verification, and Python/C++ comparison conventions.

The short root [DESIGN.md](../DESIGN.md) remains as a compatibility link to the
current detailed design.

## Research sources

- **Primary source:** Fan Zhang et al., “PRACH Preamble Design for 6G Wireless
  Systems,” six pages. The actual tracked PDF is at
  [`references/primary/PRACHPreambleDesignfor6GWirelessSystems_final.pdf`](../references/primary/PRACHPreambleDesignfor6GWirelessSystems_final.pdf).
  Its six pages were extracted and reviewed with Poppler's `pdftotext -layout`.
- **Supporting source:** Rohit Singh et al., “Enhancements for 5G NR PRACH
  Reception: An AI/ML Approach” (arXiv:2401.12803v1), a receiver-focused
  study—not the primary waveform-design paper. It motivates the separate
  [receiver research prototype](architecture.md#receiver-research-prototype),
  which adds synthetic data and a correlator, not the paper's neural networks.
- **Supporting source:** Hamed Farhadi et al., “6G AI-Driven Air Interface —
  Hexa-X-II View,” a broad 6G PHY overview—not a PRACH sequence design.

The two supporting PDFs are kept separate from the primary paper under
[`references/supporting/`](../references/supporting/). Their role and scope
are also listed in the [file guide](repository-guide.md#tracked-file-guide).
The detailed summary links the primary PDF at the supplied source commit, so
the source citation remains pinned even though the repository copy has moved.
