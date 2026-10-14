"""ML extension points only: no trained model, training loop, or claimed gain."""

from typing import Protocol, Sequence, Tuple

from python.receiver.baseline import Detection


def iq_features(samples: Sequence[complex]) -> Tuple[float, ...]:
    """Interleaved raw I/Q features; fit any normalization on training data only."""
    return tuple(component for value in samples for component in (value.real, value.imag))


class ReceiverModel(Protocol):
    """A future learned adapter can share the baseline's evaluation contract.

    Implement predict using samples alone, returning ranked preamble IDs,
    a sample-domain delay, and a collision flag. Split independently seeded
    training/validation/test data before fitting; keep labels out of features.
    """

    def predict(self, samples: Sequence[complex]) -> Detection:
        ...
