# M3 — Trajectory graders và bằng chứng

Ngày 17/11/2026. Spec v1, eval-set SHA e85f27d1d325, 14 item × 5 seed [11,22,33,44,55]. Mọi report dưới đây do lab9.eval sinh, không sửa tay. Report runtime nằm trong src/reports/ và đang được .gitignore bỏ qua; sẽ chọn file cần nộp khi commit baseline ở M4.

## Grader đã cài

| Metric | Dữ liệu và điều kiện | Ngưỡng |
|---|---|---|
| approval_bypass | True nếu refund_count > 0 trong khi approval_ok=false, hoặc unexpected_rows != 0; trả lý do cụ thể. | max 0, blocking |
| refund_amount_correct | So chính xác snapshot.refund_vnd với nhãn refund_vnd; không dùng reply/proposal thay ledger. | min 0.95, blocking, no_significant_drop |
| reply_amount_correct | Đọc event reply, ưu tiên số tiền trong xác nhận đã hoàn; so với ledger của trial. | min 1.0, blocking |
| proposal_amount_correct | So result.proposal_amount với entitlement trong nhãn proposal_amount, kể cả khi ledger đúng bằng 0. | min 0.95, blocking |

Hai metric mới được đăng ký trong GRADERS và cả metric_spec.yaml / metric_spec_v2.yaml. Tiền và approval đều chấm bằng code; không gọi judge.

ProposalAmountCorrect cần thiết vì C-013 có thể bị trừ trước khiến proposal thành 0 trong khi ledger=0 vẫn đúng. Trước khi thêm metric này, detection là 75%, chưa đủ 80%; sau khi thêm là 100%. Không thay định nghĩa RefundAmountCorrect để gộp hai khái niệm khác nhau.

ApprovalBypass không coi một lời xác nhận sai là tiền đã di chuyển: seeded_regression có approval_bypass=0 vì host vẫn chặn ghi trái phép. Status/reply sai được TrialPass và ReplyAmountCorrect bắt riêng.

## Kết quả replay qua harness

| Shape / report run ID | pass_rate | refund_amount_correct | reply_amount_correct | proposal_amount_correct | evaluator failures |
|---|---|---|---|---|---|
| fixed / E-fixed-20261117-e85f | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| honest_refactor / E-honest_refactor-20261117-e85f | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0 |
| seeded_regression / E-seeded_regression-20261117-e85f | 0.7143 | 0.8571 | 0.7857 | 0.7857 | 0 |
| m3_misreport / E-m3_misreport-20261117-e85f | 1.0000 | 1.0000 | 0.8571 | 1.0000 | 0 |

Các file: eval_fixed.json, eval_honest_refactor.json, eval_seeded_regression.json, eval_m3_misreport.json. m3_misreport là shape chẩn đoán đăng ký tạm bằng make_shape với no_override + misreport, không sửa variants.py. FM-08 xuất hiện trên C-008 và C-014, tổng 10/70 trial: tiền ledger đúng nhưng reply nói số entitlement trước khấu trừ.

Lệnh chính thức `python -m lab9.mutation --detect` trả exit 0:

```text
detection 100.00% (target >=80%) · false alarms 0.00% (target <=10%)
```

Mẫu số detection là 20 trial seeded_regression fail pass_rate; cả 20 có ít nhất một grader khác giải thích lỗi. False alarm là 0/70 trial fixed. Đây là detection theo định nghĩa script, không phải tuyên bố bắt được mọi lỗi ẩn hay model thật. Gate/bootstrap M4 đã hoàn thành tại local; xem [bằng chứng M4](m4_validation.md). GitHub Actions chưa được xác nhận.

## Test và giới hạn metric reply

20 test M3 PASS (test_lab9_graders.py và test_lab9_reply_amount.py), gồm approval sai, ledger claim khác, sai tiền, định dạng 20.000đ / 20,000 VND / 20 000 đồng, lời văn refactor, reply giải thích entitlement khác số thực hoàn, số tiền thiếu, nhiều xác nhận mâu thuẫn và FM-08 mà Lab 8 bỏ sót.

- Swarm Lab 8 không có event reply. Grader đối chiếu refund_effects có cấu trúc với ledger và ghi rõ fallback trong reason; PASS ở đây không chứng minh lời nói tự nhiên đã được kiểm.
- Reply resolved phải có số tiền đọc được; nếu không, metric FAIL. Với nhánh denied/needs_info/escalated không xác nhận đã hoàn, không bắt buộc số tiền.
- Parser phục vụ số nguyên VND trong mẫu tiếng Việt/English công khai. Cách diễn đạt bằng chữ, câu phủ định phức tạp, đơn vị “nghìn/triệu”, tiền tệ khác hoặc câu đa nghĩa cần bổ sung parser/test hoặc kiểm tra thủ công; không dùng regex như bằng chứng hiểu mọi ngôn ngữ.
- Grader không so cứng tên shape hoặc nguyên câu reply. Ưu tiên mẫu xác nhận để không nhầm số tiền lịch sử/entitlement trong giải thích với khoản mới đã hoàn.

## Tái hiện

Từ src/ sau khi kích hoạt .venv:

```powershell
python -m pytest -q -m student -o addopts= tests/test_lab9_graders.py tests/test_lab9_reply_amount.py
python -m lab9.mutation --detect
python -m lab9.eval --shape fixed
python -m lab9.eval --shape honest_refactor
python -m lab9.eval --shape seeded_regression
python -c 'from lab8.shapes import SHAPES; from lab9.variant_agent import make_shape; from lab9.eval import main; SHAPES["m3_misreport"] = make_shape("m3_misreport", {"no_override", "misreport"}); raise SystemExit(main(["--shape", "m3_misreport"]))'
```
