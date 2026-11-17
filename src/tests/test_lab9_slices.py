"""M5: generic slice rules, item-level weighting, and adversarial coverage."""
from collections import Counter
import json
from pathlib import Path

import pytest
import yaml

from lab9.gate import slice_check

pytestmark = pytest.mark.student


def report(values, tag="unseen_slice"):
    return {"rows": [{"item_id": str(i), "seed": s, "pass_rate": value, "slices": [tag]}
                     for i, samples in enumerate(values) for s, value in enumerate(samples)]}


def spec(**rule):
    return {"slices": [{"name": "unseen_slice", "metric": "pass_rate", "blocking": True, **rule}]}


def test_arbitrary_slice_blocks_without_shape_name():
    base = report([[True] * 5, [True] * 5])
    pr = report([[False, True, True, True, True], [True] * 5])
    blocked, _ = slice_check(pr, base, spec(min=0.95))
    assert blocked == ["slice:unseen_slice/pass_rate"]


def test_slice_significant_drop_blocks_above_floor():
    base = report([[True] * 5, [True] * 5])
    pr = report([[True] * 4 + [False], [True] * 4 + [False]])
    blocked, lines = slice_check(pr, base, spec(min=0.7, no_significant_drop=True))
    assert blocked == ["slice:unseen_slice/pass_rate"]
    assert "CI [-0.200, -0.200]" in lines[0]


def test_slice_averages_items_instead_of_pooling_rows():
    # Mean per item = (0 + 1)/2 = .5; pooling would misleadingly yield .8.
    base = report([[True], [True] * 4])
    pr = report([[False], [True] * 4])
    assert slice_check(pr, base, spec(min=0.6))[0]


@pytest.mark.parametrize("pr", [report([]), report([[True]])])
def test_missing_or_unmatched_slice_is_blocked(pr):
    assert slice_check(pr, report([[True], [True]]), spec(min=0.9))[0]


def test_nonblocking_slice_warns_and_identical_slice_passes():
    base = report([[True] * 5, [True] * 5])
    assert slice_check(base, base, spec(min=0.9, no_significant_drop=True))[0] == []
    blocked, lines = slice_check(report([[False] * 5, [False] * 5]), base,
                                 spec(min=0.9, blocking=False))
    assert blocked == []
    assert lines[0].endswith("warn")


def test_v2_mapping_covers_every_attack_with_three_items():
    from lab9.evalset import V1_FAILURE_MODES

    mapping = yaml.safe_load(Path("config/fm_map.yaml").read_text(encoding="utf-8"))
    pack = json.loads(Path("data/eval/adversarial_v2.json").read_text(encoding="utf-8"))
    counts = Counter(fm for modes in V1_FAILURE_MODES.values() for fm in modes)
    attacked = set()
    for claim in pack["claims"]:
        codes = {mapping[mechanism] for mechanism in claim["mechanisms"]}
        assert all(isinstance(code, str) and code.startswith("FM-") for code in codes)
        attacked.update(codes)
        counts.update(codes)
    assert all(counts[fm] >= 3 for fm in attacked)
