"""M4: paired resampling and configured confidence must drive gate decisions."""
import pytest

from lab9 import gate, stats

pytestmark = pytest.mark.student


def test_bootstrap_preserves_pairing_for_constant_shift():
    # Independent resampling would invent a wide interval from item difficulty.
    delta, lo, hi = stats.paired_bootstrap([0.2, 0.6, 0.9], [0.1, 0.5, 0.8])
    assert delta == pytest.approx(0.1)
    assert lo == pytest.approx(0.1)
    assert hi == pytest.approx(0.1)


@pytest.mark.parametrize("a,b", [([], []), ([1], [1, 0]), ([float("nan"), 0], [0, 1]), ([1], [0])])
def test_bootstrap_rejects_unusable_pairs(a, b):
    with pytest.raises(ValueError):
        stats.paired_bootstrap(a, b)


def test_gate_uses_configured_confidence_and_blocks_significant_drop(monkeypatch):
    def bootstrap(a, b, **kwargs):
        assert a == [0.0, 1.0]
        assert b == [1.0, 1.0]
        assert kwargs == {"n_resamples": 500, "rng": 17, "confidence": 0.9}
        return -0.5, -1.0, -0.1

    monkeypatch.setattr(stats, "paired_bootstrap", bootstrap)
    base = {"manifest": {"eval_set_sha": "same", "items": 2, "seeds": [1]}, "metrics": {"pass_rate": 1.0},
            "rows": [{"item_id": "a", "seed": 1, "pass_rate": True}, {"item_id": "b", "seed": 1, "pass_rate": True}]}
    pr = {"manifest": {"eval_set_sha": "same", "items": 2, "seeds": [1]}, "metrics": {"pass_rate": 0.5},
          "rows": [{"item_id": "b", "seed": 1, "pass_rate": True}, {"item_id": "a", "seed": 1, "pass_rate": False}]}
    spec = {"bootstrap": {"n_resamples": 500, "rng": 17, "confidence": 0.9},
            "metrics": [{"id": "pass_rate", "blocking": True,
                         "threshold": {"min": 0.4, "no_significant_drop": True}}]}
    blocked, lines = gate.check(pr, base, spec)
    assert blocked == ["pass_rate"]
    assert "CI [-1.000, -0.100]" in lines[0]
