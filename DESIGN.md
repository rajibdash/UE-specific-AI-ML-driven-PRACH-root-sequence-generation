# Design documentation (compatibility entry point)

The current implementation and research scope are documented in
[docs/architecture.md](docs/architecture.md). For the recommended designer
reading order, begin with [docs/README.md](docs/README.md).

The Python and C++ generators implement a deterministic Zadoff–Chu
root/cyclic-shift baseline only. A separate `python/receiver/` research prototype
adds synthetic data and correlation detection without changing those generators;
its ML path is scaffolding only. The primary paper's Kronecker-product
structured (KPS) sequence family and two-stage detector are research proposals
described in [the paper summary](docs/research/primary-paper-summary.md); they
are not implemented by this repository.
