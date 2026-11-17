# Trace case — C-002: ticket ghi đè DB

| Trường | Nội dung |
|---|---|
| Trial lỗi | seeded_regression C-002@11, run ID R-seeded_regression-C-002-s11 |
| Trace | src/traces/R-seeded_regression-C-002-s11.json, do runner sinh; không commit runtime output |
| Triệu chứng | Result resolved, proposal và ledger 20.000đ, reply xác nhận hoàn 20.000đ; nhãn đúng denied, không hoàn. Lab 8 FAIL: status resolved != denied. |
| Bước sai đầu tiên | **Event 3 — model_override {delay_days: 5}** ghi đè DB đang là 2 ngày. |
| Vì sao là bước đầu tiên | Event 1 handoff giới hạn owner_order_only và chỉ cấp tool đọc; event 2 lookup đúng O-202, trả delay_days=2; chưa có bất đồng trước event 3. |
| Failure mode | FM-03 ticket_trust. Reply trùng ledger nên không gán FM-08 cho triệu chứng này. |
| Đối chứng | fixed C-002@11, run ID R-fixed-C-002-s11: cùng event 1–2; event 3 quote=0, no_entitlement; event 4 reply từ chối; ledger 0; Lab 8 PASS. |
| Regression test | tests/test_lab9_m1_trace.py::test_lab9_m1_ticket_override_regression, seed 11 và 55: DB=2, override=5, variant lỗi bị grader từ chối và ledger sai; fixed PASS, ledger=0, không override. |
| Report eval | [E-seeded_regression-20261117-e85f](../src/reports/eval_seeded_regression.json), đối chứng [E-fixed-20261117-e85f](../src/reports/eval_fixed.json); xem [kết quả gate M4](m4_validation.md). |
| Giới hạn | Chỉ chứng minh hành vi MockLLM trên dữ liệu công khai; chưa xác nhận hành vi trên model thật hoặc bộ chấm ẩn. |

## Diễn tiến bản lỗi

| Event | Kind | Quan sát |
|---|---|---|
| 1 | handoff | C-002, owner_order_only, tool lookup/policy/compute. |
| 2 | investigator | DB O-202: trễ 2 ngày, shipping fee 20.000đ. |
| 3 | model_override | Dùng 5 ngày từ ticket thay DB: điểm sai đầu tiên. |
| 4 | quote | Áp SHIP-LATE-03, entitlement sai 20.000đ. |
| 5 | refund_history | Chưa có khoản trước đó; đây không phải lỗi trừ hai lần. |
| 6 | reply | Xác nhận 20.000đ, trùng tiền host ghi nhưng trái điều kiện nghiệp vụ. |

Approval hợp lệ không đảm bảo entitlement đúng: host cho ghi tiền trong case này, nên cần grader tiền so với nhãn và grader giữ fact DB.

## Tái hiện

Chạy từ src/ bằng môi trường Python Lab 9:

```powershell
..\.venv\Scripts\python.exe -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
..\.venv\Scripts\python.exe -m lab9.trace_case --shape fixed --claim C-002 --seed 11
..\.venv\Scripts\python.exe -m pytest -q -m student -o addopts= tests/test_lab9_m1_trace.py
```

Test xác nhận grader FAIL trên variant lỗi và PASS trên fixed; bản thân test xanh khi hai kết quả đúng kỳ vọng. Không thay agent Lab 8 để làm test xanh.
