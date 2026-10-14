# Architecture and implementation

## Scope and implemented flow

The repository is a compact, deterministic reference baseline for sequence
construction and preamble indexing. Python and C++ are separate,
standard-library-only implementations of the same operations:

```text
parameters ──> validate ──> generate ZC root ──> cyclically shift
                                               └─> assign preamble IDs
```

The flow stops at complex sequence samples plus root/shift metadata. It does
not model a complete UE transmission or gNB reception. In particular, a UE
does not run an AI model here, and there is no receiver or signaling path.
The [primary-paper summary](research/primary-paper-summary.md) covers the
paper's different KPS sequence and detector proposals.

## Sequence construction

For odd sequence length $N>1$, root index $u$ must satisfy
$1 \le u < N$ and $\gcd(u,N)=1$. For samples $n=0,\ldots,N-1$, both
implementations evaluate

$$
x_u[n] = \exp\left(-j\pi u n(n+1)/N\right).
$$

The samples have unit magnitude. Given a non-empty sequence $x$, a requested
cyclic shift $C$ is restricted to $0\le C<N$, and output sample $n$ is

$$
x_C[n] = x[(n+C)\bmod N].
$$

The direction is intentional and is tested. It describes a circular shift of
the sequence samples, not a PRACH time/frequency resource mapping.

## Allocation algorithm and parameters

`generate_preambles(length, root_start, n_cs, count)` (Python) and its
same-named C++ counterpart do the following:

1. Validate odd `length > 1`, `1 <= root_start < length`, `1 <= n_cs <=
   length`, and positive `count`.
2. Walk the root indices from `root_start` through `length - 1`, wrapping back
   to 1. Keep only roots relatively prime to `length`.
3. Use `length // n_cs` shifts per root at `0, n_cs, 2*n_cs, ...`.
4. Assign IDs starting at 0, exhausting shifts for one root before moving to
   the next valid root.
5. Reject a requested count greater than the simple capacity
   `number_of_valid_roots * (length // n_cs)`.

`root_start` is a starting point in the traversal: if it is not itself
relatively prime to `length`, traversal skips it and continues. Each returned
entry contains `preamble_id`, `root_index`, `cyclic_shift`, and its complex
`sequence`.

Defaults are `length=839`, `root_start=1`, `n_cs=13`, and `count=64`. Here
`839 // 13 == 64`, so the default result uses root 1 with shifts from 0 to
819. This is an illustrative parameterization, not a universal standard
configuration or a claim of coverage for a PRACH format.

### Interface mapping

| Responsibility | Python | C++ |
| --- | --- | --- |
| Preamble data | `python/prach_reference.py::Preamble` | `cpp/prach_reference.hpp::prach::Preamble` |
| Generate ZC root | `zadoff_chu_root_sequence` | `prach::zadoff_chu_root_sequence` |
| Circular sample shift | `cyclically_shift` | `prach::cyclically_shift` |
| Root/shift allocation | `generate_preambles` | `prach::generate_preambles` |
| Runnable default example | `examples/python/reference_demo.py` | `examples/cpp/main.cpp` |

Invalid inputs raise `ValueError` in Python and `std::invalid_argument` in
C++. The C++ demonstration catches exceptions and prints an error to standard
error. Both implementations use double-precision real/complex arithmetic;
minor floating-point differences between standard math libraries are
expected.

## UE/gNB context and unimplemented interfaces

At a conceptual level, the returned metadata could be used by a future
configuration system to agree on a preamble/root/shift mapping:

```text
UE-side choice                    PRACH channel                 gNB-side work
ID -> (root, shift, samples)  --> transmission/resource map --> receive/detect/TA
     implemented as a set          not implemented             not implemented
```

The repository does not specify how a UE selects an ID, how the gNB assigns
or broadcasts a mapping, how UE identity is bound to a sequence, or how the
network detects collisions. Do not infer SIB/RRC signaling, contention-based
or contention-free procedure handling, timing advance, beam/handover
behavior, or RAPID decoding from the current sequence API.

## Validation represented by current tests

- Root samples have constant amplitude and the tested small root has zero
  nonzero cyclic autocorrelation.
- Circular shift direction matches $x[(n+C)\bmod N]$.
- IDs fill shifts before advancing to the next valid root.
- The default allocation returns 64 length-839 preambles.
- Invalid root indices and over-capacity requests are rejected.
- The Python example runs and local Markdown links resolve.

These checks protect the educational baseline. They do not prove performance
under a radio channel or standards conformance.

## Extension points

1. **Standards-oriented baseline:** add explicit PRACH format, restricted-set,
   guard/CP and resource-grid rules, sourced and tested against the applicable
   normative specifications.
2. **Paper reproduction:** implement KPS sequence construction and the
   paper's two-stage detector as separate, testable components; first reproduce
   stated assumptions and baselines, then evaluate channel and complexity
   sensitivity. The primary paper is an independent proposal, not a completed
   extension.
3. **AI/ML research:** only after defining a signal model, objective, dataset,
   receiver, UE/gNB coordination, comparison baselines, and reproducible
   evaluation should learned generation/detection be considered. Diffusion or
   transformer models are not present and are not established by the primary
   paper.

Keep every added research choice explicitly labeled as a project proposal
unless it is directly verified in a cited source. A simulated gain is not an
implementation result, standards approval, or deployment claim.
