"""Deterministic matched-filter receiver for the toy sample-domain signal model."""

from dataclasses import dataclass
import math
from typing import Optional, Sequence, Tuple

from python.prach_reference import Preamble
from python.receiver.dataset import validate_preambles


@dataclass(frozen=True)
class Detection:
    preamble_id: Optional[int]
    timing_offset: Optional[int]
    collision: bool
    score: float
    ranked_ids: Tuple[int, ...]


class CorrelationReceiver:
    """Exhaustive delay search plus one residual collision test.

    Timing is in samples, not a 3GPP TA command. Thresholds are uncalibrated
    research knobs. Same-ID/same-delay users cannot be separated.
    """

    def __init__(
        self, preambles: Sequence[Preamble], max_delay: int = 3,
        detection_threshold: float = 0.5, collision_ratio: float = 0.5,
    ):
        self.preambles = validate_preambles(preambles)
        if not isinstance(max_delay, int) or max_delay < 0:
            raise ValueError("max_delay must be a nonnegative integer")
        for value in (detection_threshold, collision_ratio):
            if not math.isfinite(value) or not 0 < value <= 1:
                raise ValueError("thresholds must be within (0, 1]")
        self.max_delay = max_delay
        self.detection_threshold = detection_threshold
        self.collision_ratio = collision_ratio
        self.length = len(self.preambles[0].sequence)

    def _search(self, samples):
        candidates = []
        for preamble in self.preambles:
            energy = sum(abs(x) ** 2 for x in preamble.sequence)
            best = None
            for delay in range(self.max_delay + 1):
                window = samples[delay:delay + self.length]
                correlation = sum(x.conjugate() * y
                                  for x, y in zip(preamble.sequence, window))
                power = sum(abs(y) ** 2 for y in window)
                score = abs(correlation) / math.sqrt(energy * power) if power else 0.0
                candidate = (abs(correlation) / math.sqrt(energy),
                             preamble, delay, correlation / energy, min(score, 1.0))
                if best is None or candidate[0] > best[0]:
                    best = candidate
            candidates.append(best)
        return sorted(candidates, key=lambda candidate: candidate[0], reverse=True)

    def predict(self, samples: Sequence[complex]) -> Detection:
        """Use samples only; never consume ground-truth labels or impairments."""
        samples = tuple(samples)
        if len(samples) != self.length + self.max_delay:
            raise ValueError("observation length must equal sequence length + max_delay")
        if not all(math.isfinite(x.real) and math.isfinite(x.imag) for x in samples):
            raise ValueError("observation samples must be finite")
        candidates = self._search(samples)
        strength, preamble, delay, amplitude, score = candidates[0]
        ranked = tuple(candidate[1].preamble_id for candidate in candidates)
        if strength == 0 or score < self.detection_threshold:
            return Detection(None, None, False, score, ranked)
        residual = list(samples)
        for n, value in enumerate(preamble.sequence):
            residual[n + delay] -= amplitude * value
        second_strength, _, _, _, second_score = self._search(residual)[0]
        collision = (second_strength >= strength * self.collision_ratio
                     and second_score >= self.detection_threshold)
        return Detection(preamble.preamble_id, delay, collision, score, ranked)
