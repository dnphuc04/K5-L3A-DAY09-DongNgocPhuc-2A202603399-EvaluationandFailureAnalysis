# Nộp bài (cập nhật theo thông báo Day 09)

Hạn mới: **12:00 trưa 18/11/2026 (UTC+7)**. Giảng viên chấm **nhánh `main` trong repo fork của học viên**. Thông báo này thay thế hạn cũ trong README/RUBRIC/CHECKPOINTS.

Nếu dùng PR, mở `starter/d09` → `main` ngay trong repo fork rồi merge; không mở PR vào repo gốc VinUni-AI20k. Nếu đã nộp link PR trên LMS, giữ nguyên nhánh sau khi merge. Đã nộp link repo/PR thì không cần nộp lại LMS, chỉ cần cập nhật repo trước hạn.

Code, dữ liệu, tài liệu và report bắt buộc phải được commit, push và có trên `main`; file chỉ tồn tại local chưa được tính là đã nộp. `.gitignore` hiện cho phép các report nộp bài; kiểm tra bằng `git ls-files src/reports` sau khi stage/commit. Không sửa tay report.

## Core (nên xong trước 17:00)

Kiểm tra local ngày 17/11/2026: toàn bộ **721 test PASS** bằng `python -m pytest -q -o addopts=`. Fixture khôi phục registry shape sau mỗi test để các variant Lab 9 không ảnh hưởng test hợp đồng Lab 8; không chỉnh code `src/lab8/`. Core/Advanced theo workflow đã lần lượt đạt 116/12 test; gate Core cho `fixed` qua và chặn `seeded_regression`; mutation v2 3/3, 0 báo nhầm; A/A mọi Δ=0 và 4/4 trap công khai bị chặn. Chưa chạy bộ chấm ẩn hoặc xác nhận GitHub Actions xanh. Bằng chứng chi tiết: `docs/m3_graders.md`, `docs/m4_validation.md` đến `docs/m7_validation.md`.

- [ ] `src/lab9/{stats,graders,evalset}.py` đã hoàn thành TODO M1–M4
- [ ] `src/data/eval/eval_set_v1.jsonl` có `failure_modes`, `labels_v1.json` tách riêng
- [ ] `docs/failure_taxonomy.md`, `docs/trace_case.md` (1 case + regression test), `docs/judge_audit.md`, `docs/eval_card.md`, `docs/PRD_v1.1.md`
- [ ] `src/reports/baseline_v1.json`, `eval_fixed.json`, `eval_seeded_regression.json` (sinh bằng script)
- [ ] `harness_map.yaml` có section `eval` (mẫu: `src/harness_map.eval.yaml`)
- [ ] Job `eval-gate` xanh; dán output gate exit 1 của `seeded_regression` vào mô tả PR

## Advanced / Expert (tới 23:59)
- [ ] `config/fm_map.yaml`, `config/metric_spec_v2.yaml` (slices, `pass_hat_5`, metric FM-08), `stats.pass_at_k/pass_hat_k`, `gate.slice_check`, `gate.integrity_check`
- [ ] `src/data/eval/eval_set_v2.jsonl` + `labels_v2.json` (sinh bằng `evalset --v2 --build`)
- [ ] `src/reports/baseline_v2.json` (sinh bằng script) → job `eval-gate-v2` chạy và xanh
- [ ] Mô tả PR: output `lab9.mutation` (scorecard + `--aa`) và 4 dòng `exit 1` của các trap
- [ ] `docs/eval_card.md` thêm mục v2: ngưỡng chọn từ A/A, slice nào bắt lỗi nào, và giới hạn cỡ mẫu (bug 1/3 seed không phát hiện ổn định với 5 seed)
