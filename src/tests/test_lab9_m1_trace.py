"""M1: replay public-label controls and the first-wrong-step regression case."""
import pytest

from lab9.evalset import V1_FAILURE_MODES
from lab9.trace_case import investigate


@pytest.mark.student
@pytest.mark.parametrize("claim_id", V1_FAILURE_MODES)
def test_lab9_m1_fixed_checks_public_label(claim_id):
    trial = investigate("fixed", claim_id, 11)["trial"]
    assert trial["lab8_pass"], trial["lab8_reason"]
    assert trial["unexpected_rows"] == 0


@pytest.mark.student
@pytest.mark.parametrize("seed", [11, 55])
def test_lab9_m1_ticket_override_regression(seed):
    bad = investigate("seeded_regression", "C-002", seed)["trial"]
    good = investigate("fixed", "C-002", seed)["trial"]
    assert [event["kind"] for event in bad["events"][:3]] == [
        "handoff", "investigator", "model_override",
    ]
    assert bad["events"][1]["payload"]["lookup_order"]["order"]["delay_days"] == 2
    assert bad["events"][2]["payload"] == {"delay_days": 5}
    assert bad["snapshot"]["refund_vnd"] == 20000
    assert not bad["lab8_pass"]
    assert good["lab8_pass"], good["lab8_reason"]
    assert good["snapshot"]["refund_vnd"] == 0
    assert all(event["kind"] != "model_override" for event in good["events"])
