# Judge audit — M2

Đánh giá ngày 17/11/2026, backend REPLAY: verdict lấy nguyên từ CSV công khai, không gọi model/API, không sửa nhãn hoặc verdict nguồn. FAIL là lớp dương: TP = người FAIL và judge FAIL; FP = người PASS nhưng judge FAIL; FN = người FAIL nhưng judge PASS; TN = cả hai PASS.

## Calibration và quyết định

| Tiêu chí | n | TP / FP / FN / TN | κ | Precision | Recall | Floors κ≥0.6, P≥0.8, R≥0.7 | Quyết định |
|---|---|---|---|---|---|---|---|
| tone_ok | 100 | 24 / 4 / 6 / 66 | 0.757 | 0.857 | 0.800 | PASS | Đủ điều kiện dùng cho tiêu chí tone trong phạm vi replay; chưa tự động thêm vào gate tiền/approval. |
| helpful | 100 | 9 / 0 / 21 / 70 | 0.375 | 1.000 | 0.300 | FAIL | Loại khỏi release gate; cần sửa rubric/context và calibration lại. |

Precision = TP/(TP+FP), Recall = TP/(TP+FN). κ hiệu chỉnh agreement kỳ vọng do phân bố nhãn. Accuracy của helpful là 79%, nhưng bỏ sót 21/30 lỗi (70%); Precision 100% không bù được Recall 30% và κ thấp.

| Tiêu chí | Failure rate judge quan sát | Sensitivity | Specificity | Rogan–Gladen hiệu chỉnh | Failure rate theo người |
|---|---|---|---|---|---|
| tone_ok | 0.280 | 24/30 = 0.800 | 66/70 ≈ 0.942857 | 0.300 | 0.300 |
| helpful | 0.090 | 9/30 = 0.300 | 70/70 = 1.000 | 0.300 | 0.300 |

Rogan–Gladen: (p_observed + specificity − 1)/(sensitivity + specificity − 1), chặn kết quả về [0,1]. Không hiệu chỉnh nếu sensitivity + specificity ≤ 1 hoặc tỷ lệ không hợp lệ. Kết quả bằng tỷ lệ người ở đây vì sensitivity/specificity được ước lượng trên chính tập calibration; đây không phải xác nhận độc lập hay cách cứu một judge yếu. κ không xác định phải FAIL calibration; judge.py trả NaN cho giá trị không xác định. Quyết định floors dùng số chưa làm tròn.

## Audit bất đồng

Đây là phân tích hỗ trợ bởi agent dựa trên reply, nhãn người và note có sẵn trong CSV; chưa phải một vòng gán nhãn người độc lập. Cột “ai đúng” là kết luận theo dữ liệu/rubric công khai. Với case thiếu ticket/ledger gốc, không tự suy diễn thêm sự thật nghiệp vụ.

| # | Case / tiêu chí | Judge | Người | Ai đúng theo bằng chứng hiện có? | Phân tích và hành động sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 / tone | PASS | FAIL | Người, theo note về xưng hô | “Em…nha…check” quá suồng sã theo chuẩn CS lab. Nêu rõ xưng hô chuẩn và ví dụ FAIL dù thân thiện. |
| 2 | H-017 / tone | PASS | FAIL | Người, theo note khách lớn tuổi | Có “Dạ” nhưng “bạn…nha” không phù hợp ngữ cảnh ghi trong note. Rubric cần context người nhận; không suy tuổi chỉ từ reply. |
| 3 | H-029 / tone | PASS | FAIL | Người | “Không cần nhắn thêm” mang tính ngăn khách liên hệ. Chấm toàn câu, từ lịch sự mở đầu không bù giọng ra lệnh. |
| 4 | H-042 / tone | FAIL | PASS | Người | Câu ngắn nhưng lịch sự và đủ thông tin. Không bắt buộc xin lỗi trong mọi reply; không dùng độ dài làm proxy chất lượng. |
| 5 | H-051 / tone | FAIL | PASS | Người, theo note CS cho phép | Từ “refund” được cho phép trong chuẩn lab. Thêm danh sách thuật ngữ hợp lệ; không phạt mọi từ tiếng Anh. |
| 6 | H-063 / tone | PASS | FAIL | Người theo rubric hiện tại; cần tách tiêu chí | “Sẽ hoàn thêm” là cam kết ngoài kết quả hệ thống. Chuyển kiểm chứng cam kết sang factuality/tiền bằng code và ledger; tránh trộn nó vào tone thuần túy. |
| 7 | H-070 / tone | PASS | FAIL | Người theo chuẩn lab | Emoji cười không phù hợp khiếu nại. Thêm quy tắc emoji gắn với bối cảnh, không chỉ kiểm từ lễ phép. |
| 8 | H-081 / tone | FAIL | PASS | Note nguồn nói judge đúng, nhãn người sai; chưa đủ context để xác minh độc lập | Note ghi người đọc nhầm ticket. Giữ CSV nguyên trạng để tái hiện calibration; đưa vào hàng đợi adjudication với ticket gốc. Nếu lỗi là factuality, tách khỏi tone; không tự đổi nhãn từ reply riêng lẻ. |
| 9 | H-088 / tone | FAIL | PASS | Người | Lặp “Dạ” là lỗi gõ nhỏ, không làm câu thiếu tôn trọng. Cho phép lỗi hình thức nhỏ không đổi nghĩa. |
| 10 | H-094 / tone | PASS | FAIL | Người theo chuẩn ngôn ngữ của lab | Tiếng Việt không dấu trong câu trả lời CS. Ghi rõ yêu cầu ngôn ngữ; tách tiêu chí chất lượng ngôn ngữ khỏi phép kiểm tiền. |
| 11 | HL-015 / helpful | PASS | FAIL | Người, dựa note ledger | Reply 55.000 nhưng note ledger 40.000. Cấp ledger cho phép kiểm code; lịch sự không được bù số tiền sai. |
| 12 | HL-016 / helpful | PASS | FAIL | Người, dựa note ledger | Reply 55.000 nhưng ledger 35.000, được bao quanh bởi lời xin lỗi dài. Rubric ưu tiên tính đúng, không thưởng độ dài; thêm cặp ví dụ cùng lỗi với văn ngắn/dài. |
| 13 | HL-020 / helpful | PASS | FAIL | Người, dựa note ledger | Reply 90.000 nhưng ledger 120.000. Sai thiếu tiền cũng FAIL như sai thừa tiền; đối chiếu số chính xác bằng code. |
| 14 | HL-028 / helpful | PASS | FAIL | Người, dựa note ledger | Reply 50.000 nhưng ledger 35.000, nhiều câu xin lỗi lặp. Không để lời văn che lỗi nghiệp vụ; grading factuality chạy trước. |
| 15 | HL-035 / helpful | PASS | FAIL | Người, dựa note ledger | Reply 50.000 nhưng ledger 35.000. Phải kiểm số tiền/claim với ledger, sau đó mới đánh giá mức hữu ích của hướng dẫn. |

