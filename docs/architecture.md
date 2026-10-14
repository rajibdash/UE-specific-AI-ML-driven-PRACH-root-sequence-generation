# Architecture and implementation

## Scope and implemented flow

The generator is a compact, deterministic reference baseline for sequence
construction and preamble indexing. Python and C++ remain separate,
standard-library-only implementations of the same operations:

```text
parameters ──> validate ──> generate ZC root ──> cyclically shift
                                               └─> assign preamble IDs
```

The flow stops at complex sequence samples plus root/shift metadata. It does
not model a complete UE transmission or gNB reception. In particular, a UE
does not run an AI model here, and the generator has no receiver or signaling path.
The independent [receiver research prototype](#receiver-research-prototype)
consumes these sequences without changing either generator.
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

## Receiver research prototype

`python/receiver/` is a standard-library-only, research/prototype path, not a
standards-compliant or production-ready gNB. It is motivated by RAPID and
timing estimation in the supporting
[`2401.12803v1.pdf`](../references/supporting/2401.12803v1.pdf), not by the
primary paper's KPS detector. It does not reproduce either paper's receiver.

```text
unchanged generator -> template bank -> seeded synthetic samples + labels
                                           |
                                           v
                       correlation receiver -> predictions -> metrics
                       future learned adapter -----------^
```

### Synthetic signal and labels

`dataset.generate_sample` takes a preamble bank and explicit `Transmission`
objects: ID (selecting a known root/shift), integer `delay`, `doppler` in
cycles/sample, positive `amplitude`, and `phase` in radians. The observation
contains `N + max_delay` samples. Each sequence is inserted at its delay,
zero outside its full length, and multiplied at local sample `n` by
`amplitude * exp(j * (phase + 2*pi*doppler*n))`. Users are linearly superposed.
Delay is **linear**, not the generator's circular shift.

Independent zero-mean Gaussian I/Q noise has total complex variance equal to
the sum of users' average sequence powers divided by `10**(snr_db/10)`.
This reference excludes padding and coherent cross-terms; SNR is not measured
from the final collision waveform. Positive infinite SNR disables noise.
There is no multipath, CP/guard, OFDM resource grid, sample-rate conversion,
antenna model, or physical Doppler/TA calibration.

`generate_dataset` draws uniformly selected IDs (with replacement), bounded
integer delays, and bounded uniform Doppler, with one or two equal-power
users according to `collision_probability`. Both APIs use a local seeded RNG.
Returned immutable samples retain transmission settings, SNR, per-user
ID/root/shift/sample-delay labels, and a collision flag. Two identical users
still count as a ground-truth collision. The primary label is the strongest
user by configured amplitude, breaking ties by input order, not receiver score.

### Deterministic receiver and evaluation

`baseline.CorrelationReceiver.predict` sees only samples. It searches every
template over delays `0..max_delay`, ranking each ID by its best
`abs(correlation) / sqrt(template_energy)`. Ties follow bank/delay order.
The selected peak's normalized correlation must meet `detection_threshold`;
silence or a rejected peak returns no ID or delay.

The receiver subtracts the fitted complex amplitude of that delayed template.
It flags a collision only if the strongest residual correlation exceeds
`collision_ratio` times the first strength and meets the same normalized
threshold. This is a two-user **heuristic**, not the KPS two-stage detector.
It does not compensate Doppler, calibrate false alarms, or resolve collisions.
Noise, Doppler, cross-correlation, near-far effects, and overlapping
shift/delay hypotheses can cause errors. Same-ID/same-delay users cannot be
distinguished from a single stronger user.

`evaluate.evaluate` reports primary-ID accuracy, top-k accuracy (rejected
detections count as misses), and delay MAE/RMSE **only for correct primary IDs
with timing predictions**, with `timing_count` exposing that denominator.
Equal-power collisions can therefore be detected correctly yet miss the
arbitrarily tie-broken primary label. Collision precision/recall use all
observations. Undefined metrics are `None` (`null` in the demo); delay is in
samples, not TA command units. The example reports wall-clock runtime, which
is machine-dependent even when sample data are reproducible.

### ML extension boundary

`model.iq_features` returns interleaved raw I/Q values. `ReceiverModel` is a
protocol for future adapters returning the same `Detection` contract as the
correlator. It is **scaffolding only**, with no training loop, learned weights,
or asserted gain. This preserves standard-library-only execution instead of
adding a framework solely for an unvalidated model. A future implementation
must independently seed/split training, validation, and held-out test data,
fit normalization on training data only, exclude labels from inference, and
compare both receivers on identical held-out observations. Channel/OTA
generalization remains untested.

## UE/gNB context and unimplemented interfaces

At a conceptual level, the returned metadata could be used by a future
configuration system to agree on a preamble/root/shift mapping:

```text
UE-side choice                    PRACH channel                 gNB-side work
ID -> (root, shift, samples)  --> transmission/resource map --> receive/detect/TA
     implemented as a set          not implemented             not implemented
```

The generator does not specify how a UE selects an ID, how the gNB assigns
or broadcasts a mapping, how UE identity is bound to a sequence, or how the
network resolves collisions. The research receiver's sample-delay estimate and
collision heuristic do not supply a network procedure. Do not infer SIB/RRC signaling, contention-based
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
- Separate receiver tests check seeded noise and labels, superposition, Doppler,
  noiseless/high-SNR identity and delay recovery, a resolvable collision, an
  indistinguishable collision, rejection, and hand-computed metrics.

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
3. **AI/ML research:** the separate receiver path now supplies a toy signal
   model, labeled synthetic dataset, correlator, metrics, and model interface.
   A trained receiver, realistic channels, held-out generalization studies, and
   UE/gNB coordination remain future work. Learned generation is not added.
   Diffusion or transformer models are not present and are not established by
   the primary paper.

Keep every added research choice explicitly labeled as a project proposal
unless it is directly verified in a cited source. A simulated gain is not an
implementation result, standards approval, or deployment claim.
