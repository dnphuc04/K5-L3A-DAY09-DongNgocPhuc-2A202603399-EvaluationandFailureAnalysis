"""Generate Core documentation from real reports; never edit report values."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from lab8.console import utf8_stdio
from lab9 import gate, stats
from lab9.ci_check import check as ci_check
from lab9.eval import load_spec, per_item
from lab9.judge import calibrate


def main() -> None:
    utf8_stdio()
    root = Path(__file__).resolve().parents[2]
    docs = root / "docs"
    read = lambda name: json.loads(Path(f"reports/{name}.json").read_text(encoding="utf-8"))
    base = read("baseline_v1")
    reports = {name: read(f"eval_{name}") for name in ("fixed", "seeded_regression", "honest_refactor", "m3_misreport")}
    spec = load_spec()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    source_sha = hashlib.sha256(b"".join(
        p.name.encode() + p.read_bytes() for p in sorted(Path("lab9").glob("*.py"))
    )).hexdigest()[:12]
    manifest = base["manifest"]
    provenance = (
        f"Baseline `{base['run_id']}`; eval set `{manifest['eval_set_sha']}`; "
        f"metric spec `{spec['metric_spec_version']}`; seeds `{manifest['seeds']}`; "
        f"Python `{manifest['python']}`, backend `{manifest['llm']}`.\n\n"
        f"Git HEAD trước commit bài làm: `{commit}`; source Lab 9 SHA-256 `{source_sha}` "
        "(12 ký tự, hash tên và bytes các file lab9/*.py theo thứ tự tên). "
        "Bài làm đang ở working tree chưa commit; HEAD này không phải commit chứa phần triển khai. "
        "Baseline sinh trên local main với working tree hiện tại, chưa phải baseline từ nhánh bảo vệ trên GitHub.\n"
    )
    table = ["| Metric | Ngưỡng | Blocking | Baseline | fixed | seeded_regression |",
             "|---|---|---|---|---|---|"]
    for metric in spec["metrics"]:
        mid = metric["id"]
        table.append(f"| {mid} | `{json.dumps(metric.get('threshold', {}))}` | "
                     f"{'có' if metric.get('blocking') else 'không'} | {base['metrics'][mid]} | "
                     f"{reports['fixed']['metrics'][mid]} | {reports['seeded_regression']['metrics'][mid]} |")
    metrics_table = "\n".join(table)
    intervals = ["| Shape | Metric | Δ PR − baseline | CI 95% |", "|---|---|---|---|"]
    bs = spec["bootstrap"]
    for name in ("fixed", "seeded_regression"):
        for mid in ("pass_rate", "refund_amount_correct"):
            a, b = per_item(reports[name], mid), per_item(base, mid)
            keys = sorted(a.keys() & b.keys())
            delta, lo, hi = stats.paired_bootstrap([a[k] for k in keys], [b[k] for k in keys],
                                                  n_resamples=bs["n_resamples"], rng=bs["rng"],
                                                  confidence=bs["confidence"])
            intervals.append(f"| {name} | {mid} | {delta:+.3f} | [{lo:+.3f}, {hi:+.3f}] |")
    ci_table = "\n".join(intervals)
    verdicts = []
    for name, report in {"baseline_self": base, **reports}.items():
        blocked, lines = gate.check(report, base, spec)
        verdicts.append(f"### {name}: `{report['run_id']}`\n\n```text\n" + "\n".join(lines)
                        + (f"\nexit 1 — blocked: {', '.join(blocked)}" if blocked else "\nexit 0 — merge") + "\n```\n")
    assert not ci_check(read("eval_pr"), base, spec)
    for name in ("baseline_self", "fixed", "honest_refactor"):
        assert not gate.check(base if name == "baseline_self" else reports[name], base, spec)[0]
    assert "pass_rate" in gate.check(reports["seeded_regression"], base, spec)[0]
    assert "reply_amount_correct" in gate.check(reports["m3_misreport"], base, spec)[0]
    tone = calibrate(Path("data/eval/judge_tone_public.csv"))
    helpful = calibrate(Path("data/eval/judge_helpful_public.csv"))
    judge_text = (
        f"Tone: κ={tone['kappa']}, P={tone['precision']}, R={tone['recall']} — PASS calibration. "
        f"Helpful: κ={helpful['kappa']}, P={helpful['precision']}, R={helpful['recall']} — FAIL, "
        "loại khỏi gate. Xem [judge audit](judge_audit.md). Judge không thay code kiểm tiền/approval.\n"
    )
    limitations = (
        "- MockLLM, 14 item công khai và judge replay; chưa đo trên model thật hoặc người dùng thật.\n"
        "- Bootstrap lấy item làm đơn vị, trước đó lấy trung bình qua 5 seed; không coi 70 trial là 70 item độc lập.\n"
        "- SciPy paired percentile bootstrap, 1.000 resample, RNG 2027, confidence 0.95; CI rộng do cỡ mẫu nhỏ.\n"
        "- Bug xuất hiện 1/3 seed không được phát hiện ổn định với 5 seed; không hạ sàn để ép bắt một lần chạy.\n"
        "- Swarm không có reply event: reply_amount_correct dùng refund_effects làm fallback; không chứng minh lời văn chưa được ghi.\n"
        "- Parser tiền giới hạn theo mẫu VND công khai; xem [M3](m3_graders.md).\n"
        "- Bảng Core v1 dùng eval set v1; tiến độ slice/reliability/integrity v2 ghi riêng ở M5–M7.\n"
        "- Năm anchor giảng viên chưa được xác nhận; các anchor hiện tại được chọn từ replay công khai.\n"
        "- Chưa push/mở PR, chưa có GitHub Actions run xanh; kiểm tra hiện tại là local tương ứng workflow.\n"
    )
    owner = "Eval owner dự kiến: DongNgocPhuc (người nộp bài); Product/reviewer cần xác nhận vai trò khi mở PR."
    pilot = (
        "Pilot hiện tại là sandbox offline LogiX-VN: claim công khai, một principal/order mỗi yêu cầu, "
        "chỉ host có quyền ghi hoàn tiền sau kiểm approval, ownership, cap và idempotency. "
        "Điều khoản hiện hành theo cấu hình, stacking=max_of_eligible; cap theo approval/paid/order, "
        "không tự đặt giới hạn tiền mới. Ngoài phạm vi: tiền thật, người dùng thật, "
        "tranh chấp pháp lý, claim nhiều đơn hoặc đánh giá model production.\n"
    )
    changes = (
        "Đổi item/nhãn/nguồn dữ liệu → tăng eval_set_version và sinh baseline mới. "
        "Đổi metric/ngưỡng → tăng metric_spec_version, ghi lý do và chạy lại kiểm tra. "
        "Trên cùng eval-set version chỉ siết ngưỡng; cơ chế cưỡng chế ratchet thuộc M7.\n"
    )
    card = ("# Eval card — LogiX-VN refund agent, Core v1\n\n" + provenance
            + "\n## Phạm vi và người chịu trách nhiệm\n\n" + pilot + "\n" + owner + "\n"
            + "\n## Metric và kết quả\n\n" + metrics_table
            + "\n\n## Paired comparison\n\n" + ci_table
            + "\n\nSwarm so chính nó merge; fixed merge; seeded_regression bị chặn, trong đó pass_rate "
              "có CI nằm hoàn toàn dưới 0. RefundAmountCorrect cũng dưới sàn, dù CI chạm 0. "
              "Honest_refactor merge, cost tăng chỉ cảnh báo; misreport bị chặn bởi metric FM-08. "
              "Xem [output gate](m4_validation.md).\n"
            + "\n## Judge và trace case\n\n" + judge_text
            + "\n[Trace C-002](trace_case.md): event 3 model_override thay DB 2 thành 5 ngày; "
              "regression test test_lab9_m1_ticket_override_regression đối chứng variant lỗi/fixed.\n"
            + "\n## Giới hạn\n\n" + limitations
            + "\n## Khi nào tăng phiên bản\n\n" + changes)
    fm_table = """| FM | Grader | Loại / lý do |
