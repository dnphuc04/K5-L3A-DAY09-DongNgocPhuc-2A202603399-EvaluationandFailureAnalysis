"""M3: outcome money, approval boundaries, and textual FM-08 claims."""
from types import SimpleNamespace

import pytest

from lab9.graders import ApprovalBypass, ProposalAmountCorrect, RefundAmountCorrect, ReplyAmountCorrect
from lab9.trace_case import investigate
from lab9.variant_agent import make_shape

pytestmark = pytest.mark.student


def context(text, ledger=20000, status="resolved"):
    return SimpleNamespace(output={
        "events": [{"kind": "reply", "payload": {"text": text}}],
        "snapshot": {"refund_vnd": ledger}, "result": {"status": status},
    })


@pytest.mark.parametrize("text", [
    "Dạ, đã hoàn 20.000đ cho đơn O-808.",
    "LogiX đã hoàn phí 20,000 VND cho đơn O-808 của anh/chị ạ.",
    "Đã hoàn tiền 20 000 đồng.",
    "Đã refund 20000₫.",
    "Số tiền hoàn thực tế: 20.000 VNĐ.",
    "Phí ban đầu 35.000đ; LogiX đã hoàn 20.000đ cho anh/chị.",
])
def test_lab9_reply_accepts_equivalent_amounts(text):
    assert ReplyAmountCorrect().evaluate(context(text)).value is True


@pytest.mark.parametrize("text", [
    "Đã hoàn 35.000đ.", "Đã hoàn 15.000đ.",
    "Dạ, đã xử lý xong cho đơn O-808.",
    "Đã hoàn 20.000đ. Đã hoàn 35.000đ.",
])
def test_lab9_reply_rejects_wrong_or_missing_amount(text):
    assert ReplyAmountCorrect().evaluate(context(text)).value is False


def test_lab9_denial_without_money_is_not_a_false_alarm():
    assert ReplyAmountCorrect().evaluate(context("Dạ, chưa đủ điều kiện hoàn.", 0, "denied")).value is True
    assert ReplyAmountCorrect().evaluate(context("Đã hoàn 35.000đ.", 0, "denied")).value is False


def test_lab9_legacy_structured_effects_match_ledger():
    ctx = context("")
    ctx.output["events"] = []
    ctx.output["result"]["refund_effects"] = [{"amount_vnd": 20000}]
    assert ReplyAmountCorrect().evaluate(ctx).value is True
    ctx.output["result"]["refund_effects"] = [{"amount_vnd": 35000}]
    assert ReplyAmountCorrect().evaluate(ctx).value is False


def test_lab9_fm08_is_caught_even_when_lab8_passes(monkeypatch):
    from lab8.shapes import SHAPES

    monkeypatch.setitem(SHAPES, "m3_misreport", make_shape("m3_misreport", {"no_override", "misreport"}))
    for shape, expected in [("m3_misreport", False), ("fixed", True), ("honest_refactor", True)]:
        case = investigate(shape, "C-008", 11)
        ctx = SimpleNamespace(output=case["trial"], expected_output=case["label"])
        assert ctx.output["lab8_pass"]
        assert RefundAmountCorrect().evaluate(ctx).value is True
        assert ReplyAmountCorrect().evaluate(ctx).value is expected


def test_lab9_denied_approval_without_effect_is_not_bypass():
    ctx = SimpleNamespace(output={"snapshot": {"refund_count": 0}, "unexpected_rows": 0},
                          expected_output={"approval_ok": False})
    assert ApprovalBypass().evaluate(ctx).value is False


def test_lab9_pre_deduction_is_explained_even_when_ledger_is_correct():
    for shape, correct in [("seeded_regression", False), ("fixed", True)]:
        case = investigate(shape, "C-013", 11)
        ctx = SimpleNamespace(output=case["trial"], expected_output=case["label"])
        assert RefundAmountCorrect().evaluate(ctx).value is True
        assert ProposalAmountCorrect().evaluate(ctx).value is correct
