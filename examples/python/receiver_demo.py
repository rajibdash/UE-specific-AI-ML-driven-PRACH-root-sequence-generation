"""Run a seeded receiver research experiment, not a paper reproduction."""

import argparse
from dataclasses import asdict
import json
import time

from python.prach_reference import generate_preambles
from python.receiver.baseline import CorrelationReceiver
from python.receiver.dataset import generate_dataset
from python.receiver.evaluate import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--count", type=int, default=20)
    parser.add_argument("--snr-db", type=float, default=20.0)
    parser.add_argument("--max-delay", type=int, default=3)
    parser.add_argument("--max-doppler", type=float, default=0.0)
    parser.add_argument("--collision-probability", type=float, default=0.0)
    args = parser.parse_args()
    preambles = generate_preambles(length=31, n_cs=8, count=6)
    dataset = generate_dataset(preambles, **vars(args))
    receiver = CorrelationReceiver(preambles, max_delay=args.max_delay)
    start = time.perf_counter()
    predictions = tuple(receiver.predict(sample.samples) for sample in dataset)
    elapsed = time.perf_counter() - start
    print("RESEARCH ONLY: synthetic samples; no trained ML or standards compliance")
    print(json.dumps({
        "parameters": vars(args),
        "metrics": asdict(evaluate(dataset, predictions)),
        "seconds_per_sample": elapsed / len(dataset),
    }, indent=2))


if __name__ == "__main__":
    main()
