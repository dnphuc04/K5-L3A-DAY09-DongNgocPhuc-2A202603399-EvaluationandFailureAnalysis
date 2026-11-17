"""Capture real gate exit codes for public traps and final M7 evidence."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys

from lab8.console import utf8_stdio
from lab9 import gate
from lab9.eval import load_spec


def main() -> None:
    utf8_stdio()
    read = lambda path: json.loads(Path(path).read_text(encoding="utf-8"))
    spec_path = "config/metric_spec_v2.yaml"
    baseline_path = "reports/baseline_v2.json"
    spec, base = load_spec(Path(spec_path)), read(baseline_path)
    trap_names = ("evaluator_errors_as_nan", "dropped_failing_rows", "cherry_picked_seeds", "loosened_spec")
    trap_table = ["| Trap công khai | Exit thực | Lý do |", "|---|---|---|"]
    logs = []
    for name in trap_names:
        args = ["-m", "lab9.gate", "--pr", f"reports/traps/{name}.json", "--baseline", baseline_path,
                "--spec", f"reports/traps/{name}.spec.yaml" if name == "loosened_spec" else spec_path]
        if name == "loosened_spec":
            args += ["--base-spec", spec_path]
        result = subprocess.run([sys.executable, *args], capture_output=True, text=True, encoding="utf-8",
                                env={**os.environ, "PYTHONUTF8": "1"})
        assert result.returncode == 1 and "INTEGRITY" in result.stdout, result.stdout + result.stderr
        if name == "loosened_spec":
            assert "RATCHET" in result.stdout
        trap_table.append(f"| {name} | {result.returncode} | {'INTEGRITY / RATCHET' if name == 'loosened_spec' else 'INTEGRITY'} |")
        logs.append(f"### {name}\n\n```text\npython {' '.join(args)}\n{result.stdout.rstrip()}\n```\n")
    green_tests = []
    for name in ("duplicate_rows", "failures_on_green", "forged_summary", "slice_relabel"):
        altered = copy.deepcopy(base)
        if name == "duplicate_rows":
            altered["rows"][-1] = copy.deepcopy(altered["rows"][0])
        elif name == "failures_on_green":
            altered["evaluator_failures"] = ["simulated failure on a green report"]
        elif name == "forged_summary":
            altered["metrics"]["pass_rate"] = 1.0
        else:
            for row in altered["rows"]:
                row["slices"] = [tag for tag in row["slices"] if tag != "money_movement"]
        assert gate.check(altered, base, spec, spec)[0] == ["integrity"]
        green_tests.append(f"| {name} | INTEGRITY |")
    assert not gate.check(base, base, spec, spec)[0]
    expected = {"fixed": False, "honest_refactor": False, "seeded_regression": True,
                "slice_regression": True, "flaky_regression": True}
    decisions = []
    for name, should_block in expected.items():
        report = read(f"reports/eval_{name}_v2.json")
        blocked = gate.check(report, base, spec, spec)[0]
        assert bool(blocked) == should_block
        decisions.append(f"| {name} | {'block' if blocked else 'merge'} | {', '.join(blocked) or '—'} |")
    quiet = read("reports/eval_m7_quiet_override_v2.json")
    quiet_blocked = gate.check(quiet, base, spec, spec)[0]
    assert quiet["metrics"]["db_fact_kept"] == 1.0 and quiet_blocked
    summary = (
        "## M7 — Integrity, ratchet và trap\n\n"
        f"Spec `{spec['metric_spec_version']}`, baseline `{base['run_id']}`, "
        f"eval SHA `{base['manifest']['eval_set_sha']}`. Bốn trap công khai đều được gate CLI trả exit 1 "
        "với INTEGRITY; trap nới spec có thêm RATCHET. lab9.traps trả exit 0 vì không trap công khai nào lọt.\n\n"
        + "\n".join(trap_table)
        + "\n\nKiểm cả PR và baseline: finite metrics, không mất grade, không evaluator failure; "
        "đủ Cartesian item × seed, không trùng dòng, đúng tập item/seed; slice nhất quán giữa seed và với baseline. "
        "Tính lại aggregate từ rows (gồm pass@k/pass^k và cost), chặn summary không khớp. "
        "Reorder dòng/seed/tag không bị báo nhầm.\n\n"
        "Ratchet cần **--base-spec từ nguồn tin cậy**: trên cùng eval-set version không hạ min, nâng max/max_increase, "
        "bỏ metric/slice, tắt blocking/no_significant_drop hoặc giảm seed/pass_k coverage. "
        "Đổi grader/kind/level hoặc bootstrap/data-source cũng bị yêu cầu review thay vì lặng lẽ thay thước đo. "
        "Workflow đã lấy spec từ base SHA của PR bằng git show và truyền --base-spec cho gate/scorecard; "
        "workflow_dispatch dùng SHA của lần chạy. CI v2 bổ sung bước chạy trap.\n\n"
        "Scorecard công khai giữ 3/3 regression bị chặn, 0 báo nhầm; baseline tự so merge. "
        "Đối chứng quiet_override không ghi model_override, db_fact_kept vẫn 1.0, nhưng bị gate chặn "
        "qua tiền/proposal và slice. Đây là phép thử bổ sung bằng công tắc công khai, không phải variant ẩn giảng viên.\n\n"
        "Chưa push/mở PR nên chưa có GitHub Actions run xanh. Test/trap ẩn giảng viên chưa được chạy. "
        "Tính nhất quán report không chứng minh rows là thật nếu kẻ sửa có thể đồng thời giả rows, totals và baseline: "
        "vẫn cần rerun từ CI tin cậy, bảo vệ baseline/spec và review thay đổi evaluator/workflow. "
        "Chưa có chữ ký artifact hoặc dữ liệu held-out mới. Xem [bằng chứng M7](m7_validation.md).\n"
    )
    detail = ("# M7 — Bằng chứng chống làm đẹp eval\n\n" + summary
              + "\n## Thử thêm trên report xanh\n\n| Tình huống | Kết quả |\n|---|---|\n"
              + "\n".join(green_tests)
              + "\n\nCác thử thêm dùng bản sao trong bộ nhớ; không sửa tay report gốc, không sửa variants.py/traps.py.\n"
              + "\n## Gate trên report thật\n\n| Shape | Quyết định | Blocked metrics |\n|---|---|---|\n"
              + "\n".join(decisions)
              + f"\n\nQuiet override: `{quiet['run_id']}`, db_fact_kept={quiet['metrics']['db_fact_kept']}, "
                f"pass_rate={quiet['metrics']['pass_rate']}; blocked: {', '.join(quiet_blocked)}.\n"
              + "\n## Bốn output gate CLI\n\n" + "\n".join(logs)
              + "\n## Tái hiện\n\n```powershell\n"
                "python -m pytest -q -m student -o addopts= -k lab9\n"
                "python -m lab9.traps --pr reports/eval_slice_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml\n"
                "python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json --base-spec config/metric_spec_v2.yaml\n"
                "python -m lab9.m7_docs\n```\n\n"
                "Dùng spec hiện tại làm base-spec trong lệnh local chỉ là self-check; CI phải lấy base-spec "
                "từ commit gốc được tin cậy. Xem .github/workflows/eval-gate.yml.\n")
    docs = Path(__file__).resolve().parents[2] / "docs"
    (docs / "m7_validation.md").write_text(detail, encoding="utf-8")
    card = (docs / "eval_card.md").read_text(encoding="utf-8").split("## M7 —", 1)[0].rstrip()
    (docs / "eval_card.md").write_text(card + "\n\n" + summary, encoding="utf-8")
    print("wrote docs/m7_validation.md and M7 section in docs/eval_card.md")


if __name__ == "__main__":
    main()