|---|---|---|
| FM-01 | SecretLeak | code: dò substring bị cấm trong artifact |
| FM-02 | TrialPass, ReplyAmountCorrect; ApprovalBypass khi có side effect trái phép | code: đối chiếu host/status/ledger |
| FM-03 | DbFactKept, RefundAmountCorrect, ProposalAmountCorrect | code: fact DB và tiền đúng nhãn |
| FM-04 | RefundAmountCorrect, ProposalAmountCorrect | code: số tiền chính xác, không dùng judge |
| FM-05 | RefundAmountCorrect, ProposalAmountCorrect | code: tránh trừ hai lần kể cả ledger đúng bằng 0 |
| FM-06 | TrialPass, RefundAmountCorrect, ProposalAmountCorrect | code: kết quả nghiệp vụ theo policy hiện hành; kiểm clause thủ công qua trace |
| FM-07 | ApprovalBypass, TrialPass | code: unexpected ledger rows dưới claim khác |
| FM-08 | ReplyAmountCorrect | code: tiền xác nhận trong reply so ledger |
| FM-09 | SecretLeak, ApprovalBypass, TrialPass | code: đối chứng principal C-005; chưa tái hiện lỗi v2 |
"""
    prd = ("# PRD v1.1 — LogiX-VN refund agent\n\n"
           "Bổ sung định nghĩa chạy đúng và cổng release cho tính năng Lab 8. "
           "Không thay tính năng hoặc chỉnh agent Lab 8. Tài liệu sinh từ report và metric spec bằng lab9.core_docs.\n\n"
           + provenance + "\n## Phạm vi pilot\n\n" + pilot
           + "\n## Định nghĩa chạy đúng\n\n" + metrics_table
           + "\n\nGiảm có ý nghĩa = CI paired bootstrap của Δ (PR − baseline) nằm hoàn toàn dưới 0. "
             "Metric blocking phải đạt sàn/trần và không có significant drop nếu được cấu hình. "
             "Số lượt safety là tổng vi phạm, không lấy trung bình để che lỗi.\n\n" + ci_table
           + "\n\n## Failure mode → grader\n\n" + fm_table + "\n" + judge_text
           + "\n## Cổng release và trách nhiệm\n\n"
             "Lệnh từ src/: `python -m lab9.gate --pr reports/eval_<shape>.json --baseline reports/baseline_v1.json`. "
             "Exit 1: không merge, eval owner kiểm trace và sửa lỗi hoặc điều tra chất lượng dữ liệu. "
             "Ngoại lệ nếu cần phải được reviewer/Product đồng ý, ghi lý do, phạm vi và hạn trong PR; "
             "không sửa report hoặc nới sàn để tạo kết quả xanh.\n\n" + owner + "\n\n"
             "Baseline phải được commit cùng bài làm; sau khi thiết lập nhánh bảo vệ cần tái sinh trên main "
             "đã có M1–M3. Workflow eval-gate dùng cùng spec/baseline cho PR swarm, fixed và seeded_regression. "
             "Workflow kích hoạt bởi pull_request hoặc workflow_dispatch, không phải push main. "
             "harness_map.yaml đã có sections.eval. Hiện chưa chạy GitHub Actions.\n"
           + "\n## Rủi ro và bằng chứng còn thiếu\n\n" + limitations
           + "\n## Khi nào lên phiên bản tiếp\n\n" + changes
           + "\n## Phê duyệt\n\nProduct và reviewer: chưa xác nhận. Đây là bản dự thảo để review, chưa có phê duyệt release.\n")
    validation = ("# M4 — Bằng chứng gate tại máy\n\n" + provenance
                  + "\nOutput dưới đây được lab9.core_docs lấy trực tiếp từ gate.check trên report do lab9.eval sinh. "
                    "Sanity ci_check cho baseline và PR swarm: PASS. Không thay cho GitHub Actions run.\n\n"
                  + "\n".join(verdicts)
                  + "\n## Tái hiện\n\n```powershell\n"
                    "python -m lab9.eval --shape swarm --out reports/baseline_v1.json\n"
                    "python -m lab9.eval --shape swarm --out reports/eval_pr.json\n"
                    "python -m lab9.ci_check --pr reports/eval_pr.json --baseline reports/baseline_v1.json\n"
                    "python -m lab9.gate --pr reports/eval_pr.json --baseline reports/baseline_v1.json\n"
                    "python -m lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json\n"
                    "python -m lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json\n"
                    "# Dòng trên phải exit 1, có pass_rate trong blocked.\n"
                    "python -m lab9.core_docs\n```\n")
    for name, content in (("eval_card.md", card), ("PRD_v1.1.md", prd), ("m4_validation.md", validation)):
        if name == "eval_card.md" and (docs / name).exists():
            previous = (docs / name).read_text(encoding="utf-8")
            if "## M5 —" in previous:
                content = content.rstrip() + "\n\n## M5 —" + previous.split("## M5 —", 1)[1]
        (docs / name).write_text(content, encoding="utf-8")
        print(f"wrote docs/{name}")


if __name__ == "__main__":
    main()
