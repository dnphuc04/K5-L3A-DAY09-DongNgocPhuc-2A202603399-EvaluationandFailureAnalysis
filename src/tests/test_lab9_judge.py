"""M2 calibration decisions must fail safely on degenerate judges."""
import math

import pytest

from lab9 import stats
from lab9.judge import calibrate

pytestmark = pytest.mark.student


def test_public_judge_decisions():
    from pathlib import Path

    tone = calibrate(Path("data/eval/judge_tone_public.csv"))
    helpful = calibrate(Path("data/eval/judge_helpful_public.csv"))
    assert tone["passed"]
    assert not helpful["passed"]
    assert helpful["confusion"] == {"tp": 9, "fp": 0, "fn": 21, "tn": 70}
    assert helpful["corrected_fail_rate"] == pytest.approx(0.3)


def test_constant_judge_fails_calibration_without_crashing(tmp_path):
    path = tmp_path / "constant.csv"
    path.write_text("item_id,reply,human,judge\n1,ok,PASS,PASS\n2,ok,PASS,PASS\n", encoding="utf-8")
    result = calibrate(path)
    assert not result["passed"]
    assert math.isnan(result["kappa"])
    assert math.isnan(result["corrected_fail_rate"])
    assert (result["precision"], result["recall"]) == (0.0, 0.0)


def test_calibration_uses_unrounded_floors(tmp_path, monkeypatch):
    path = tmp_path / "borderline.csv"
    path.write_text("item_id,reply,human,judge\n1,bad,FAIL,FAIL\n2,ok,PASS,PASS\n", encoding="utf-8")
    monkeypatch.setattr(stats, "cohen_kappa", lambda h, j: 0.5999)
    result = calibrate(path)
    assert result["kappa"] == 0.6
    assert not result["passed"]


@pytest.mark.parametrize("human,judge", [([], []), (["PASS"], []), (["UNKNOWN"], ["PASS"])])
def test_confusion_rejects_invalid_labels(human, judge):
    with pytest.raises(ValueError):
        stats.confusion(human, judge)


@pytest.mark.parametrize("rates", [(0.3, 0, 1), (0.3, 0.2, 0.2), (float("nan"), 0.8, 0.9), (1.1, 0.8, 0.9)])
def test_rogan_gladen_rejects_invalid_calibration(rates):
    with pytest.raises(ValueError):
        stats.rogan_gladen(*rates)


def test_rogan_gladen_clips_upper_bound():
    assert stats.rogan_gladen(1.0, 0.8, 0.9) == 1.0
