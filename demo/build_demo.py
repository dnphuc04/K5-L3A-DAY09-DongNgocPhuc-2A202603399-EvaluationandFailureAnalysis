"""Build a self-contained Vietnamese teaching demo from local Lab 9 evidence."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from lab9.stats import paired_bootstrap


def read_report(name):
    return json.loads((ROOT / "src/reports" / f"{name}.json").read_text(encoding="utf-8"))


def calibration(name):
    with (ROOT / "src/data/eval" / name).open(encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    tp = sum(r["human"] == "FAIL" and r["judge"] == "FAIL" for r in rows)
    fp = sum(r["human"] == "PASS" and r["judge"] == "FAIL" for r in rows)
    fn = sum(r["human"] == "FAIL" and r["judge"] == "PASS" for r in rows)
    tn = len(rows) - tp - fp - fn
    n = len(rows)
    po = (tp + tn) / n
    pe = ((tp + fn) * (tp + fp) + (tn + fp) * (tn + fn)) / n**2
    return dict(n=n, tp=tp, fp=fp, fn=fn, tn=tn,
                precision=tp / (tp + fp), recall=tp / (tp + fn), kappa=(po - pe) / (1 - pe))


GLOSSARY = {
    "test": ["Test / unit test / pytest", "Test là phép kiểm tự động có điều kiện kỳ vọng. Unit test kiểm một phần logic nhỏ; pytest là công cụ chạy test Python. Test xanh xác nhận điều kiện đã viết được đáp ứng, không chứng minh đã bao phủ mọi lỗi ẩn."],
    "spec": ["Metric spec / version", "Bản cấu hình định nghĩa metric, cách tính và ngưỡng chặn. Version là mã phiên bản: eval-set version đổi khi dữ liệu/nhãn thay đổi; metric-spec version đổi khi thước đo hoặc ngưỡng thay đổi. V2 hiện dùng metric spec 2.1."],
    "passrate": ["pass_rate", "Tỷ lệ trial được grader tổng của Lab 8 đánh PASS: số trial PASS / tổng trial đã chấm. Tiêu chí đó không bao phủ mọi lỗi mới; FM-08 có thể xảy ra dù pass_rate=1."],
    "passfive": ["pass_5", "Tỷ lệ item có tất cả các seed quan sát đều PASS. Với đúng 5 seed, nó trùng pass^5 trên mẫu này; không phải lời bảo đảm 5 lần tương lai đều đúng."],
    "toolsstack": ["NumPy / SciPy / pydantic-evals / PyYAML", "NumPy xử lý mảng số, SciPy cung cấp phép bootstrap, pydantic-evals tổ chức Dataset/Case/Evaluator để chạy đánh giá, PyYAML đọc cấu hình YAML. Chúng là dependencies, không phải các model được gọi."],
    "rng": ["RNG / percentile", "RNG là bộ sinh số ngẫu nhiên; seed 2027 giúp tái hiện việc resample. Percentile bootstrap lấy các phân vị từ phân bố chênh lệch được resample; với CI 95%, hai đầu tương ứng mức 2,5% và 97,5%."],
    "artifact": ["Artifact / report / row", "Artifact là sản phẩm sinh ra khi chạy, như trace hoặc report. Report là báo cáo gồm metadata, rows và metrics tổng hợp. Trong report, mỗi row ghi một trial item@seed và các grade của nó."],
    "registry": ["GRADERS / đăng ký grader", "GRADERS là dictionary nối mã metric trong spec với lớp Python chấm metric đó. Thêm code grader nhưng chưa đăng ký hoặc chưa đưa metric vào spec thì harness chưa dùng nó để chấm."],
    "significance": ["no_significant_drop", "Cờ trong spec yêu cầu chặn nếu khoảng tin cậy của PR−baseline nằm hoàn toàn dưới 0. Điều này khác với ngưỡng min tuyệt đối; gate có thể chặn vì một trong hai điều kiện."],
    "agent": ["Agent", "Chương trình nhận yêu cầu, tra dữ liệu/chính sách, chọn bước xử lý và gọi công cụ. Trong lab, agent xử lý yêu cầu hoàn tiền; host mới có quyền ghi tiền."],
    "host": ["Host", "Lớp thực thi có quyền kiểm tra phê duyệt, giới hạn và ghi ledger. Agent đề xuất; host quyết định có thực hiện tác động hay không. Host không tự tính lại entitlement trong cấu hình lab."],
    "repo": ["Repo / repository", "Thư mục dự án được Git quản lý, gồm code, dữ liệu, tài liệu và lịch sử thay đổi. Repo nộp bài hiện tại là Lab 9; package Lab 8 nằm bên trong src/."],
    "package": ["Package", "Nhóm module Python có thể import. lab8 và lab9 là hai package ngang hàng trong src/, không phải hai repo lồng nhau."],
    "dependency": ["Dependency", "Thư viện mà chương trình cần để chạy, ví dụ NumPy, SciPy, PyYAML và pydantic-evals. Chúng được cài vào môi trường riêng .venv."],
    "venv": [".venv / virtual environment", "Môi trường Python riêng của repo, chứa interpreter và thư viện đã cài. Nó giúp tránh trộn dependencies của các dự án."],
    "smoke": ["Smoke test", "Kiểm tra nhanh những điều kiện tối thiểu: import được thư viện, thấy package Lab 8 và các file dữ liệu. M0 PASS chưa có nghĩa logic hoàn tiền đã đúng."],
    "mock": ["MockLLM", "Mô hình ngôn ngữ giả lập bằng code với hành vi có thể tái hiện. Không gọi model thật, không cần API key; kết quả không đại diện cho chất lượng production."],
    "llm": ["LLM", "Large Language Model: mô hình ngôn ngữ lớn. Với model thật, cùng đầu vào có thể cho kết quả khác nhau; lab dùng MockLLM để kiểm tra offline."],
    "offline": ["Offline", "Thực hiện phép đánh giá mà không cần gọi dịch vụ model bên ngoài. Bản HTML này cũng không dùng thư viện, phông chữ hay tài nguyên mạng."],
    "api": ["API key", "Khóa xác thực để gọi dịch vụ qua API (giao diện cho chương trình giao tiếp). Bài lab không cần khóa vì dùng MockLLM và verdict đã lưu."],
    "eval": ["Evaluation / eval", "Quá trình chạy các tình huống kiểm tra và đo chất lượng bằng tiêu chí đã định nghĩa, thay vì chỉ nhìn demo thành công."],
    "evalset": ["Eval set", "Bộ các tình huống dùng để đánh giá. v1 có 14 item; v2 có 28 item, gồm 14 item cũ và 14 item adversarial."],
    "item": ["Item", "Một tình huống trong eval set. Một item thường gắn với một claim, có mã E-xxx và metadata; không chứa đáp án inline."],
    "claim": ["Claim", "Một yêu cầu hoàn tiền có mã C-xxx. Claim tham chiếu principal, order, ticket và approval; nhiều claim có thể liên quan cùng đơn hàng."],
    "seed": ["Seed", "Số dùng để điều khiển một lần chạy có thể tái hiện. Trong MockLLM, seed còn quyết định khi nào lỗi gài sẵn bật lên; không đồng nghĩa với một người dùng mới."],
    "trial": ["Trial", "Một lần chạy cho một item với một seed. v1: 14 item × 5 seed = 70 trial; v2: 28 × 5 = 140 trial."],
    "label": ["Label / nhãn đáp án", "Kết quả đúng được kỳ vọng cho claim: trạng thái, tiền đề xuất, tiền thực ghi và các chuỗi bị cấm. Label được lưu riêng với item để tránh lộ đáp án."],
    "inline": ["Inline label", "Đặt đáp án ngay trong item đầu vào. Lab cấm cách này để tách đề bài khỏi đáp án và tránh phép đánh giá bị đánh lừa."],
    "jsonl": ["JSONL / JSON", "JSON biểu diễn dữ liệu bằng object, array, số và chuỗi. JSONL lưu mỗi dòng là một object JSON độc lập, tiện quản lý danh sách item."],
    "yaml": ["YAML", "Định dạng cấu hình dễ đọc, dùng thụt dòng. metric_spec.yaml khai báo metric, ngưỡng, seed và cách bootstrap; không phải báo cáo kết quả."],
    "trace": ["Trace", "Dấu vết quá trình agent chạy: các sự kiện handoff, tra dữ liệu, quote, proposal, override và reply. Đọc trace giúp tìm bước sai đầu tiên."],
    "event": ["Event", "Một sự kiện có kind (loại) và payload (nội dung) trong trace. Số event trong tài liệu được đếm từ 1."],
    "trajectory": ["Trajectory", "Toàn bộ chuỗi bước agent đi qua trong một trial. Kiểm trajectory giúp thấy lỗi quyết định, kể cả khi kết quả cuối tình cờ đúng."],
    "taxonomy": ["Failure taxonomy", "Bảng phân loại các kiểu lỗi có tên, định nghĩa, layer, bằng chứng và cách đo. Nó giúp biến nhận xét “agent sai” thành lỗi cụ thể có thể kiểm tra."],
    "fm": ["FM / failure mode", "Một kiểu lỗi cụ thể. FM-03 là tin ticket hơn DB; FM-08 là reply báo tiền khác ledger. FM là mã phân loại, không phải điểm số."],
    "layer": ["Layer", "Lớp phát sinh lỗi: model/prompt (hướng dẫn cho model), tool/schema (công cụ/cấu trúc dữ liệu), retrieval (tra cứu), orchestration/state (điều phối/trạng thái), guardrail/approval (rào chắn/phê duyệt)."],
    "provenance": ["Provenance", "Thông tin nguồn gốc của item/nhãn: lấy từ đâu, matrix_id, trace liên quan, ai gán nhãn và cách kiểm lại. Dùng để truy lại bằng chứng."],
    "anchor": ["Anchor", "Trace mẫu bắt buộc để giảng viên đối chiếu mã FM và bước sai đầu tiên với đáp án riêng. Chưa có xác nhận đúng danh sách 5 anchor; các ví dụ hiện tại chỉ là case công khai đã chọn."],
    "regtest": ["Regression test", "Test giữ lại một tình huống từng gây lỗi để bảo đảm lần sửa sau không làm lỗi đó quay lại. Test có thể xanh khi nó xác nhận đúng rằng bản lỗi FAIL và bản sửa PASS."],
    "judge": ["Judge", "Bộ chấm dựa vào đánh giá ngôn ngữ, chẳng hạn tone hoặc helpfulness. Judge cũng có thể sai, nên phải đo độ tin cậy trước khi dùng làm gate."],
    "replay": ["Replay", "Phát lại kết quả đã lưu thay vì gọi model mới. M2 đọc nhãn human/judge có sẵn trong CSV, vì vậy sửa rubric trong tài liệu chưa tạo ra verdict mới."],
    "csv": ["CSV", "Bảng dữ liệu văn bản, mỗi dòng là một bản ghi và các cột được phân cách. CSV M2 chứa reply, human, judge và note."],
    "calibration": ["Calibration", "Kiểm định judge bằng cách so verdict với nhãn người và đo κ, Precision, Recall. Trong lab, đây là đánh giá mức đồng thuận/chất lượng phân loại, không phải hiệu chỉnh xác suất model."],
    "verdict": ["Verdict / PASS / FAIL", "Kết luận của một phép chấm. PASS là đạt tiêu chí, FAIL là không đạt. Riêng metric safety như approval_bypass, True lại có nghĩa phát hiện vi phạm; không thể coi mọi True đều là tốt."],
    "confusion": ["Confusion matrix", "Ma trận bốn loại kết quả khi coi FAIL là lớp dương: TP tìm đúng lỗi; FP báo lỗi nhầm; FN bỏ sót lỗi; TN xác nhận đúng trường hợp đạt."],
    "precision": ["Precision", "TP/(TP+FP): trong những case judge báo FAIL, bao nhiêu case thật sự FAIL theo nhãn người. Precision cao không đảm bảo judge tìm được nhiều lỗi."],
    "recall": ["Recall", "TP/(TP+FN): trong tất cả case thật sự FAIL theo người, judge tìm được bao nhiêu. Helpful có Recall 0,3 nghĩa là chỉ tìm được 30% lỗi."],
    "kappa": ["Cohen’s κ / kappa", "(pₒ−pₑ)/(1−pₑ), đo mức đồng thuận sau khi trừ phần đồng thuận kỳ vọng từ phân bố nhãn. κ=1 là hoàn toàn đồng thuận; κ=0 ngang mức kỳ vọng đó. κ không xác định thì calibration FAIL."],
    "rg": ["Rogan–Gladen", "Ước lượng tỷ lệ lỗi sau khi tính đến sai số judge: (p quan sát + specificity − 1)/(sensitivity + specificity − 1), chặn về [0,1]. Không làm judge yếu trở thành phù hợp cho gate."],
    "sensitivity": ["Sensitivity / specificity", "Sensitivity là tỷ lệ tìm đúng lỗi, bằng Recall khi FAIL là lớp dương. Specificity = TN/(TN+FP), là tỷ lệ xác nhận đúng các case thực sự đạt."],
    "audit": ["Audit", "Đọc lại các trường hợp bất đồng, xác định bằng chứng nghiêng về ai và đề xuất sửa rubric. Audit hiện tại do agent hỗ trợ từ dữ liệu công khai, chưa phải vòng gán nhãn người độc lập."],
    "rubric": ["Rubric", "Bộ tiêu chí chấm rõ điều kiện đạt/không đạt và ví dụ. Rubric của bài còn chỉ bảng điểm Core 60, Advanced 25, Expert 15; test xanh không tự bảo đảm được chấm đủ 100 điểm."],
    "tone": ["Tone / helpfulness", "Tone là giọng điệu, độ lịch sự và cách xưng hô. Helpfulness là mức hữu ích của phản hồi. Lời văn lịch sự hoặc dài không thể bù cho tiền sai."],
    "grader": ["Grader / evaluator", "Đoạn code hoặc bộ chấm đánh giá một tiêu chí trên trial và label. Grader tiền/approval trong bài luôn dùng code, không giao judge ngôn ngữ quyết định."],
    "ledger": ["Ledger", "Sổ ghi nhận khoản hoàn tiền thực sự đã được host thực hiện. Đây là nguồn để kiểm tiền đã di chuyển, không lấy câu trả lời của agent làm bằng chứng thanh toán."],
    "proposal": ["Proposal / entitlement", "Entitlement là mức được hưởng theo policy; proposal là số agent đề xuất cho host. Khoản mới thực ghi có thể thấp hơn proposal vì cap hoặc khoản đã hoàn trước đó."],
    "approval": ["Approval", "Sự kiện phê duyệt do host cung cấp, phải đúng claim, trạng thái và thời hạn. Approval hợp lệ chưa chứng minh agent tính entitlement đúng."],
    "bypass": ["ApprovalBypass", "Grader báo vi phạm nếu có khoản hoàn khi approval không hợp lệ, hoặc có ledger row dưới claim không được giao. Reply nói “đã hoàn” nhưng host chặn tiền không tự động là side effect bypass."],
    "metric": ["Metric", "Đại lượng đo một khía cạnh chất lượng: pass_rate, tiền đúng, số lần lộ secret… Phải biết chiều tốt/xấu và ngưỡng của từng metric."],
    "safety": ["Safety / capability / system", "Safety đo vi phạm an toàn, thường cần bằng 0. Capability đo khả năng làm đúng việc. System đo vận hành như cost_per_success. Trong spec có metric chỉ theo dõi, không chặn merge."],
    "threshold": ["Threshold / floor", "Ngưỡng để quyết định đạt: min là sàn tối thiểu, max là trần tối đa. Ví dụ reply_amount_correct min=1 yêu cầu 100%; approval_bypass max=0 yêu cầu không vi phạm."],
    "detection": ["Detection của M3", "Trong trial seeded_regression bị pass_rate đánh FAIL, tỷ lệ có ít nhất một grader khác cũng chỉ ra lỗi. Không phải tỷ lệ mọi trial được gọi là lỗi và cũng không chỉ là số test unit xanh."],
    "falsealarm": ["False alarm / báo nhầm", "Một trial fixed đúng nhưng bị ít nhất một grader giải thích lỗi đánh dấu sai. M3 yêu cầu ≤10%; kết quả hiện tại 0/70. Trên scorecard, báo nhầm tính theo variant trung thực bị gate chặn."],
    "variant": ["Variant / shape", "Một biến thể agent hoặc cách tổ chức agent. fixed là bản sửa; honest_refactor đổi lời văn/đường đi nhưng giữ hành vi đúng; các tên regression là biến thể có lỗi cố ý."],
    "regression": ["Regression", "Sự giảm chất lượng so với phiên bản tham chiếu. seeded_regression có lỗi rõ; slice_regression chỉ lỗi ở nhóm nhỏ; flaky_regression lỗi chập chờn theo seed."],
    "baseline": ["Baseline", "Báo cáo mốc để so sánh, trong bài sinh từ shape swarm. v1 và v2 cần baseline riêng vì dùng eval set khác nhau; bản nộp cần commit và bảo vệ baseline."],
    "paired": ["Paired comparison", "So hai phiên bản trên cùng item, lấy trung bình seed cho mỗi item rồi ghép đúng cặp. Nhờ vậy khác biệt độ khó item không bị nhầm thành hiệu ứng phiên bản."],
    "bootstrap": ["Paired bootstrap", "Lấy mẫu lại các cặp item có hoàn lại nhiều lần để ước lượng khoảng tin cậy của chênh lệch. Bài dùng SciPy percentile: chọn hai đầu phân vị 2,5% và 97,5% của 1.000 kết quả lấy mẫu lại, với bộ sinh số ngẫu nhiên (RNG) seed 2027."],
    "ci": ["CI 95% — khoảng tin cậy", "Khoảng được thủ tục bootstrap ước lượng cho chênh lệch PR−baseline. Theo quy tắc lab, CI hoàn toàn dưới 0 ⇒ giảm có ý nghĩa. CI chạm 0 không chứng minh hai bản tương đương; nó chưa đủ bằng chứng giảm theo phép kiểm này."],
    "delta": ["Δ / delta", "Chênh lệch metric = giá trị PR − baseline. Với metric càng cao càng tốt, Δ âm là giảm; −0,271 tương đương giảm khoảng 27,1 điểm phần trăm, không phải giảm tương đối 27,1%."],
    "gate": ["Gate / blocking", "Cổng tự động quyết định cho qua hoặc chặn thay đổi. Metric blocking có quyền chặn; metric theo dõi chỉ cảnh báo. Gate PASS trong máy chưa đồng nghĩa GitHub đã merge hoặc release."],
    "exit": ["Exit code", "Mã chương trình trả khi kết thúc: gate exit 0 là cho qua, exit 1 là chặn. Lệnh traps exit 0 lại nghĩa là nó đã xác nhận mọi trap bị gate chặn. Phải đọc đúng chương trình và lý do, không chỉ nhìn số."],
    "harness": ["Eval harness", "Khung chạy thống nhất: chuẩn bị dữ liệu, chạy các case, gọi graders và tổng hợp report. Bài dùng pydantic-evals, mỗi case là một item@seed."],
    "runid": ["Run ID / SHA", "Run ID là mã báo cáo/lần chạy; SHA là dấu vân tay hash của dữ liệu. Run ID hiện không chứa seeds nên hai run cùng shape/ngày/SHA có thể trùng; cần xem cả tên file và manifest.seeds."],
    "manifest": ["Manifest", "Phần metadata mô tả report: eval-set SHA, số item, seed, phiên bản spec, backend và Python. Nó giúp kiểm báo cáo có cùng điều kiện đánh giá hay không."],
    "cicd": ["CI — tích hợp liên tục", "Continuous Integration: các job tự chạy test và gate trên GitHub Actions khi mở PR hoặc chạy tay. Khác với CI 95% (confidence interval) trong thống kê."],
    "pr": ["PR / merge / commit / push", "Commit ghi một phiên bản thay đổi vào Git; push đưa commit lên remote. PR (pull request) đề nghị ghép nhánh; merge thực hiện việc ghép. Bài hiện chưa commit/push/mở PR."],
    "evalcard": ["Eval card / PRD", "Eval card tóm tắt bộ đo, kết quả, phiên bản và giới hạn. PRD (Product Requirements Document) v1.1 bổ sung định nghĩa chạy đúng, phạm vi pilot và trách nhiệm khi gate chặn."],
    "pilot": ["Pilot / production", "Pilot là phạm vi thử nghiệm có giới hạn. Production là môi trường dùng thật. Bài mới là sandbox offline với tiền giả lập, chưa đo chất lượng trên người dùng hay tiền thật."],
    "adversarial": ["Adversarial pack", "Bộ tình huống cố ý gây khó: ticket giả quyền admin, nêu policy cũ, yêu cầu cộng khoản hoặc truy cập dữ liệu principal khác. Mục tiêu là thử ranh giới, không chỉ case dễ."],
    "slice": ["Slice", "Một nhóm con item theo đặc điểm cố định. money_movement gồm item có nhãn refund_vnd>0; adversarial gồm item từ pack; denial gồm item có nhãn denied."],
    "mapping": ["FM mapping", "Bảng nối tên cơ chế tấn công với mã FM trong taxonomy, ví dụ ticket_over_db → FM-03. Mapping không sửa đầu vào hoặc nhãn của pack."],
    "principal": ["Principal / scope", "Principal là danh tính đang được cấp quyền, scope là phạm vi dữ liệu/hành động được phép. Claim cùng order không tự tạo quyền đọc dữ liệu hoặc hoàn tiền cho người/claim khác."],
    "policy": ["Policy / clause", "Policy là chính sách; clause là điều khoản cụ thể. Chỉ clause áp dụng tại thời điểm đánh giá mới được dùng; quy tắc stacking của lab lấy max khoản đủ điều kiện, không cộng tất cả."],
    "aa": ["A/A", "So cùng một agent qua hai bộ seed, thay vì so hai phiên bản khác nhau. Dùng để xem chênh lệch quan sát khi chưa có thay đổi hành vi. Một A/A bằng 0 trên MockLLM chưa ước lượng được nhiễu model thật."],
    "passat": ["pass@k", "Xác suất ước lượng có ít nhất một lần PASS khi chọn k lần từ n trial, trong đó c lần PASS: 1−C(n−c,k)/C(n,k). Mỗi item tính riêng rồi lấy trung bình."],
    "passhat": ["pass^k / pass_hat_k", "Xác suất ước lượng cả k lần đều PASS khi chọn không hoàn lại: C(c,k)/C(n,k). Với n=k=5, một item lỗi một lần đã có pass^5=0; đây là chỉ số độ ổn định."],
    "comb": ["C(n,k) / tổ hợp", "Số cách chọn k phần tử từ n phần tử mà không phân biệt thứ tự. n là số trial đã chạy; c là số trial PASS; k là số lần muốn xét. Cần n≥1, 0≤c≤n và 1≤k≤n, tất cả là số nguyên."],
    "noise": ["Noise band / dải nhiễu", "Vùng dao động của kết quả do ngẫu nhiên hoặc điều kiện chạy dù agent không đổi. Cần lặp A/A đủ nhiều để ước lượng; sàn quá sát vùng chạy trung thực có thể chặn nhầm."],
    "flaky": ["Flaky", "Hành vi không ổn định: cùng tình huống có lần đúng, lần sai. Variant flaky_regression bật lỗi làm tròn ở một seed trong năm seed công khai."],
    "integrity": ["Integrity", "Kiểm tính toàn vẹn và nhất quán của bằng chứng: đủ rows, đúng item/seed/slice, không mất grade và tổng điểm khớp rows. Nó không chứng minh dữ liệu là thật nếu toàn bộ bằng chứng lẫn nguồn tin cậy đều bị giả."],
    "ratchet": ["Ratchet", "Quy tắc chỉ siết, không nới thước đo trên cùng eval-set version: không hạ min, nâng max, bỏ blocking hay xóa metric/slice. Cần so với base-spec lấy từ commit gốc tin cậy."],
    "trap": ["Trap", "Report hoặc spec cố ý bị chỉnh để che lỗi, dùng thử gate. Khác variant: variant làm agent xử lý sai; trap làm bằng chứng đánh giá trông đẹp giả tạo."],
    "nan": ["NaN / None / evaluator failure", "NaN là giá trị số không hợp lệ; None là thiếu kết quả; evaluator failure là grader bị lỗi. Không được bỏ những giá trị này khỏi trung bình để làm điểm tăng."],
    "cartesian": ["Cartesian product / tích Descartes", "Tập tất cả cặp item × seed phải có trong report. V2 cần 28×5=140 cặp duy nhất; 140 dòng vẫn chưa đủ nếu có dòng trùng và cặp khác bị mất."],
    "aggregate": ["Aggregate / summary", "Các số tổng hợp từ rows: trung bình pass_rate, tổng số vi phạm safety, pass@k/pass^k và cost. Gate M7 tính lại chúng để phát hiện report sửa tổng điểm nhưng giữ rows lỗi."],
    "refactor": ["Honest refactor", "Đổi cách viết hoặc đường xử lý mà không đổi kết quả nghiệp vụ đúng. Gate cần cho qua để tránh coi mọi thay đổi câu chữ/tool call là lỗi."],
    "hidden": ["Hidden tests / held-out", "Hidden tests là bộ kiểm giảng viên không công khai, chưa được chạy ở đây. Held-out là dữ liệu độc lập, không dùng để phát triển/điều chỉnh grader; CSV công khai hiện tại chưa phải held-out mới."],
    "idempotency": ["Idempotency / cap", "Idempotency ngăn một tác động được thực hiện lặp ngoài ý muốn. Cap giới hạn khoản ghi theo số được duyệt, số đã trả và tổng theo order, có trừ tiền đã hoàn trước đó."],
    "secret": ["Secret / canary", "Secret là dữ liệu bí mật. Canary là chuỗi giả lập được cài vào dữ liệu để phát hiện lộ lọt khi nó xuất hiện trong trace/artifact; không phải khóa thật."],
    "db": ["DB / SQLite", "DB là cơ sở dữ liệu; SQLite là hệ quản trị dùng file trong bài. Mỗi trial chạy trên database tạm mới để tránh trial trước làm thay đổi kết quả trial sau."],
    "tool": ["Tool call / handoff / override", "Tool call là gọi công cụ; handoff là giao nhiệm vụ với dữ liệu và quyền hạn; override là ghi đè fact đã có. model_override là một loại event, nhưng không thấy event này chưa chứng minh không có lỗi ghi đè im lặng."],
}


STAGES = [
dict(id="M0", name="Dựng nền đánh giá", subtitle="Trước khi đo đúng sai, cần chạy được phép đo.", group="Chuẩn bị", status="Đạt tại máy", terms=["repo","package","dependency","venv","smoke","mock","evalset","item","seed","trial","label","inline","jsonl","db"],
 question="Đã có cùng một môi trường và bộ đầu vào để chạy lại chưa?",
 requirements=["Ghép nền [[package|Lab 8]] vào [[repo|repo Lab 9]], giữ nguyên code agent Lab 8.","Cài [[dependency|dependencies]], chạy [[smoke|smoke test]] và tạo [[evalset|eval set v1]].","Giữ [[label|nhãn đáp án]] riêng, không đặt [[inline|inline label]] trong item."],
 outputs=["Dòng xác nhận <code>M0 PASS</code>.","<code>eval_set_v1.jsonl</code>: 14 [[item|item]]; <code>labels_v1.json</code>: 14 nhãn.","Năm [[seed|seed]] cố định 11, 22, 33, 44, 55 → 70 [[trial|trial]] khi đánh giá v1."],
 done=["Chép code nền, dữ liệu và cấu hình còn thiếu vào repo Lab 9; <code>src/lab8/</code> và <code>src/lab9/</code> nằm ngang hàng.","Tạo [[venv|.venv]] riêng, cài thư viện và chạy smoke thành công.","Chạy builder chính thức để sinh item/label. Không dùng [[api|API key]]; toàn bộ đánh giá dùng [[mock|MockLLM]]."],
 example="Một item C-002 chạy với seed 11 là một trial. Cùng item chạy thêm seed 22 là trial khác, không phải item mới.",
 files=[("../src/requirements-lab9.txt","Thư viện Lab 9"),("../src/data/eval/eval_set_v1.jsonl","Eval set v1"),("../src/data/eval/labels_v1.json","Nhãn v1")], command="python -m lab9.smoke\npython -m lab9.evalset --build", widget="environment"),
dict(id="M1", name="Gọi đúng tên lỗi", subtitle="Từ “agent bị nhầm” đến một bước sai có bằng chứng.", group="Core", status="Đạt local · còn anchor", terms=["taxonomy","fm","layer","trace","event","claim","provenance","anchor","regtest","db","tool","policy","secret"],
 question="Lỗi thuộc kiểu nào và bắt đầu sai ở event nào?",
 requirements=["Viết [[taxonomy|taxonomy]] có ≥5 [[fm|failure mode]], mỗi lỗi có định nghĩa, [[layer|layer]], bằng chứng và grader dự kiến.","Gắn mã FM cho eval set, ghi đủ [[provenance|provenance]] và chạy check không lỗi.","Phân tích 5 [[anchor|anchor]] bắt buộc; ghi một [[trace|trace case]] có [[regtest|regression test]]."],
 outputs=["<code>failure_taxonomy.md</code>, item đã có <code>failure_modes</code>.","Một case nêu số [[event|event]] sai đầu tiên, bản đối chứng và test tái hiện.","<code>evalset --check</code> trả 0 problem; danh sách anchor phải đối chiếu giảng viên."],
 done=["Mô tả 8 FM có trace lỗi: lộ secret, bỏ qua từ chối, tin ticket, tính sai, trừ hai lần, dùng clause cũ, ghi claim khác, reply sai tiền.","Gắn mã và nguồn gốc cho đủ 14 item; builder giữ annotation khi chạy lại.","C-002: event 2 đọc [[db|DB]] là 2 ngày, event 3 [[tool|model_override]] thành 5 ngày → hoàn sai 20.000đ; <code>fixed</code> giữ DB và không hoàn.","Đã thêm test đối chứng seed 11 và 55. FM-09 có [[principal|principal]] controls, chưa coi các case chặn đúng là lỗi đã quan sát."],
 example="Reply của C-002 khớp ledger 20.000đ, nhưng chính khoản hoàn đó sai điều kiện. Điểm sai đầu tiên nằm trước reply: event 3 thay fact của DB.",
 note="Chưa được xác nhận đúng danh sách 5 anchor giảng viên chỉ định. Không thể xem phần đối chiếu anchor là hoàn tất chỉ vì đã tự chọn 5 ví dụ.",
 files=[("../docs/failure_taxonomy.md","Taxonomy và coverage"),("../docs/trace_case.md","Trace case C-002"),("../src/tests/test_lab9_m1_trace.py","Regression test")], command="python -m lab9.evalset --check\npython -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11", widget="trace"),
dict(id="M2", name="Chấm lại bộ chấm", subtitle="Judge cũng có thể sai. Đo nó trước khi tin nó.", group="Core", status="Đạt tại máy", terms=["judge","replay","csv","calibration","confusion","precision","recall","kappa","rg","sensitivity","audit","rubric","tone","hidden"],
 question="Judge có đủ đáng tin để đưa vào quyết định chặn hay không?",
 requirements=["Cài [[confusion|confusion matrix]], [[precision|Precision]], [[recall|Recall]], [[kappa|Cohen’s κ]] và [[rg|Rogan–Gladen]].","Đạt sàn calibration: κ ≥0,6; Precision ≥0,8; Recall ≥0,7. κ không xác định phải FAIL.","[[audit|Audit]] ≥5 bất đồng và giải thích vì sao judge <code>helpful</code> không được làm gate."],
 outputs=["Các hàm thống kê qua test và kết quả [[calibration|calibration]] cho cả hai CSV.","Bảng audit có case, verdict người/judge, bằng chứng và hành động sửa [[rubric|rubric]].","Quyết định dùng/loại đúng phạm vi; không biến giọng văn hay thành bằng chứng tiền đúng."],
 done=["Cài đủ hàm; [[verdict|FAIL]] được coi là lớp dương vì mục tiêu là tìm lỗi.","Tone đạt κ=0,757, P=0,857, R=0,8. Helpful chỉ κ=0,375 và R=0,3, bỏ sót 21/30 lỗi dù P=1.","Audit 15 bất đồng, gồm case nhãn người có dấu hiệu sai. Giữ nguyên CSV nguồn; chưa tuyên bố [[replay|replay]] đã cải thiện nhờ rubric mới."],
 example="Precision 100% nghĩa là các lỗi helpful tìm ra đều đúng. Nó vẫn không dùng được làm gate vì chỉ tìm được 9 trong 30 lỗi thật.",
 note="Audit do agent hỗ trợ trên note/reply công khai; chưa có vòng gán nhãn người độc lập hoặc tập held-out mới.",
 files=[("../docs/judge_audit.md","Audit 15 trường hợp"),("../src/lab9/stats.py","Hàm thống kê"),("../src/lab9/judge.py","Calibration replay")], command="python -m lab9.judge --csv data/eval/judge_tone_public.csv --audit 10\npython -m lab9.judge --csv data/eval/judge_helpful_public.csv --audit 5", widget="judges"),
dict(id="M3", name="Đo hành vi, không chỉ lời nói", subtitle="Tiền và phê duyệt phải được chấm bằng code.", group="Core", status="Đạt tại máy", terms=["trajectory","grader","ledger","proposal","approval","bypass","metric","safety","threshold","detection","falsealarm","variant","verdict"],
 question="Grader có tìm đúng lỗi tiền/approval và tránh báo nhầm bản đúng không?",
 requirements=["Cài hai [[grader|grader]] bắt buộc: <code>ApprovalBypass</code> và <code>RefundAmountCorrect</code>.","[[detection|Detection]] ≥80% trace lỗi của <code>seeded_regression</code>; [[falsealarm|báo nhầm]] ≤10% trial của <code>fixed</code>.","Thêm [[metric|metric]] [[gate|blocking]] bắt FM-08: tiền nói trong reply khác [[ledger|ledger]]."],
 outputs=["Hai grader qua test; có metric FM-08 đăng ký trong <code>GRADERS</code> và metric spec.","Kết quả chính thức từ <code>lab9.mutation --detect</code>, không chỉ số unit test PASS.","Report cho thấy lỗi reply được bắt dù grader Lab 8 và tiền trong ledger cùng đúng."],
 done=["ApprovalBypass đọc approval và ledger row ngoài claim; RefundAmountCorrect so tiền thực ghi với nhãn.","Thêm <code>ReplyAmountCorrect</code> so tiền reply với ledger; thêm <code>ProposalAmountCorrect</code> để bắt trừ trước khi ledger=0 vẫn đúng.","Đạt detection 20/20 trace lỗi =100%; báo nhầm 0/70 trial fixed =0%.","FM-08 cô lập: 10/70 reply sai tiền bị bắt; Lab 8 vẫn cho toàn bộ các trial này PASS theo thước đo cũ."],
 example="C-008: proposal 35.000đ, host cap và ghi 20.000đ. Nói “đã hoàn 35.000đ” là FM-08 dù ledger và approval hoàn toàn đúng.",
 note="Swarm Lab 8 không có event reply: metric dùng refund_effects có cấu trúc làm đối chứng, không tuyên bố đã kiểm lời văn chưa được ghi. Parser hiện hỗ trợ mẫu số nguyên VND công khai.",
 files=[("../docs/m3_graders.md","Bằng chứng M3"),("../src/lab9/graders.py","Các grader"),("../src/config/metric_spec.yaml","Ngưỡng v1")], command="python -m lab9.mutation --detect\npython -m pytest -q -m student -o addopts= tests/test_lab9_graders.py tests/test_lab9_reply_amount.py", widget="money"),
dict(id="M4", name="Ra quyết định bằng so sánh cặp", subtitle="Có giảm thật hay chỉ là khác biệt trên mẫu?",
 group="Core", status="Đạt local · CI chờ", terms=["baseline","paired","bootstrap","ci","delta","gate","exit","harness","runid","manifest","cicd","pr","evalcard","pilot"],
 question="Bản mới có giảm chất lượng so với baseline trên cùng item không?",
 requirements=["Cài [[paired|paired]] [[bootstrap|bootstrap]], khoảng tin cậy lệch ≤0,01 so tham chiếu.","Sinh [[baseline|baseline]] từ <code>swarm</code>; <code>fixed</code> phải qua, <code>seeded_regression</code> phải bị chặn ở pass_rate.","Dùng cùng spec/baseline trong [[cicd|CI]], thêm eval vào [[harness|harness map]], hoàn thiện [[evalcard|eval card và PRD v1.1]]."],
 outputs=["Report baseline v1, report fixed/regression có [[runid|run ID]] và [[manifest|manifest]].","Gate [[exit|exit 0]] cho swarm/fixed; [[exit|exit 1]] cho regression, có tên metric bị chặn.","[[ci|CI 95%]] của [[delta|Δ]] = PR−baseline; job GitHub Actions xanh sau commit/push/PR."],
 done=["Cài SciPy bootstrap paired, percentile, 1.000 resample, RNG 2027. Lấy trung bình 5 seed cho từng item trước khi resample item.","Baseline pass_rate=0,9857; fixed=1; seeded_regression=0,7143.","Regression: Δ=−0,271; CI [−0,500; −0,057], khớp tham chiếu. Fixed và baseline tự so đều merge.","Đã sinh eval card/PRD từ report thực; rà workflow và kiểm các bước tương ứng tại máy."],
 example="CI nằm hoàn toàn dưới 0 ⇒ chặn theo no_significant_drop. Nếu CI chạm 0, vẫn có thể chặn vì dưới sàn tuyệt đối; đó là hai điều kiện riêng.",
 note="CI trong thống kê là khoảng tin cậy; CI trong GitHub là tích hợp liên tục. Hiện chưa commit/push/mở PR nên chưa có GitHub Actions run xanh.",
 files=[("../docs/m4_validation.md","Output gate M4"),("../src/reports/baseline_v1.json","Baseline v1"),("../docs/PRD_v1.1.md","PRD v1.1"),("../docs/eval_card.md","Eval card")], command="python -m lab9.gate --pr reports/eval_fixed.json --baseline reports/baseline_v1.json\npython -m lab9.gate --pr reports/eval_seeded_regression.json --baseline reports/baseline_v1.json", widget="compare"),
dict(id="M5", name="Không để trung bình che lỗi", subtitle="Một nhóm nhỏ có thể cần được bảo vệ riêng.", group="Advanced", status="Đạt tại máy", terms=["adversarial","slice","mapping","principal","policy","aggregate","evalset","threshold"],
 question="Một nhóm liên quan tiền có thể sai dù điểm tổng vẫn cao không?",
 requirements=["Ghép [[adversarial|adversarial pack]] vào eval set v2; [[mapping|map cơ chế sang mã FM]]; mỗi FM bị tấn công có ≥3 item trên toàn v2.","Thêm [[slice|slice]] <code>money_movement</code> và <code>adversarial</code> dạng blocking.","Chặn <code>slice_regression</code> qua money_movement khi trung bình còn trên sàn và CI tổng chạm 0."],
 outputs=["28 item v2 và 28 nhãn riêng; baseline v2 mới, không dùng baseline v1 để so chéo.","<code>slice_check</code> tính trung bình theo item trong từng slice, không phụ thuộc tên variant.","Bằng chứng fixed/refactor qua; slice_regression bị chặn đúng nhóm tiền."],
 done=["Giữ 14 item v1, thêm 14 item adversarial và approval trong bộ nhớ; không sửa world Lab 8.","Map đủ tám cơ chế; mỗi FM bị tấn công có 3–6 item. Kiểm v2 báo 0 problem.","Cài money_movement, adversarial và denial cùng sàn 0,90 và no_significant_drop.","Slice regression tổng đạt 93,57%; money_movement chỉ 85% nên gate chặn đúng slice này. [[refactor|Honest refactor]] vẫn qua."],
 example="money_movement được gán theo nhãn refund_vnd>0, không phải agent tự khai có hoàn tiền hay không. Agent không thể né slice bằng cách trả lời denied.",
 note="V2 là eval-set version mới nên có baseline và cấu hình khởi tạo riêng. Từ baseline v2 đã chốt, không được nới ngưỡng cùng version. Nhãn slice bị đổi để che lỗi sẽ được M7 chặn.",
 files=[("../docs/m5_validation.md","Bằng chứng slice"),("../src/config/fm_map.yaml","Mapping FM"),("../src/data/eval/eval_set_v2.jsonl","Eval set v2"),("../src/config/metric_spec_v2.yaml","Spec v2")], command="python -m lab9.evalset --v2 --build\npython -m lab9.gate --pr reports/eval_slice_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml", widget="slices"),
dict(id="M6", name="Đúng một lần hay lần nào cũng đúng?", subtitle="Độ ổn định cần một thước đo khác tỷ lệ trung bình.", group="Advanced", status="Đạt tại máy", terms=["aa","passat","passhat","comb","noise","flaky","seed","hidden"],
 question="Agent có đủ ổn định hay chỉ cần thử nhiều lần mới được một lần?",
 requirements=["Cài [[passat|pass@k]] và [[passhat|pass^k]], từ chối [[comb|(n,c,k)]] không hợp lệ.","Chạy [[aa|A/A]] trên hai bộ seed, giải thích [[noise|dải nhiễu]] và chọn sàn ngoài vùng chạy trung thực quan sát được.","Thêm <code>pass_hat_5</code> blocking, bắt [[flaky|flaky_regression]] và không báo nhầm bản trung thực."],
 outputs=["Estimator đúng trên test công khai, các tổ hợp nhỏ và đầu vào sai.","A/A seeds 11…55 so 66…110; report v2 có pass@k/pass^k, không còn null.","Ngưỡng pass_hat_5 có lý do chọn; scorecard phân biệt regression với refactor."],
 done=["Cài công thức tổ hợp lấy mẫu không hoàn lại; kiểm bằng liệt kê các cách chọn trial và kiểm số nguyên/phạm vi.","A/A cho Δ=0 mọi metric; baseline pass_hat_5=0,8929 trên cả hai bộ seed.","Chốt sàn 0,85, margin 0,0429 dưới mức baseline quan sát; tăng metric_spec_version lên 2.1 và sinh lại report.","Flaky có pass_rate=0,9143 nhưng pass_hat_5=0,5714 <0,85. Fixed/refactor đều pass_hat_5=1 và được merge."],
 example="Một item đúng 4/5 lần: pass@5=1 vì có ít nhất một lần đúng; pass^5=0 vì cả năm lần không đồng thời đúng.",
 note="Chỉ một phép A/A với MockLLM không chứng minh nhiễu model thật bằng 0. Cần nhiều batch độc lập hơn. Năm seed cũng không đảm bảo phát hiện ổn định lỗi chỉ xuất hiện 1/3 seed.",
 files=[("../docs/m6_validation.md","A/A và reliability"),("../src/reports/eval_swarm_aa_v2.json","Report seed đối chứng"),("../src/reports/eval_flaky_regression_v2.json","Report flaky")], command="python -m lab9.mutation --spec config/metric_spec_v2.yaml --aa 66,77,88,99,110\npython -m lab9.mutation --spec config/metric_spec_v2.yaml --baseline reports/baseline_v2.json", widget="reliability"),
dict(id="M7", name="Bảo vệ chính phép đánh giá", subtitle="Một report xanh chỉ có giá trị khi bằng chứng còn nguyên.", group="Expert", status="Đạt tại máy", terms=["integrity","ratchet","trap","nan","cartesian","aggregate","manifest","cicd","hidden","exit"],
 question="Gate có chặn được người làm đẹp report hoặc nới thước đo không?",
 requirements=["Cài [[integrity|integrity_check]]: số hữu hạn, đủ grade, đủ tập [[cartesian|item × seed]], không dòng trùng, không mất lỗi evaluator.","Cài [[ratchet|ratchet]] với base-spec: không nới ngưỡng, bỏ metric/slice hoặc tắt blocking/no_significant_drop cùng version.","Mọi [[trap|trap]] công khai phải khiến gate exit 1 có lý do; mutation đạt 3/3 regression, 0 báo nhầm."],
 outputs=["Bốn output gate CLI: INTEGRITY hoặc RATCHET; lệnh traps tổng kết không trap nào lọt.","Test report xanh bị giả mạo, tính lại [[aggregate|aggregate]] từ rows và đối chứng giữ hành vi đúng.","Workflow lấy spec từ commit gốc của PR, truyền <code>--base-spec</code> và có bước chạy trap."],
 done=["Kiểm cả PR/baseline: thiếu/trùng row, seed đẹp, đổi slice, [[nan|NaN/None]], grader crash; tính lại summary, pass@k/pass^k và cost.","Chặn 4/4 trap công khai và thêm test dòng trùng, evaluator failure trong report xanh, sửa tổng và đổi tag.","Ratchet bảo vệ min/max/max_increase, metric/slice, blocking, significance, grader và cấu hình phép đo.","128 test Lab 9 PASS; scorecard 3/3 regression và 0 báo nhầm. Quiet override không có event cũng bị kiểm tiền/proposal chặn."],
 example="140 dòng không đủ chứng minh v2 đầy đủ: nếu một cặp item@seed bị lặp và một cặp khác mất, tổng dòng vẫn 140. Gate phải kiểm từng cặp duy nhất.",
 note="Base-spec phải đến từ commit tin cậy. Nếu cả rows, totals và baseline đều bị giả đồng bộ, kiểm nhất quán chưa chứng minh được sự thật. Test/trap ẩn chưa chạy; GitHub Actions vẫn cần xác nhận sau push/PR.",
 files=[("../docs/m7_validation.md","Bốn exit code CLI"),("../src/lab9/integrity.py","Kiểm tra report và ratchet"),("../.github/workflows/eval-gate.yml","Workflow CI")], command="python -m lab9.traps --pr reports/eval_slice_regression_v2.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml\npython -m pytest -q -m student -o addopts= -k lab9", widget="traps"),
]


def main():
    extra_terms = {
        "M0": ["test", "toolsstack", "offline"], "M1": ["regtest", "artifact"],
        "M2": ["test", "sensitivity"], "M3": ["test", "spec", "registry", "passrate"],
        "M4": ["rng", "spec", "passrate", "passfive", "significance", "artifact"],
        "M5": ["spec", "refactor", "passrate", "significance"],
        "M6": ["test", "spec", "passrate", "passfive", "noise"],
        "M7": ["test", "spec", "artifact", "significance"],
    }
    for stage in STAGES:
        stage["terms"] += extra_terms[stage["id"]]
    # Catch missing definitions and broken evidence links before building HTML.
    import re
    for stage in STAGES:
        text = " ".join(stage["requirements"] + stage["outputs"] + stage["done"] + [stage["example"]])
        for key in stage["terms"] + re.findall(r"\[\[([^|\]]+)\|", text):
            assert key in GLOSSARY, f"Missing glossary definition: {key}"
        for target, _ in stage["files"]:
            assert (Path(__file__).parent / target).is_file(), target
    v1 = read_report("baseline_v1")
    seeded = read_report("eval_seeded_regression")
    fixed = read_report("eval_fixed")
    spec = __import__("yaml").safe_load((ROOT / "src/config/metric_spec.yaml").read_text(encoding="utf-8"))
    directions = {m["id"]: "max" in m.get("threshold", {}) for m in spec["metrics"] if m["id"] != "pass_rate"}
    flagged = lambda row: any(mid in row and row[mid] is bad for mid, bad in directions.items())
    failed = [r for r in seeded["rows"] if r["pass_rate"] is False]
    comparison = {}
    for name in ("fixed", "seeded_regression"):
        report = read_report(f"eval_{name}")
        per = lambda rep: {item: sum(r["pass_rate"] for r in rep["rows"] if r["item_id"] == item) / 5
                           for item in sorted({r["item_id"] for r in rep["rows"]})}
        a, b = per(report), per(v1)
        comparison[name] = dict(rate=report["metrics"]["pass_rate"],
                                ci=paired_bootstrap(list(a.values()), list(b.values())), run_id=report["run_id"])
    evidence = dict(
        v1=v1["metrics"], base_v2=read_report("baseline_v2")["metrics"],
        slice=read_report("eval_slice_regression_v2")["metrics"], flaky=read_report("eval_flaky_regression_v2")["metrics"],
        tone=calibration("judge_tone_public.csv"), helpful=calibration("judge_helpful_public.csv"),
        detected=sum(map(flagged, failed)), failed=len(failed),
        false_alarms=sum(map(flagged, fixed["rows"])), fixed_trials=len(fixed["rows"]), comparison=comparison,
        sha_v1=v1["manifest"]["eval_set_sha"], sha_v2=read_report("baseline_v2")["manifest"]["eval_set_sha"],
    )
    data = dict(stages=STAGES, glossary=GLOSSARY, evidence=evidence)
    template = (Path(__file__).parent / "template.html").read_text(encoding="utf-8")
    result = template.replace("/*__LAB_DATA__*/", "const DATA = " + json.dumps(data, ensure_ascii=False).replace("</", "<\\/") + ";")
    (Path(__file__).parent / "index.html").write_text(result, encoding="utf-8")
    print(f"Built demo/index.html: {len(STAGES)} stages, {len(GLOSSARY)} glossary entries; data from local reports")


if __name__ == "__main__":
    main()
