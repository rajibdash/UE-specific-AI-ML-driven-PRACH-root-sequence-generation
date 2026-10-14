"""Educational PRACH Zadoff-Chu root and cyclic-shift reference implementation."""

from dataclasses import dataclass
import cmath
import math
from typing import List, Tuple


@dataclass(frozen=True)
class Preamble:
    """One preamble and the root/shift parameters used to construct it."""

    preamble_id: int
    root_index: int
    cyclic_shift: int
    sequence: Tuple[complex, ...]


def zadoff_chu_root_sequence(length: int, root_index: int) -> Tuple[complex, ...]:
    """Generate an odd-length Zadoff-Chu root sequence.

    For odd ``length``, x[u][n] = exp(-j*pi*u*n*(n+1)/length).
    The root index must be relatively prime to the sequence length.
    """
    if length <= 1 or length % 2 == 0:
        raise ValueError("length must be an odd integer greater than one")
    if not 1 <= root_index < length:
        raise ValueError("root_index must be between 1 and length - 1")
    if math.gcd(root_index, length) != 1:
        raise ValueError("root_index must be relatively prime to length")

    return tuple(
        cmath.exp(-1j * math.pi * root_index * sample * (sample + 1) / length)
        for sample in range(length)
    )


def cyclically_shift(sequence: Tuple[complex, ...], shift: int) -> Tuple[complex, ...]:
    """Return the sequence x[(n + shift) mod N] for each output sample n."""
    if not sequence:
        raise ValueError("sequence must not be empty")
    if not 0 <= shift < len(sequence):
        raise ValueError("shift must be between zero and sequence length - 1")

    return tuple(sequence[(sample + shift) % len(sequence)] for sample in range(len(sequence)))


def generate_preambles(
    length: int = 839,
    root_start: int = 1,
    n_cs: int = 13,
    count: int = 64,
) -> List[Preamble]:
    """Allocate preamble IDs across valid roots and their cyclic shifts.

    This basic model uses ``floor(length / n_cs)`` shifts per root, beginning
    at zero. It does not implement format-specific restricted-set rules.
    """
    if length <= 1 or length % 2 == 0:
        raise ValueError("length must be an odd integer greater than one")
    if not 1 <= root_start < length:
        raise ValueError("root_start must be between 1 and length - 1")
    if not 1 <= n_cs <= length:
        raise ValueError("n_cs must be between 1 and length")
    if count < 1:
        raise ValueError("count must be positive")

    shifts_per_root = length // n_cs
    valid_roots = [
        ((root_start - 1 + offset) % (length - 1)) + 1
        for offset in range(length - 1)
    ]
    valid_roots = [root for root in valid_roots if math.gcd(root, length) == 1]
    if count > len(valid_roots) * shifts_per_root:
        raise ValueError("requested preambles exceed the available roots and shifts")

    preambles = []
    preamble_id = 0
    for root_index in valid_roots:
        root = zadoff_chu_root_sequence(length, root_index)
        for shift_index in range(shifts_per_root):
            cyclic_shift = shift_index * n_cs
            preambles.append(
                Preamble(
                    preamble_id=preamble_id,
                    root_index=root_index,
                    cyclic_shift=cyclic_shift,
                    sequence=cyclically_shift(root, cyclic_shift),
                )
            )
            preamble_id += 1
            if preamble_id == count:
                return preambles

    return preambles


if __name__ == "__main__":
    preambles = generate_preambles()
    print(f"Generated {len(preambles)} preambles")
    print(f"First preamble: root={preambles[0].root_index}, shift={preambles[0].cyclic_shift}")
    print(
        f"Last preamble: root={preambles[-1].root_index}, "
        f"shift={preambles[-1].cyclic_shift}"
    )
