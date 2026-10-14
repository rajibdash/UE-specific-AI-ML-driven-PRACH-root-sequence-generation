import math
import unittest

from python.prach_reference import (
    cyclically_shift,
    generate_preambles,
    zadoff_chu_root_sequence,
)


class ZadoffChuTests(unittest.TestCase):
    def test_root_sequence_has_constant_amplitude_and_zero_cyclic_autocorrelation(self):
        sequence = zadoff_chu_root_sequence(5, 1)
        self.assertTrue(all(math.isclose(abs(sample), 1.0) for sample in sequence))

        for shift in range(1, len(sequence)):
            correlation = sum(
                sequence[index].conjugate()
                * sequence[(index + shift) % len(sequence)]
                for index in range(len(sequence))
            )
            self.assertAlmostEqual(abs(correlation), 0.0, places=10)

    def test_cyclic_shift_uses_documented_direction(self):
        self.assertEqual(cyclically_shift((1, 2, 3, 4), 1), (2, 3, 4, 1))

    def test_preamble_ids_fill_shifts_then_advance_to_next_root(self):
        preambles = generate_preambles(length=7, root_start=1, n_cs=3, count=4)
        self.assertEqual(
            [(item.preamble_id, item.root_index, item.cyclic_shift) for item in preambles],
            [(0, 1, 0), (1, 1, 3), (2, 2, 0), (3, 2, 3)],
        )

    def test_default_configuration_creates_64_long_format_preambles(self):
        preambles = generate_preambles()
        self.assertEqual(len(preambles), 64)
        self.assertEqual([item.preamble_id for item in preambles], list(range(64)))
        self.assertEqual(len({item.cyclic_shift for item in preambles}), 64)
        self.assertTrue(all(len(item.sequence) == 839 for item in preambles))

    def test_rejects_invalid_root_and_unavailable_preamble_count(self):
        with self.assertRaises(ValueError):
            zadoff_chu_root_sequence(7, 0)
        with self.assertRaises(ValueError):
            zadoff_chu_root_sequence(7, 7)
        with self.assertRaises(ValueError):
            generate_preambles(length=5, n_cs=5, count=5)


if __name__ == "__main__":
    unittest.main()
