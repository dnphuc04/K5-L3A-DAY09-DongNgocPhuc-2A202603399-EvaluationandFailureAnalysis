# M4 — Bằng chứng gate tại máy

## Tái lập giữa Windows và Linux

`lab9.evalset.sha12` hash bytes gốc của eval set. Baseline hiện tại sinh từ file CRLF trên Windows; checkout LF trên Linux cho hash khác dù item không đổi. `.gitattributes` cố định `eol=crlf` cho đúng hai file eval_set_v1/v2.jsonl để checkout trên hai hệ điều hành giữ cùng bytes và hash. Không sửa report, không bỏ kiểm integrity. GitHub Actions run 44123715751 đã phát hiện khác biệt này; đã khắc phục ở `c21d5fc` và xác nhận cả hai job xanh trên [GitHub Actions run 44124235967](https://github.com/dnphuc04/K5-L3A-DAY09-DongNgocPhuc-2A202603399-EvaluationandFailureAnalysis/actions/runs/44124235967).

Baseline `E-swarm-20261117-e85f`; eval set `e85f27d1d325`; metric spec `1.0`; seeds `[11, 22, 33, 44, 55]`; Python `3.14.6`, backend `MockLLM`.

Git HEAD trước commit bài làm: `d1b9471540727d693c9eb392667b9f0d8a998bf5`; source Lab 9 SHA-256 `19ae56c9890a` (12 ký tự, hash tên và bytes các file lab9/*.py theo thứ tự tên). Đây là thông tin provenance tại lúc sinh baseline, trước commit triển khai. Bài làm và baseline sau đó đã được commit trong `502fd5d`; main tại `c21d5fc` đã được CI Linux kiểm tra thành công. Baseline ban đầu sinh tại local, không phải trên nhánh bảo vệ.

Output dưới đây được lab9.core_docs lấy trực tiếp từ gate.check trên report do lab9.eval sinh. Sanity ci_check cho baseline và PR swarm: PASS. Không thay cho GitHub Actions run.

### baseline_self: `E-swarm-20261117-e85f`

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9857   {"min": 0.95}                                                         ok
  refund_amount_correct  0.9857   {"min": 0.95, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_rate              0.9857   {"min": 0.85, "no_significant_drop": true} Δ +0.000 CI [+0.000, +0.000] ok
  pass_5                 0.9286   {"min": 0.8}                                                          ok
  cost_per_success       49.567   {"max_increase": 0.1}                                                 ok
  reply_amount_correct   1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 0.9857   {"min": 0.95}                                                         ok
exit 0 — merge
```

### fixed: `E-fixed-20261117-e85f`

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.95, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_5                 1.0      {"min": 0.8}                                                          ok
  cost_per_success       48.7157  {"max_increase": 0.1}                                                 ok
  reply_amount_correct   1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 1.0      {"min": 0.95}                                                         ok
exit 0 — merge
```

### seeded_regression: `E-seeded_regression-20261117-e85f`

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9286   {"min": 0.95}                                                         warn
  refund_amount_correct  0.8571   {"min": 0.95, "no_significant_drop": true} Δ -0.129 CI [-0.315, +0.000] BLOCK
  pass_rate              0.7143   {"min": 0.85, "no_significant_drop": true} Δ -0.271 CI [-0.500, -0.057] BLOCK
  pass_5                 0.7143   {"min": 0.8}                                                          warn
  cost_per_success       81.202   {"max_increase": 0.1}                                                 warn
  reply_amount_correct   0.7857   {"min": 1.0}                                                          BLOCK
  proposal_amount_correct 0.7857   {"min": 0.95}                                                         BLOCK
exit 1 — blocked: refund_amount_correct, pass_rate, reply_amount_correct, proposal_amount_correct
```

### honest_refactor: `E-honest_refactor-20261117-e85f`

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.95, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_5                 1.0      {"min": 0.8}                                                          ok
  cost_per_success       57.2871  {"max_increase": 0.1}                                                 warn
  reply_amount_correct   1.0      {"min": 1.0}                                                          ok
  proposal_amount_correct 1.0      {"min": 0.95}                                                         ok
exit 0 — merge
```

### m3_misreport: `E-m3_misreport-20261117-e85f`

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           1.0      {"min": 0.95}                                                         ok
  refund_amount_correct  1.0      {"min": 0.95, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_rate              1.0      {"min": 0.85, "no_significant_drop": true} Δ +0.014 CI [+0.000, +0.043] ok
  pass_5                 1.0      {"min": 0.8}                                                          ok
  cost_per_success       48.7157  {"max_increase": 0.1}                                                 ok
  reply_amount_correct   0.8571   {"min": 1.0}                                                          BLOCK
  proposal_amount_correct 1.0      {"min": 0.95}                                                         ok
exit 1 — blocked: reply_amount_correct
```

## Tái hiện

```powershell
python -m lab9.eval --shape swarm --out reports/baseline_v1.json
python -m lab9.eval --shape swarm --out reports/eval_pr.json
python -m lab9.ci_check --pr reports/eval_pr.json --baseline reports/baseline_v1.json
python -m lab9.gate --pr reports/eval_pr.json --baseline reports/baseline_v1.json
python -m lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json
python -m lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json
# Dòng trên phải exit 1, có pass_rate trong blocked.
python -m lab9.core_docs
```
