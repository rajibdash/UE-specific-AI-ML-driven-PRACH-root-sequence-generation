"""Seeded, sample-domain receiver experiments, not a PRACH waveform simulator."""

import cmath
from dataclasses import dataclass
import math
import random
from typing import Sequence, Tuple

from python.prach_reference import Preamble


@dataclass(frozen=True)
class Transmission:
    """One user: Doppler is cycles/sample, delay is an integer sample offset."""

    preamble_id: int
    delay: int = 0
    doppler: float = 0.0
    amplitude: float = 1.0
    phase: float = 0.0


@dataclass(frozen=True)
class UserLabel:
    preamble_id: int
    root_index: int
    cyclic_shift: int
    timing_offset: int
    amplitude: float


@dataclass(frozen=True)
class Sample:
    samples: Tuple[complex, ...]
    labels: Tuple[UserLabel, ...]
    transmissions: Tuple[Transmission, ...]
    snr_db: float

    @property
    def primary(self) -> UserLabel:
        """Strongest transmitted user; input order breaks amplitude ties."""
        return max(self.labels, key=lambda label: label.amplitude)

    @property
    def collision(self) -> bool:
        """Ground truth includes indistinguishable same-preamble collisions."""
        return len(self.labels) > 1


def validate_preambles(preambles: Sequence[Preamble]) -> Tuple[Preamble, ...]:
    """Snapshot a nonempty bank with unique IDs and equal, finite sequences."""
    bank = tuple(preambles)
    if not bank or not bank[0].sequence:
        raise ValueError("preamble bank must not be empty")
    length = len(bank[0].sequence)
    if len({p.preamble_id for p in bank}) != len(bank):
        raise ValueError("preamble IDs must be unique")
    for preamble in bank:
        if len(preamble.sequence) != length:
            raise ValueError("preamble sequences must have equal lengths")
        if not all(math.isfinite(x.real) and math.isfinite(x.imag)
                   for x in preamble.sequence):
            raise ValueError("preamble samples must be finite")
        energy = sum(abs(x) ** 2 for x in preamble.sequence)
        if not math.isfinite(energy) or energy <= 0:
            raise ValueError("preamble energy must be finite and positive")
    return bank


def _validate_parameters(max_delay: int, snr_db: float) -> None:
    if not isinstance(max_delay, int) or max_delay < 0:
        raise ValueError("max_delay must be a nonnegative integer")
    if not math.isfinite(snr_db) and snr_db != math.inf:
        raise ValueError("snr_db must be finite or positive infinity (no noise)")


def _synthesize(bank, users, snr_db, max_delay, rng):
    by_id = {p.preamble_id: p for p in bank}
    users = tuple(users)
    if not users:
        raise ValueError("at least one transmission is required")
    length = len(bank[0].sequence)
    received = [0j] * (length + max_delay)
    labels = []
    reference_power = 0.0
    for user in users:
        if user.preamble_id not in by_id:
            raise ValueError("unknown preamble ID")
        if not isinstance(user.delay, int) or not 0 <= user.delay <= max_delay:
            raise ValueError("delay must be an integer within the observation bound")
        if not math.isfinite(user.doppler) or not -0.5 <= user.doppler <= 0.5:
            raise ValueError("doppler must be finite and within [-0.5, 0.5]")
        if not math.isfinite(user.amplitude) or user.amplitude <= 0:
            raise ValueError("amplitude must be finite and positive")
        if not math.isfinite(user.phase):
            raise ValueError("phase must be finite")
        preamble = by_id[user.preamble_id]
        for n, value in enumerate(preamble.sequence):
            received[n + user.delay] += user.amplitude * value * cmath.exp(
                1j * (user.phase + 2 * math.pi * user.doppler * n)
            )
        reference_power += user.amplitude ** 2 * sum(
            abs(x) ** 2 for x in preamble.sequence
        ) / length
        labels.append(UserLabel(
            preamble.preamble_id, preamble.root_index, preamble.cyclic_shift,
            user.delay, user.amplitude,
        ))
    try:
        noise_power = (0.0 if snr_db == math.inf else
                       reference_power * 10.0 ** (-snr_db / 10.0))
    except OverflowError as error:
        raise ValueError("signal/noise power exceeds numeric range") from error
    if not math.isfinite(reference_power) or not math.isfinite(noise_power):
        raise ValueError("signal/noise power must be finite")
    sigma = math.sqrt(noise_power / 2)
    samples = tuple(x + complex(rng.gauss(0, sigma), rng.gauss(0, sigma))
                    for x in received)
    return Sample(samples, tuple(labels), users, snr_db)


def generate_sample(
    preambles: Sequence[Preamble],
    transmissions: Sequence[Transmission],
    *,
    snr_db: float = 20.0,
    max_delay: int = 3,
    seed: int = 0,
) -> Sample:
    """Superpose full delayed sequences with AWGN relative to summed user power.

    No CP, resource grid, multipath, or physical timing-advance units are modeled.
    Positive infinite SNR explicitly disables noise.
    """
    bank = validate_preambles(preambles)
    _validate_parameters(max_delay, snr_db)
    return _synthesize(bank, transmissions, snr_db, max_delay, random.Random(seed))


def generate_dataset(
    preambles: Sequence[Preamble],
    count: int,
    *,
    seed: int = 0,
    snr_db: float = 20.0,
    max_delay: int = 3,
    max_doppler: float = 0.0,
    collision_probability: float = 0.0,
) -> Tuple[Sample, ...]:
    """Draw one or two equal-power users, including same-ID collisions.

    Delays are uniform on [0, max_delay]; Doppler is uniform on
    [-max_doppler, max_doppler]. A local RNG leaves global random state alone.
    """
    bank = validate_preambles(preambles)
    _validate_parameters(max_delay, snr_db)
    if not isinstance(count, int) or count < 1:
        raise ValueError("count must be a positive integer")
    if not math.isfinite(max_doppler) or not 0 <= max_doppler <= 0.5:
        raise ValueError("max_doppler must be within [0, 0.5]")
    if not math.isfinite(collision_probability) or not 0 <= collision_probability <= 1:
        raise ValueError("collision_probability must be within [0, 1]")
    rng = random.Random(seed)
    result = []
    for _ in range(count):
        user_count = 2 if rng.random() < collision_probability else 1
        users = tuple(Transmission(
            rng.choice(bank).preamble_id,
            rng.randint(0, max_delay),
            rng.uniform(-max_doppler, max_doppler),
        ) for _ in range(user_count))
        result.append(_synthesize(bank, users, snr_db, max_delay, rng))
    return tuple(result)