Các số tiền trong audit helpful dựa note của từng item CSV, không join order với world Lab 8 vì CSV không cung cấp trial/seed để khẳng định cùng trạng thái ledger.

## Rubric đề xuất sau audit

1. Tone: lịch sự, xưng hô phù hợp context, không ra lệnh/ngăn liên hệ, phù hợp ngôn ngữ và ngữ cảnh khiếu nại. Cho phép thuật ngữ nghiệp vụ được duyệt và lỗi gõ nhỏ; không đòi xin lỗi hay câu dài ở mọi case.
2. Factuality: tiền, trạng thái, claim/principal, approval và cam kết phải khớp dữ liệu thực. Tiền/approval luôn dùng code; tone PASS không chứng minh hoàn đúng.
3. Helpfulness: phản hồi đúng nhu cầu và nêu bước tiếp theo khi cần thông tin/xử lý lỗi. Lịch sự đơn thuần không đủ; ví dụ sai tiền phải FAIL ở phép kiểm factuality.
4. Dùng ví dụ đối lập ngắn/dài, có/không xin lỗi, thuật ngữ cho phép, sai tiền tăng/giảm. Sau khi sửa rubric, thu nhãn người mới và calibration lại trước khi cho judge mới vào gate.

Chưa sửa replay hoặc tuyên bố rubric mới đã tăng điểm: không có lần gọi judge mới trong M2.

## Giới hạn và bước tiếp theo

- Hai CSV đều công khai, 100 item mỗi tập; audit và calibration dùng cùng dữ liệu, chưa có held-out mới.
- Nhãn người không tuyệt đối đúng (H-081); cần adjudication và lưu phiên bản, không sửa lặng lẽ dữ liệu gốc.
- Helpful có dấu hiệu thiên về lời văn: nhiều câu dài lịch sự nhưng sai tiền vẫn PASS. Muốn đo mức thiên lệch phải có thí nghiệm đối chứng mới, chưa kết luận quan hệ nhân quả từ CSV này.
- Tỷ lệ lỗi hiệu chỉnh phụ thuộc sensitivity/specificity còn đúng trên phân bố mới; không đảm bảo chuyển sang model/user thật.
- M3 bổ sung metric FM-08 đọc reply và ledger. Không dùng judge helpful hiện tại thay phép kiểm đó.

## Tái hiện

Chạy từ src/ sau khi kích hoạt .venv:

```powershell
python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10
# Kỳ vọng exit 0, PASS floors
python -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5
# Kỳ vọng exit 1, FAIL floors — đây là kết quả đúng của M2
python -m pytest -q -m student -o addopts= tests/test_lab9_stats.py -k 'not paired_bootstrap'
python -m pytest -q -m student -o addopts= tests/test_lab9_judge.py
```

Hai test paired_bootstrap trong test_lab9_stats.py thuộc M4, chưa thực hiện ở M2. Trên máy hiện tại có thể cần --basetemp trỏ tới thư mục mới trong .venv vì thư mục pytest temp mặc định bị khóa quyền.
