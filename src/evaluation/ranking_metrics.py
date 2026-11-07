import math


def _prepare(recommended, relevant, k):
    if k <= 0:
        raise ValueError("k phải > 0")
    return list(dict.fromkeys(recommended))[:k], set(relevant)


def precision_at_k(recommended, relevant, k: int) -> float:
    items, targets = _prepare(recommended, relevant, k)
    return float(len(set(items) & targets) / k)


def recall_at_k(recommended, relevant, k: int) -> float:
    items, targets = _prepare(recommended, relevant, k)
    return float(len(set(items) & targets) / len(targets)) if targets else 0.0


def ndcg_at_k(recommended, relevant, k: int) -> float:
    items, targets = _prepare(recommended, relevant, k)
    ideal = sum(1 / math.log2(rank + 2) for rank in range(min(len(targets), k)))
    gain = sum(1 / math.log2(rank + 2) for rank, item in enumerate(items) if item in targets)
    return float(gain / ideal) if ideal else 0.0
