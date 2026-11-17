"""M6: compare estimators with explicit draws, not just formula examples."""
from itertools import combinations

import pytest

from lab9 import stats
from lab9.eval import aggregate

pytestmark = pytest.mark.student


def test_pass_estimators_match_exhaustive_draws():
    for n in range(1, 8):
        for c in range(n + 1):
            for k in range(1, n + 1):
                draws = list(combinations(range(n), k))
                any_pass = sum(any(i < c for i in draw) for draw in draws) / len(draws)
                all_pass = sum(all(i < c for i in draw) for draw in draws) / len(draws)
                assert stats.pass_at_k(n, c, k) == pytest.approx(any_pass)
                assert stats.pass_hat_k(n, c, k) == pytest.approx(all_pass)
                assert stats.pass_hat_k(n, c, k) <= c / n <= stats.pass_at_k(n, c, k)


@pytest.mark.parametrize("fn", [stats.pass_at_k, stats.pass_hat_k])
@pytest.mark.parametrize("args", [
    (0, 0, 1), (-1, 0, 1), (5, -1, 1), (5, 6, 1), (5, 2, 0),
    (5, 2, 6), (5.0, 2, 1), (5, 2.5, 1), (5, 2, True), (True, 0, 1),
])
def test_pass_estimators_reject_invalid_counts(fn, args):
    with pytest.raises(ValueError):
        fn(*args)


def test_rare_success_estimator_does_not_lose_precision():
    assert stats.pass_at_k(10**18, 1, 1) == pytest.approx(1e-18, rel=1e-12, abs=0)


def test_aggregate_distinguishes_one_success_from_reliability():
    rows = [{"item_id": "a", "seed": i, "pass_rate": i != 0, "cost": 1.0} for i in range(5)]
    metrics = aggregate(rows, ["pass_rate"], k_values=[1, 3, 5])
    assert metrics["pass_rate"] == 0.8
    assert metrics["pass_at_5"] == 1.0
    assert metrics["pass_hat_5"] == 0.0
    assert metrics["pass_hat_3"] == 0.4
    assert metrics["pass_hat_1"] == metrics["pass_at_1"] == metrics["pass_rate"]
