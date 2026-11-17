# M7 — Bằng chứng chống làm đẹp eval

## M7 — Integrity, ratchet và trap

Spec `2.1`, baseline `E-swarm-20261117-335a`, eval SHA `335a8aea7f5f`. Bốn trap công khai đều được gate CLI trả exit 1 với INTEGRITY; trap nới spec có thêm RATCHET. lab9.traps trả exit 0 vì không trap công khai nào lọt.

| Trap công khai | Exit thực | Lý do |
|---|---|---|
| evaluator_errors_as_nan | 1 | INTEGRITY |
| dropped_failing_rows | 1 | INTEGRITY |
| cherry_picked_seeds | 1 | INTEGRITY |
| loosened_spec | 1 | INTEGRITY / RATCHET |

Kiểm cả PR và baseline: finite metrics, không mất grade, không evaluator failure; đủ Cartesian item × seed, không trùng dòng, đúng tập item/seed; slice nhất quán giữa seed và với baseline. Tính lại aggregate từ rows (gồm pass@k/pass^k và cost), chặn summary không khớp. Reorder dòng/seed/tag không bị báo nhầm.

Ratchet cần **--base-spec từ nguồn tin cậy**: trên cùng eval-set version không hạ min, nâng max/max_increase, bỏ metric/slice, tắt blocking/no_significant_drop hoặc giảm seed/pass_k coverage. Đổi grader/kind/level hoặc bootstrap/data-source cũng bị yêu cầu review thay vì lặng lẽ thay thước đo. Workflow đã lấy spec từ base SHA của PR bằng git show và truyền --base-spec cho gate/scorecard; workflow_dispatch dùng SHA của lần chạy. CI v2 bổ sung bước chạy trap.

Scorecard công khai giữ 3/3 regression bị chặn, 0 báo nhầm; baseline tự so merge. Đối chứng quiet_override không ghi model_override, db_fact_kept vẫn 1.0, nhưng bị gate chặn qua tiền/proposal và slice. Đây là phép thử bổ sung bằng công tắc công khai, không phải variant ẩn giảng viên.

Chưa push/mở PR nên chưa có GitHub Actions run xanh. Test/trap ẩn giảng viên chưa được chạy. Tính nhất quán report không chứng minh rows là thật nếu kẻ sửa có thể đồng thời giả rows, totals và baseline: vẫn cần rerun từ CI tin cậy, bảo vệ baseline/spec và review thay đổi evaluator/workflow. Chưa có chữ ký artifact hoặc dữ liệu held-out mới. Xem [bằng chứng M7](m7_validation.md).

## Thử thêm trên report xanh

| Tình huống | Kết quả |
|---|---|
| duplicate_rows | INTEGRITY |
| failures_on_green | INTEGRITY |
| forged_summary | INTEGRITY |
| slice_relabel | INTEGRITY |

Các thử thêm dùng bản sao trong bộ nhớ; không sửa tay report gốc, không sửa variants.py/traps.py.

## Gate trên report thật

| Shape | Quyết định | Blocked metrics |
|---|---|---|
| fixed | merge | — |
| honest_refactor | merge | — |
| seeded_regression | block | refund_amount_correct, pass_rate, pass_hat_5, reply_amount_correct, proposal_amount_correct, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate |
| slice_regression | block | slice:money_movement/pass_rate |
| flaky_regression | block | pass_rate, pass_hat_5, slice:money_movement/pass_rate |

Quiet override: `E-m7_quiet_override-20261117-335a`, db_fact_kept=1.0, pass_rate=0.8929; blocked: refund_amount_correct, proposal_amount_correct, slice:adversarial/pass_rate, slice:denial/pass_rate.

## Bốn output gate CLI

### evaluator_errors_as_nan

```text
python -m lab9.gate --pr reports/traps/evaluator_errors_as_nan.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-335a vs main E-swarm-20261117-335a · eval set 335a8aea7f5f
  INTEGRITY PR: row 65 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 65 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 65 metric refund_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 67 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 67 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 67 metric refund_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 69 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 69 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 69 metric refund_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 90 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 90 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 90 metric refund_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 92 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 92 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 92 metric refund_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 94 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 94 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 94 metric refund_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 95 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 95 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 95 metric refund_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 97 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 97 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 97 metric refund_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 99 metric pass_rate missing, nonfinite, or not binary
  INTEGRITY PR: row 99 metric proposal_amount_correct missing, nonfinite, or not binary
  INTEGRITY PR: row 99 metric refund_amount_correct missing, nonfinite, or not binary
exit 1 — blocked: integrity
```

### dropped_failing_rows

```text
python -m lab9.gate --pr reports/traps/dropped_failing_rows.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-335a vs main E-swarm-20261117-335a · eval set 335a8aea7f5f
  INTEGRITY PR: row count 131 != 28 items x 5 seeds
  INTEGRITY PR: missing or invalid metric pass_hat_5
  INTEGRITY PR: incomplete item x seed Cartesian product
  INTEGRITY PR (item_id, seed) set differs from baseline
exit 1 — blocked: integrity
```

### cherry_picked_seeds

```text
python -m lab9.gate --pr reports/traps/cherry_picked_seeds.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-335a vs main E-swarm-20261117-335a · eval set 335a8aea7f5f
  INTEGRITY PR: missing or invalid metric pass_hat_5
  INTEGRITY PR (item_id, seed) set differs from baseline
  INTEGRITY PR: seeds differ from spec
exit 1 — blocked: integrity
```

### loosened_spec

```text
python -m lab9.gate --pr reports/traps/loosened_spec.json --baseline reports/baseline_v2.json --spec reports/traps/loosened_spec.spec.yaml --base-spec config/metric_spec_v2.yaml
gate: PR E-slice_regression-20261117-335a vs main E-swarm-20261117-335a · eval set 335a8aea7f5f
  INTEGRITY RATCHET metrics:db_fact_kept min loosened or removed
  INTEGRITY RATCHET metrics:refund_amount_correct min loosened or removed
  INTEGRITY RATCHET metrics:refund_amount_correct no_significant_drop disabled
  INTEGRITY RATCHET metrics:pass_rate min loosened or removed
  INTEGRITY RATCHET metrics:pass_rate no_significant_drop disabled
  INTEGRITY RATCHET metrics:pass_hat_5 min loosened or removed
  INTEGRITY RATCHET metrics:reply_amount_correct min loosened or removed
  INTEGRITY RATCHET metrics:proposal_amount_correct min loosened or removed
  INTEGRITY RATCHET slices:('money_movement', 'pass_rate') removed
  INTEGRITY RATCHET slices:('adversarial', 'pass_rate') removed
  INTEGRITY RATCHET slices:('denial', 'pass_rate') removed
exit 1 — blocked: integrity
```

## Tái hiện

```powershell
python -m pytest -q -m student -o addopts= -k lab9
python -m lab9.traps --pr reports/eval_slice_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
python -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json --base-spec config/metric_spec_v2.yaml
python -m lab9.m7_docs
```

Dùng spec hiện tại làm base-spec trong lệnh local chỉ là self-check; CI phải lấy base-spec từ commit gốc được tin cậy. Xem .github/workflows/eval-gate.yml.
