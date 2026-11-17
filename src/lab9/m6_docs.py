"""Generate M6 reliability and A/A evidence from script-generated reports."""
import json
from pathlib import Path

from lab8.console import utf8_stdio
from lab9 import gate
from lab9.eval import load_spec


def main() -> None:
    utf8_stdio()
    read = lambda name: json.loads(Path(f"reports/{name}.json").read_text(encoding="utf-8"))
    base, alternate = read("baseline_v2"), read("eval_swarm_aa_v2")
    spec = load_spec(Path("config/metric_spec_v2.yaml"))
    reports = {name: read(f"eval_{name}_v2") for name in
               ("fixed", "honest_refactor", "seeded_regression", "slice_regression", "flaky_regression")}
    aa = ["| Metric | Seeds chuẩn | Seeds A/A | Δ |", "|---|---|---|---|"]
    for metric, value in base["metrics"].items():
        other = alternate["metrics"][metric]
        assert value is not None and other is not None
        assert abs(value - other) < 1e-12, (metric, value, other)
        aa.append(f"| {metric} | {value} | {other} | {other - value:+.4f} |")
    table = ["| Shape | pass_rate | pass@5 | pass^5 | Gate |", "|---|---|---|---|---|"]
    logs = []
    for name, report in {"baseline_self": base, **reports}.items():
        blocked, lines = gate.check(report, base, spec)
        assert (not blocked) == (name in {"baseline_self", "fixed", "honest_refactor"})
        if name == "flaky_regression":
            assert "pass_hat_5" in blocked
        values = report["metrics"]
        table.append(f"| {name} | {values['pass_rate']} | {values['pass_at_5']} | "
                     f"{values['pass_hat_5']} | {'block: ' + ', '.join(blocked) if blocked else 'merge'} |")
        logs.append(f"### {name}: {report['run_id']}\n\n```text\n" + "\n".join(lines)
                    + (f"\nexit 1 — blocked: {', '.join(blocked)}" if blocked else "\nexit 0 — merge") + "\n```\n")
    floor = next(m["threshold"]["min"] for m in spec["metrics"] if m["id"] == "pass_hat_5")
    summary = (
        "## M6 — Nhiễu A/A và độ ổn định\n\n"
        f"Spec `{spec['metric_spec_version']}`, eval SHA `{base['manifest']['eval_set_sha']}`; "
        f"baseline `{base['run_id']}`. Đã tái sinh baseline và report v2, không còn pass@k/pass^k null. "
        "Sàn các metric trước giữ nguyên; bổ sung pass_hat_5 blocking.\n\n"
        "pass@k = 1 − C(n−c,k)/C(n,k): ít nhất một lần đúng. "
        "pass^k = C(c,k)/C(n,k): cả k lần đều đúng khi lấy mẫu không hoàn lại từ n lần. "
        "Ví dụ n=5,c=4,k=5: pass@5=1 nhưng pass^5=0; chỉ cần thử đến khi được không chứng minh độ ổn định. "
        "Code từ chối n/c/k sai phạm vi, không nguyên hoặc boolean.\n\n"
        f"A/A: seeds chuẩn `{base['manifest']['seeds']}`, seeds đối chứng `{alternate['manifest']['seeds']}`. "
        f"Mọi Δ=0; pass_hat_5 cùng bằng {base['metrics']['pass_hat_5']}. "
        f"Chọn sàn **{floor}**, dưới mức baseline quan sát được khoảng "
        f"{base['metrics']['pass_hat_5'] - floor:.4f}, đồng thời ≥0.8 theo rubric. "
        "Khoảng chênh này lớn hơn nhiễu quan sát 0; không coi đây là cận nhiễu của LLM thật.\n\n"
        + "\n".join(table)
        + "\n\nScorecard công khai: 3/3 regression bị chặn, 0 báo nhầm; "
        "lệnh lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json cũng exit 0.\n\n"
        "Hai bộ seed có cấu trúc tương ứng trong MockLLM, cho cùng kết quả tổng hợp; đây là một phép "
        "so sánh A/A, chưa ước lượng được phân bố nhiễu thực. LLM thật có ngẫu nhiên, drift model/provider "
        "và tương quan giữa các lần chạy; cần lặp A/A nhiều batch, dùng held-out và chọn sàn thấp hơn "
        "cận dưới vùng chạy trung thực với margin phù hợp, đồng thời tránh vùng nhiễu của Δ khi xét hồi quy. "
        "Không giảm sàn sau khi thấy một variant cụ thể lọt.\n\n"
        "Cỡ mẫu vẫn chỉ 28 item × 5 seed. Lỗi chỉ xuất hiện ở 1/3 seed không phát hiện ổn định với "
        "5 seed; pass^k là estimator trên mẫu, không đảm bảo xác suất thành công production. "
        "M7 đã bổ sung integrity/ratchet và kiểm trap công khai; xem [M7](m7_validation.md). "
        "Mutation công khai qua không chứng minh bắt được mọi trap ẩn. "
        "Xem [bằng chứng M6](m6_validation.md).\n"
    )
    detail = ("# M6 — Bằng chứng reliability và A/A\n\n" + summary
              + "\n## A/A từ report\n\n" + "\n".join(aa)
              + "\n\nNguồn: baseline_v2.json và eval_swarm_aa_v2.json, cùng spec 2.1. "
                "Run ID hiện không chứa seeds nên hai run swarm cùng ngày/SHA có thể trùng ID; "
                "phải dùng tên file và manifest.seeds để phân biệt. Không đưa hai report khác seed qua gate PR.\n"
              + "\n## Output gate\n\n" + "\n".join(logs)
              + "\n## Tái hiện\n\n```powershell\n"
                "python -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110\n"
                "python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json\n"
                "python -m lab9.gate --pr reports/eval_flaky_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml\n"
                "# Gate phải exit 1, có pass_hat_5.\n"
                "python -m pytest -q -m student -o addopts= tests/test_lab9_reliability.py\n"
                "python -m pytest -q -m student -o addopts= tests/test_lab9_advanced.py -k 'not integrity'\n"
                "python -m lab9.m6_docs\n```\n")
    docs = Path(__file__).resolve().parents[2] / "docs"
    (docs / "m6_validation.md").write_text(detail, encoding="utf-8")
    card = (docs / "eval_card.md").read_text(encoding="utf-8").split("## M6 —", 1)[0].rstrip()
    (docs / "eval_card.md").write_text(card + "\n\n" + summary, encoding="utf-8")
    print("wrote docs/m6_validation.md and M6 section in docs/eval_card.md")


if __name__ == "__main__":
    main()
