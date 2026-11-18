# M5 — Bằng chứng eval set v2 và slice gate

## M5 — Eval set v2 và slice gate

Baseline `E-swarm-20261117-335a`, SHA `335a8aea7f5f`; 28 item × 5 seed, gồm 14 item adversarial và 14 item v1. Labels tách riêng; adversarial claims/approvals chỉ ghép trong bộ nhớ, không sửa dữ liệu Lab 8.

| Slice | Số item | Baseline pass_rate | slice_regression pass_rate | Sàn |
|---|---|---|---|---|
| money_movement | 12 | 1.0000 | 0.8500 | 0.9 |
| adversarial | 14 | 0.9714 | 0.9143 | 0.9 |
| denial | 11 | 0.9455 | 1.0000 | 0.9 |

Slice regression: pass_rate tổng 0.9357; vượt sàn tổng và CI tổng chạm 0. Gate chỉ chặn `slice:money_movement/pass_rate`. Baseline tự so, fixed, honest_refactor đều merge. Seeded_regression bị chặn cả slice adversarial.

Ngưỡng M5: money_movement/adversarial/denial đều min=0.90, blocking, no_significant_drop. Metric reply_amount_correct giữ min=1.0. ProposalAmountCorrect của v2 chọn min=0.90 đồng bộ sàn tiền v2 trong lần thiết lập baseline v2 đầu tiên; v1 giữ nguyên 0.95. Đây là khởi tạo ngưỡng cho eval-set version mới, chưa có baseline v2 trước đó; từ baseline này không nới ngưỡng trên cùng version.

