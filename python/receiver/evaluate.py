"""Comparable toy receiver metrics; these are not paper-performance results."""

from dataclasses import dataclass
import math
from typing import Optional, Sequence

from python.receiver.baseline import Detection
from python.receiver.dataset import Sample


@dataclass(frozen=True)
class Metrics:
    count: int
    rapid_accuracy: float
    top_k_accuracy: float
    timing_count: int
    timing_mae: Optional[float]
    timing_rmse: Optional[float]
    collision_precision: Optional[float]
    collision_recall: Optional[float]


def evaluate(
    dataset: Sequence[Sample], predictions: Sequence[Detection], top_k: int = 3,
) -> Metrics:
    """Score the strongest-user label (input order breaks equal-power ties).

    Delay error is conditional on correct primary identity and available timing.
    Undefined timing/precision/recall values are None, not fabricated zeros.
    """
    if not dataset or len(dataset) != len(predictions):
        raise ValueError("nonempty dataset and equally sized predictions are required")
    if not isinstance(top_k, int) or top_k < 1:
        raise ValueError("top_k must be a positive integer")
    correct = top_correct = true_positive = false_positive = false_negative = 0
    errors = []
    for sample, prediction in zip(dataset, predictions):
        primary = sample.primary
        matched = prediction.preamble_id == primary.preamble_id
        correct += matched
        top_correct += (prediction.preamble_id is not None
                        and primary.preamble_id in prediction.ranked_ids[:top_k])
        if matched and prediction.timing_offset is not None:
            errors.append(prediction.timing_offset - primary.timing_offset)
        true_positive += sample.collision and prediction.collision
        false_positive += not sample.collision and prediction.collision
        false_negative += sample.collision and not prediction.collision
    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    return Metrics(
        len(dataset), correct / len(dataset), top_correct / len(dataset), len(errors),
        sum(abs(error) for error in errors) / len(errors) if errors else None,
        math.sqrt(sum(error ** 2 for error in errors) / len(errors)) if errors else None,
        true_positive / precision_denominator if precision_denominator else None,
        true_positive / recall_denominator if recall_denominator else None,
    )
