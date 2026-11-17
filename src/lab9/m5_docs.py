"""Write M5 evidence from v2 reports, coverage counts, and principal controls."""
from collections import Counter
import json
from pathlib import Path
import tempfile

from lab8.console import utf8_stdio
from lab9 import gate, variants
from lab9.eval import load_spec, load_world, make_task, per_item
from lab9.evalset import load_jsonl


def main() -> None:
    utf8_stdio()
    spec = load_spec(Path("config/metric_spec_v2.yaml"))
    read = lambda name: json.loads(Path(f"reports/{name}.json").read_text(encoding="utf-8"))
    base = read("baseline_v2")
    reports = {name: read(f"eval_{name}_v2")
               for name in ("fixed", "honest_refactor", "slice_regression", "seeded_regression")}
    items = load_jsonl(Path(spec["eval_set"]))
    counts = Counter(fm for item in items for fm in set(item["failure_modes"]))
    attacked = {fm for item in items if item["split"] == "adversarial" for fm in item["failure_modes"]}
    assert all(counts[fm] >= 3 for fm in attacked)
    coverage = "| FM bị tấn công | Số item v2 |\n|---|---|\n" + "\n".join(
        f"| {fm} | {counts[fm]} |" for fm in sorted(attacked))
    slice_table = ["| Slice | Số item | Baseline pass_rate | slice_regression pass_rate | Sàn |",
                   "|---|---|---|---|---|"]
    for rule in spec["slices"]:
        a = per_item(base, rule["metric"], rule["name"])
        b = per_item(reports["slice_regression"], rule["metric"], rule["name"])
        slice_table.append(f"| {rule['name']} | {len(a)} | {sum(a.values()) / len(a):.4f} | "
                           f"{sum(b.values()) / len(b):.4f} | {rule['min']} |")
    logs = []
    for name, report in {"baseline_self": base, **reports}.items():
        blocked, lines = gate.check(report, base, spec)
        if name in {"baseline_self", "fixed", "honest_refactor"}:
            assert not blocked, (name, blocked)
        if name == "slice_regression":
            assert blocked == ["slice:money_movement/pass_rate"], blocked
        if name == "seeded_regression":
            assert "slice:adversarial/pass_rate" in blocked, blocked
        logs.append(f"### {name}: {report['run_id']}\n\n```text\n" + "\n".join(lines)
                    + (f"\nexit 1 — blocked: {', '.join(blocked)}" if blocked else "\nexit 0 — merge") + "\n```\n")
    variants.register()
    world, claims = load_world(spec)
    labels = json.loads(Path(spec["labels"]).read_text(encoding="utf-8"))
    principal_rows = ["| Claim@seed | Run ID | Event 2 lookup | Result | Ledger |",
                      "|---|---|---|---|---|"]
    with tempfile.TemporaryDirectory(prefix="m5-principal-", ignore_cleanup_errors=True) as tmp:
        for cid in ("C-110", "C-113", "C-114"):
            trial = make_task("fixed", world, claims, labels, Path(tmp))({"claim_id": cid, "seed": 11})
            lookup = trial["events"][1]["payload"]["lookup_order"]
            assert trial["lab8_pass"] and not lookup["visible"]
            assert lookup["reason"] == "outside_principal_scope"
            principal_rows.append(f"| {cid}@11 | {trial['result']['run_id']} | outside_principal_scope | "
                                  f"{trial['result']['status']} | {trial['snapshot']['refund_vnd']} |")
    reliability_status = (
        "M6 đã cài pass_at_k/pass_hat_k, thêm pass_hat_5 blocking và tái sinh baseline bằng spec 2.1; "
        "xem [M6](m6_validation.md). Integrity/ratchet và trap công khai đã kiểm ở [M7](m7_validation.md); "
        "GitHub Actions chưa chạy.\n\n"
        if any(m["id"] == "pass_hat_5" for m in spec["metrics"]) else
        "M5 chưa cài pass_at_k/pass_hat_k, nên các trường pass@k/pass^k trong report v2 đang null; "
        "chưa có pass_hat_5 blocking. M6 sẽ đo A/A, chọn sàn và tái sinh baseline v2. "
        "Chưa có integrity/ratchet M7; chưa tuyên bố job eval-gate-v2 xanh.\n\n"
    )
    summary = (
        "## M5 — Eval set v2 và slice gate\n\n"
        f"Baseline `{base['run_id']}`, SHA `{base['manifest']['eval_set_sha']}`; "
        f"{len(items)} item × {len(spec['seeds'])} seed, "
        f"gồm {sum(i['split'] == 'adversarial' for i in items)} item adversarial và 14 item v1. "
        "Labels tách riêng; adversarial claims/approvals chỉ ghép trong bộ nhớ, không sửa dữ liệu Lab 8.\n\n"
        + "\n".join(slice_table)
        + "\n\nSlice regression: pass_rate tổng "
        f"{reports['slice_regression']['metrics']['pass_rate']}; vượt sàn tổng và CI tổng chạm 0. "
        "Gate chỉ chặn `slice:money_movement/pass_rate`. Baseline tự so, fixed, honest_refactor đều merge. "
        "Seeded_regression bị chặn cả slice adversarial.\n\n"
        "Ngưỡng M5: money_movement/adversarial/denial đều min=0.90, blocking, no_significant_drop. "
        "Metric reply_amount_correct giữ min=1.0. ProposalAmountCorrect của v2 chọn min=0.90 "
        "đồng bộ sàn tiền v2 trong lần thiết lập baseline v2 đầu tiên; v1 giữ nguyên 0.95. "
        "Đây là khởi tạo ngưỡng cho eval-set version mới, chưa có baseline v2 trước đó; "
        "từ baseline này không nới ngưỡng trên cùng version.\n\n"
        + reliability_status +
        "Giới hạn cỡ mẫu: 28 item vẫn nhỏ; 5 seed không đảm bảo phát hiện ổn định bug chỉ xuất hiện "
        "1/3 seed. Chưa có kết quả người dùng/model thật. Xem [bằng chứng M5](m5_validation.md).\n"
    )
    detail = ("# M5 — Bằng chứng eval set v2 và slice gate\n\n" + summary
              + "\n## Coverage\n\n" + coverage
              + "\n\nMọi cơ chế trong pack đã map; mỗi FM bị tấn công có ít nhất 3 item tính trên toàn v2, "
                "theo quy tắc evalset.check. Các mã FM v1 được kế thừa nguyên vẹn.\n"
              + "\n## Principal controls và taxonomy\n\n" + "\n".join(principal_rows)
              + "\n\nĐây là trace đối chứng đã chặn đúng, chưa phải bằng chứng tái hiện lỗi cross-principal. "
                "FM-09 giữ định nghĩa trong taxonomy. FM-06 bao phủ policy không áp dụng tại thời điểm đánh giá, "
                "gồm điều khoản cũ và điều khoản chưa hiệu lực (C-104); không thêm mã mới chỉ vì cách diễn đạt khác.\n"
              + "\n## Output gate\n\n" + "\n".join(logs)
              + "\n## Tái hiện\n\n```powershell\n"
                "python -m lab9.evalset --v2 --build\n"
                "python -m lab9.eval --shape swarm --spec config/metric_spec_v2.yaml --out reports/baseline_v2.json\n"
                "python -m lab9.eval --shape slice_regression --spec config/metric_spec_v2.yaml --out reports/eval_slice_regression_v2.json\n"
                "foreach ($shape in @('fixed','honest_refactor','seeded_regression')) { python -m lab9.eval --shape $shape --spec config/metric_spec_v2.yaml --out reports/eval_${shape}_v2.json }\n"
                "python -m lab9.gate --pr reports/eval_slice_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml\n"
                "# Gate phải exit 1 chỉ ở slice:money_movement/pass_rate.\n"
                "python -m pytest -q -m student -o addopts= tests/test_lab9_slices.py\n"
                "python -m pytest -q -m student -o addopts= tests/test_lab9_advanced.py -k slice_check\n"
                "python -m lab9.m5_docs\n```\n")
    docs = Path(__file__).resolve().parents[2] / "docs"
    (docs / "m5_validation.md").write_text(detail, encoding="utf-8")
    previous = (docs / "eval_card.md").read_text(encoding="utf-8")
    card = previous.split("## M5 —", 1)[0].rstrip()
    tail = "\n\n## M6 —" + previous.split("## M6 —", 1)[1] if "## M6 —" in previous else ""
    (docs / "eval_card.md").write_text(card + "\n\n" + summary + tail, encoding="utf-8")
    print("wrote docs/m5_validation.md and M5 section in docs/eval_card.md")


if __name__ == "__main__":
    main()