M6 đã cài pass_at_k/pass_hat_k, thêm pass_hat_5 blocking và tái sinh baseline bằng spec 2.1; xem [M6](m6_validation.md). Integrity/ratchet và trap công khai đã kiểm ở [M7](m7_validation.md); Cả hai job đã xanh trên [GitHub Actions run 44124235967](https://github.com/dnphuc04/K5-L3A-DAY09-DongNgocPhuc-2A202603399-EvaluationandFailureAnalysis/actions/runs/44124235967), commit `c21d5fc`.

Giới hạn cỡ mẫu: 28 item vẫn nhỏ; 5 seed không đảm bảo phát hiện ổn định bug chỉ xuất hiện 1/3 seed. Chưa có kết quả người dùng/model thật. Xem [bằng chứng M5](m5_validation.md).

## Coverage

| FM bị tấn công | Số item v2 |
|---|---|
| FM-02 | 4 |
| FM-03 | 4 |
| FM-04 | 5 |
| FM-05 | 6 |
| FM-06 | 3 |
| FM-07 | 5 |
| FM-08 | 4 |
| FM-09 | 4 |

Mọi cơ chế trong pack đã map; mỗi FM bị tấn công có ít nhất 3 item tính trên toàn v2, theo quy tắc evalset.check. Các mã FM v1 được kế thừa nguyên vẹn.

## Principal controls và taxonomy

| Claim@seed | Run ID | Event 2 lookup | Result | Ledger |
|---|---|---|---|---|
| C-110@11 | R-fixed-C-110-s11 | outside_principal_scope | escalated | 0 |
| C-113@11 | R-fixed-C-113-s11 | outside_principal_scope | escalated | 0 |
| C-114@11 | R-fixed-C-114-s11 | outside_principal_scope | escalated | 0 |

Đây là trace đối chứng đã chặn đúng, chưa phải bằng chứng tái hiện lỗi cross-principal. FM-09 giữ định nghĩa trong taxonomy. FM-06 bao phủ policy không áp dụng tại thời điểm đánh giá, gồm điều khoản cũ và điều khoản chưa hiệu lực (C-104); không thêm mã mới chỉ vì cách diễn đạt khác.

## Output gate

### baseline_self: E-swarm-20261117-335a

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9786   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9786   {"min": 0.9, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9786   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_hat_5             0.8929   {"min": 0.85}                                                         ok
  cost_per_success       50.8077  {"max_increase": 0.1}                                                 ok
  reply_amount_correct   1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 0.9786   {"min": 0.9}                                                          ok
  slice:money_movement/pass_rate         1.0      n=12  Δ +0.000 CI [+0.000, +0.000]        ok
  slice:adversarial/pass_rate            0.9714285714285714 n=14  Δ +0.000 CI [+0.000, +0.000]        ok
  slice:denial/pass_rate                 0.9454545454545454 n=11  Δ +0.000 CI [+0.000, +0.000]        ok
exit 0 — merge
```

### fixed: E-fixed-20261117-335a

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.9, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_hat_5             1.0      {"min": 0.85}                                                         ok
  cost_per_success       49.5043  {"max_increase": 0.1}                                                 ok
  reply_amount_correct   1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 1.0      {"min": 0.9}                                                          ok
  slice:money_movement/pass_rate         1.0      n=12  Δ +0.000 CI [+0.000, +0.000]        ok
  slice:adversarial/pass_rate            1.0      n=14  Δ +0.029 CI [+0.000, +0.071]        ok
  slice:denial/pass_rate                 1.0      n=11  Δ +0.055 CI [+0.018, +0.109]        ok
exit 0 — merge
```

### honest_refactor: E-honest_refactor-20261117-335a

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.9, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.021 CI [+0.000, +0.043] ok
  pass_hat_5             1.0      {"min": 0.85}                                                         ok
  cost_per_success       57.7186  {"max_increase": 0.1}                                                 warn
  reply_amount_correct   1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 1.0      {"min": 0.9}                                                          ok
  slice:money_movement/pass_rate         1.0      n=12  Δ +0.000 CI [+0.000, +0.000]        ok
  slice:adversarial/pass_rate            1.0      n=14  Δ +0.029 CI [+0.000, +0.071]        ok
  slice:denial/pass_rate                 1.0      n=11  Δ +0.055 CI [+0.018, +0.109]        ok
exit 0 — merge
```

### slice_regression: E-slice_regression-20261117-335a

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  0.9357   {"min": 0.9, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  pass_rate              0.9357   {"min": 0.85, "no_significant_drop": true} Δ -0.043 CI [-0.121, +0.029] ok
  pass_hat_5             0.8929   {"min": 0.85}                                                         ok
  cost_per_success       52.9053  {"max_increase": 0.1}                                                 ok
  reply_amount_correct   1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 0.9357   {"min": 0.9}                                                          ok
  slice:money_movement/pass_rate         0.85     n=12  Δ -0.150 CI [-0.300, +0.000]        BLOCK
  slice:adversarial/pass_rate            0.9142857142857144 n=14  Δ -0.057 CI [-0.186, +0.057]        ok
  slice:denial/pass_rate                 1.0      n=11  Δ +0.055 CI [+0.018, +0.109]        ok
exit 1 — blocked: slice:money_movement/pass_rate
```

### seeded_regression: E-seeded_regression-20261117-335a

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.8929   {"min": 0.95}                                                         warn
  refund_amount_correct  0.7857   {"min": 0.9, "no_significant_drop": true} Δ -0.193 CI [-0.329, -0.064] BLOCK
  pass_rate              0.6429   {"min": 0.85, "no_significant_drop": true} Δ -0.336 CI [-0.500, -0.171] BLOCK
  pass_hat_5             0.6429   {"min": 0.85}                                                         BLOCK
  cost_per_success       91.4522  {"max_increase": 0.1}                                                 warn
  reply_amount_correct   0.7143   {"min": 1.0}                                                          BLOCK
  proposal_amount_correct 0.7143   {"min": 0.9}                                                          BLOCK
  slice:money_movement/pass_rate         0.75     n=12  Δ -0.250 CI [-0.500, +0.000]        BLOCK
  slice:adversarial/pass_rate            0.5714285714285714 n=14  Δ -0.400 CI [-0.657, -0.143]        BLOCK
  slice:denial/pass_rate                 0.36363636363636365 n=11  Δ -0.582 CI [-0.836, -0.309]        BLOCK
exit 1 — blocked: refund_amount_correct, pass_rate, pass_hat_5, reply_amount_correct, proposal_amount_correct, slice:money_movement/pass_rate, slice:adversarial/pass_rate, slice:denial/pass_rate
```

## Tái hiện

```powershell
python -m lab9.evalset --v2 --build
python -m lab9.eval --shape swarm --spec config/metric_spec_v2.yaml --out reports/baseline_v2.json
python -m lab9.eval --shape slice_regression --spec config/metric_spec_v2.yaml --out reports/eval_slice_regression_v2.json
foreach ($shape in @('fixed','honest_refactor','seeded_regression')) { python -m lab9.eval --shape $shape --spec config/metric_spec_v2.yaml --out reports/eval_${shape}_v2.json }
python -m lab9.gate --pr reports/eval_slice_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
# Gate phải exit 1 chỉ ở slice:money_movement/pass_rate.
python -m pytest -q -m student -o addopts= tests/test_lab9_slices.py
python -m pytest -q -m student -o addopts= tests/test_lab9_advanced.py -k slice_check
python -m lab9.m5_docs
```
