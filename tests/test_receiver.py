import cmath
from dataclasses import replace
import json
import math
import random
import subprocess
import sys
import unittest

from python.prach_reference import generate_preambles
from python.receiver.baseline import CorrelationReceiver, Detection
from python.receiver.dataset import Transmission, generate_dataset, generate_sample
from python.receiver.evaluate import evaluate
from python.receiver.model import iq_features


class DatasetTests(unittest.TestCase):
    def setUp(self):
        self.bank = generate_preambles(length=31, n_cs=8, count=6)

    def test_noiseless_delay_and_identity_labels(self):
        user = Transmission(4, delay=3)
        sample = generate_sample(self.bank, [user], snr_db=math.inf)
        self.assertEqual(sample.samples, (0j,) * 3 + self.bank[4].sequence)
        self.assertEqual(sample.primary.preamble_id, 4)
        self.assertEqual(sample.primary.root_index, self.bank[4].root_index)
        self.assertEqual(sample.primary.cyclic_shift, self.bank[4].cyclic_shift)
        self.assertEqual(sample.primary.timing_offset, 3)
        self.assertFalse(sample.collision)
        self.assertEqual(sample.transmissions, (user,))

    def test_doppler_phase_and_amplitude(self):
        user = Transmission(0, delay=1, doppler=0.02, amplitude=0.75, phase=0.4)
        sample = generate_sample(self.bank, [user], snr_db=math.inf)
        for n, value in enumerate(self.bank[0].sequence):
            expected = 0.75 * value * cmath.exp(1j * (0.4 + 2 * math.pi * 0.02 * n))
            self.assertAlmostEqual(abs(sample.samples[n + 1] - expected), 0.0)
        self.assertEqual(sample.samples[0], 0j)
        self.assertEqual(sample.samples[-2:], (0j, 0j))

    def test_collision_is_linear_superposition_and_strongest_label(self):
        users = [Transmission(0, delay=1), Transmission(4, delay=3, amplitude=2)]
        combined = generate_sample(self.bank, users, snr_db=math.inf)
        separate = [generate_sample(self.bank, [user], snr_db=math.inf) for user in users]
        self.assertEqual(combined.samples, tuple(
            a + b for a, b in zip(separate[0].samples, separate[1].samples)
        ))
        self.assertTrue(combined.collision)
        self.assertEqual(combined.primary.preamble_id, 4)
        self.assertEqual(len(combined.labels), 2)

    def test_seed_reproducibility_and_global_rng_isolation(self):
        state = random.getstate()
        kwargs = dict(count=10, seed=42, max_doppler=0.01, collision_probability=0.5)
        first = generate_dataset(self.bank, **kwargs)
        self.assertEqual(random.getstate(), state)
        self.assertEqual(first, generate_dataset(self.bank, **kwargs))
        self.assertNotEqual(first, generate_dataset(self.bank, **{**kwargs, "seed": 43}))
        self.assertTrue(all(len(sample.samples) == 34 for sample in first))

    def test_collision_flags_include_identical_users(self):
        sample = generate_sample(self.bank, [Transmission(0), Transmission(0)],
                                 snr_db=math.inf)
        self.assertTrue(sample.collision)
        self.assertEqual(sample.samples[:31], tuple(2 * x for x in self.bank[0].sequence))
        for probability in (0.0, 1.0):
            data = generate_dataset(self.bank, 5, collision_probability=probability)
            self.assertTrue(all(s.collision == bool(probability) for s in data))

    def test_awgn_power_tracks_configured_snr(self):
        clean = generate_sample(self.bank, [Transmission(0)], snr_db=math.inf)
        noisy = [generate_sample(self.bank, [Transmission(0)], snr_db=10, seed=seed)
                 for seed in range(100)]
        noise_power = sum(abs(a - b) ** 2 for s in noisy
                          for a, b in zip(s.samples, clean.samples)) / (100 * 34)
        self.assertAlmostEqual(noise_power, 0.1, delta=0.01)
        low = generate_sample(self.bank, [Transmission(0)], snr_db=-5, seed=7)
        high = generate_sample(self.bank, [Transmission(0)], snr_db=20, seed=7)
        self.assertGreater(sum(abs(a - b) ** 2 for a, b in zip(low.samples, clean.samples)),
                           sum(abs(a - b) ** 2 for a, b in zip(high.samples, clean.samples)))

    def test_invalid_transmissions_and_parameters(self):
        for user in (Transmission(99), Transmission(0, delay=-1),
                     Transmission(0, delay=4), Transmission(0, delay=0.5),
                     Transmission(0, doppler=math.nan), Transmission(0, doppler=0.6),
                     Transmission(0, amplitude=0), Transmission(0, amplitude=math.inf),
                     Transmission(0, phase=math.inf)):
            with self.subTest(user=user), self.assertRaises(ValueError):
                generate_sample(self.bank, [user])
        for kwargs in ({"max_delay": -1}, {"max_delay": 1.5}, {"snr_db": math.nan},
                       {"snr_db": -math.inf}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                generate_sample(self.bank, [Transmission(0)], **kwargs)
        with self.assertRaises(ValueError):
            generate_sample(self.bank, [])
        for kwargs in ({"count": 0}, {"count": 1.5}, {"collision_probability": -0.1},
                       {"collision_probability": math.nan}, {"max_doppler": -1},
                       {"max_doppler": math.inf}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                generate_dataset(self.bank, **{"count": 2, **kwargs})

    def test_invalid_template_banks(self):
        invalid = [
            [], [self.bank[0], self.bank[0]],
            [self.bank[0], replace(self.bank[1], sequence=(1j,))],
            [replace(self.bank[0], sequence=())],
            [replace(self.bank[0], sequence=(0j,) * 31)],
            [replace(self.bank[0], sequence=(complex(math.nan, 0),) * 31)],
        ]
        for bank in invalid:
            with self.subTest(bank=bank), self.assertRaises(ValueError):
                generate_sample(bank, [Transmission(0)])
            with self.assertRaises(ValueError):
                CorrelationReceiver(bank)


class ReceiverTests(unittest.TestCase):
    def setUp(self):
        self.bank = generate_preambles(length=31, n_cs=8, count=6)
        self.receiver = CorrelationReceiver(self.bank)

    def test_all_identities_and_delays_without_noise(self):
        for preamble in self.bank:
            for delay in range(4):
                with self.subTest(preamble=preamble.preamble_id, delay=delay):
                    sample = generate_sample(self.bank, [Transmission(
                        preamble.preamble_id, delay, amplitude=0.7, phase=0.8,
                    )], snr_db=math.inf)
                    detection = self.receiver.predict(sample.samples)
                    self.assertEqual(detection.preamble_id, preamble.preamble_id)
                    self.assertEqual(detection.timing_offset, delay)
                    self.assertFalse(detection.collision)
                    self.assertAlmostEqual(detection.score, 1.0)
                    self.assertEqual(detection.ranked_ids[0], preamble.preamble_id)
                    self.assertEqual(set(detection.ranked_ids), set(range(6)))

    def test_seeded_high_snr_detection(self):
        dataset = generate_dataset(self.bank, 40, seed=123, snr_db=30)
        predictions = [self.receiver.predict(sample.samples) for sample in dataset]
        metrics = evaluate(dataset, predictions)
        self.assertEqual(metrics.rapid_accuracy, 1.0)
        self.assertEqual(metrics.timing_mae, 0.0)
        self.assertFalse(any(p.collision for p in predictions))

    def test_resolvable_collision(self):
        sample = generate_sample(self.bank, [Transmission(0), Transmission(1, amplitude=0.75)],
                                 max_delay=0, snr_db=math.inf)
        detection = CorrelationReceiver(self.bank, max_delay=0).predict(sample.samples)
        self.assertEqual(detection.preamble_id, 0)
        self.assertEqual(detection.timing_offset, 0)
        self.assertTrue(detection.collision)

    def test_identical_collision_is_not_identifiable(self):
        sample = generate_sample(self.bank, [Transmission(0, delay=2)] * 2,
                                 snr_db=math.inf)
        detection = self.receiver.predict(sample.samples)
        self.assertTrue(sample.collision)
        self.assertFalse(detection.collision)

    def test_silence_and_threshold_rejection(self):
        detection = self.receiver.predict((0j,) * 34)
        self.assertIsNone(detection.preamble_id)
        self.assertIsNone(detection.timing_offset)
        self.assertEqual(detection.score, 0.0)
        self.assertFalse(detection.collision)
        sample = generate_sample(self.bank, [Transmission(0)], snr_db=-10)
        strict = CorrelationReceiver(self.bank, detection_threshold=1.0)
        self.assertIsNone(strict.predict(sample.samples).preamble_id)

    def test_invalid_observation_and_thresholds(self):
        for values in ((), (0j,) * 33, (complex(math.inf, 0),) * 34):
            with self.assertRaises(ValueError):
                self.receiver.predict(values)
        for kwargs in ({"max_delay": -1}, {"max_delay": 0.5},
                       {"detection_threshold": 0}, {"collision_ratio": 1.1},
                       {"collision_ratio": math.nan}):
            with self.assertRaises(ValueError):
                CorrelationReceiver(self.bank, **kwargs)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        bank = generate_preambles(length=31, n_cs=8, count=3)
        self.single = generate_sample(bank, [Transmission(0, delay=2)], snr_db=math.inf)
        self.collision = generate_sample(bank, [Transmission(0, delay=2), Transmission(1)],
                                         snr_db=math.inf)

    def test_hand_computed_metrics_and_conditional_timing(self):
        predictions = [
            Detection(0, 3, True, 1, (0, 1, 2)),
            Detection(0, 0, True, 1, (0, 1, 2)),
            Detection(1, 0, False, 1, (1, 0, 2)),
        ]
        metrics = evaluate([self.single, self.collision, self.collision], predictions, top_k=2)
        self.assertEqual(metrics.count, 3)
        self.assertAlmostEqual(metrics.rapid_accuracy, 2 / 3)
        self.assertEqual(metrics.top_k_accuracy, 1.0)
        self.assertEqual(metrics.timing_count, 2)
        self.assertEqual(metrics.timing_mae, 1.5)
        self.assertAlmostEqual(metrics.timing_rmse, math.sqrt(2.5))
        self.assertEqual(metrics.collision_precision, 0.5)
        self.assertEqual(metrics.collision_recall, 0.5)

    def test_undefined_metrics_and_rejection(self):
        rejected = Detection(None, None, False, 0, (0, 1, 2))
        metrics = evaluate([self.single], [rejected])
        self.assertEqual(metrics.rapid_accuracy, 0)
        self.assertEqual(metrics.top_k_accuracy, 0)
        self.assertEqual(metrics.timing_count, 0)
        self.assertIsNone(metrics.timing_mae)
        self.assertIsNone(metrics.timing_rmse)
        self.assertIsNone(metrics.collision_precision)
        self.assertIsNone(metrics.collision_recall)
        for data, predictions, k in (([], [], 1), ([self.single], [], 1),
                                     ([self.single], [rejected], 0)):
            with self.assertRaises(ValueError):
                evaluate(data, predictions, top_k=k)

    def test_iq_features_have_no_labels(self):
        self.assertEqual(iq_features((1 + 2j, -3 - 4j)), (1, 2, -3, -4))
        self.assertEqual(iq_features(()), ())

    def test_receiver_example_runs(self):
        result = subprocess.run(
            [sys.executable, "-m", "examples.python.receiver_demo", "--count", "4",
             "--seed", "7", "--snr-db", "30"],
            check=True, capture_output=True, text=True,
        )
        banner, payload = result.stdout.split("\n", 1)
        self.assertIn("RESEARCH ONLY", banner)
        report = json.loads(payload)
        self.assertEqual(report["bank"], dict(length=31, root_start=1, n_cs=8, count=6))
        self.assertEqual(report["receiver"]["detection_threshold"], 0.5)
        self.assertEqual(report["receiver"]["collision_ratio"], 0.5)
        self.assertEqual(report["metrics"]["count"], 4)
        self.assertEqual(report["metrics"]["rapid_accuracy"], 1.0)
        self.assertEqual(report["metrics"]["timing_mae"], 0.0)
        self.assertGreaterEqual(report["seconds_per_sample"], 0)


if __name__ == "__main__":
    unittest.main()
