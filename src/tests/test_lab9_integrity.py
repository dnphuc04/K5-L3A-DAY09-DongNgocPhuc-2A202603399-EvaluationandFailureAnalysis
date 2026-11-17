"""M7: adversarial report/spec changes on otherwise green evidence."""
import copy

import pytest

from lab9.eval import aggregate
from lab9.gate import check, integrity_check

pytestmark = pytest.mark.student


@pytest.fixture
def evidence():
    spec = {"eval_set_version": "v2", "seeds": [1, 2], "pass_k": [2],
            "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True,
                         "threshold": {"min": 0.8, "no_significant_drop": True}},
                        {"id": "secret_leak", "kind": "safety", "blocking": True, "threshold": {"max": 0}},
                        {"id": "pass_hat_2", "kind": "capability", "blocking": True, "threshold": {"min": 0.8}}],
            "slices": [{"name": "money", "metric": "pass_rate", "min": 0.8,
                        "no_significant_drop": True, "blocking": True}]}
    rows = [{"item_id": cid, "seed": seed, "slices": ["money", "adversarial"],
             "pass_rate": True, "secret_leak": False, "cost": 1.0}
            for cid in ("a", "b") for seed in (1, 2)]
    base = {"manifest": {"eval_set_sha": "same", "items": 2, "seeds": [1, 2]},
            "rows": rows, "metrics": aggregate(rows, ["pass_rate", "secret_leak"], [2]),
            "evaluator_failures": []}
    return spec, base


@pytest.mark.parametrize("attack", [
    "duplicate", "failures_on_green", "missing_row_grade", "nan_row", "inf_summary",
    "forged_summary", "slice_relabel", "inconsistent_slice", "fake_seed", "bad_manifest",
    "negative_cost", "missing_cost", "dropped_seed_with_changed_manifest",
])
def test_integrity_blocks_gamed_green_report(evidence, attack):
    spec, base = evidence
    pr = copy.deepcopy(base)
    if attack == "duplicate":
        pr["rows"][-1] = copy.deepcopy(pr["rows"][0])
    elif attack == "failures_on_green":
        pr["evaluator_failures"] = ["grader crashed"]
    elif attack == "missing_row_grade":
        for row in pr["rows"]:
            row.pop("pass_rate")
    elif attack == "nan_row":
        pr["rows"][0]["pass_rate"] = float("nan")
    elif attack == "inf_summary":
        pr["metrics"]["pass_rate"] = float("inf")
    elif attack == "forged_summary":
        pr["rows"][0]["pass_rate"] = False
    elif attack == "slice_relabel":
        for row in pr["rows"]:
            row["slices"] = ["adversarial"]
    elif attack == "inconsistent_slice":
        pr["rows"][0]["slices"] = []
    elif attack == "fake_seed":
        pr["rows"][0]["seed"] = 99
    elif attack == "bad_manifest":
        pr["manifest"]["seeds"] = None
    elif attack == "negative_cost":
        pr["rows"][0]["cost"] = -1
    elif attack == "missing_cost":
        del pr["rows"][0]["cost"]
    elif attack == "dropped_seed_with_changed_manifest":
        pr["rows"] = [row for row in pr["rows"] if row["seed"] == 1]
        pr["manifest"]["seeds"] = [1]
    blocked, lines = check(pr, base, spec)
    assert blocked == ["integrity"]
    assert any("INTEGRITY" in line for line in lines)


@pytest.mark.parametrize("attack", ["lower_min", "remove_min", "raise_max", "disable_metric",
                                    "drop_metric", "drop_slice", "lower_slice", "disable_slice",
                                    "drop_significance", "drop_slice_significance", "drop_pass_k"])
def test_ratchet_blocks_weaker_same_version_spec(evidence, attack):
    spec, base = evidence
    loose = copy.deepcopy(spec)
    metric, rule = loose["metrics"][0], loose["slices"][0]
    if attack == "lower_min":
        metric["threshold"]["min"] = 0.7
    elif attack == "remove_min":
        del metric["threshold"]["min"]
    elif attack == "raise_max":
        loose["metrics"][1]["threshold"]["max"] = 1
    elif attack == "disable_metric":
        metric["blocking"] = False
    elif attack == "drop_metric":
        loose["metrics"] = loose["metrics"][1:]
    elif attack == "drop_slice":
        loose["slices"] = []
    elif attack == "lower_slice":
        rule["min"] = 0.7
    elif attack == "disable_slice":
        rule["blocking"] = False
    elif attack == "drop_significance":
        del metric["threshold"]["no_significant_drop"]
    elif attack == "drop_slice_significance":
        del rule["no_significant_drop"]
    elif attack == "drop_pass_k":
        loose["pass_k"] = []
    assert any("RATCHET" in reason for reason in integrity_check(base, base, loose, spec))


def test_reordering_and_stricter_spec_do_not_raise_false_alarm(evidence):
    spec, base = evidence
    pr = copy.deepcopy(base)
    pr["rows"].reverse()
    pr["manifest"]["seeds"].reverse()
    for row in pr["rows"]:
        row["slices"].reverse()
    strict = copy.deepcopy(spec)
    strict["metrics"][0]["threshold"]["min"] = 0.9
    assert integrity_check(pr, base, strict, spec) == []
    assert check(pr, base, strict, spec)[0] == []


def test_forged_derived_metric_is_recomputed_without_pass_k(evidence):
    spec, base = evidence
    pr = copy.deepcopy(base)
    pr["metrics"]["pass_hat_2"] = 0.5
    spec["pass_k"] = []
    assert integrity_check(pr, base, spec)


def test_corrupt_baseline_is_also_rejected(evidence):
    spec, base = evidence
    bad = copy.deepcopy(base)
    bad["evaluator_failures"] = ["hidden evaluator failure"]
    assert any("baseline" in problem for problem in integrity_check(base, bad, spec))
