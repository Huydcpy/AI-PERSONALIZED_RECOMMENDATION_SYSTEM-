# Review tích hợp cuối — Day 5

**Ngày:** 12/11/2026  
**Người review:** Huy  
**Base:** `main` tại `2104c8b` (sau PR #21)  
**Release:** `v1.0.1`  
**Closeout:** [day5_closeout.md](day5_closeout.md)

## 1. Phạm vi review

- PR #18 — Day 4 finalization.
- PR #19 — README, screenshot, demo script, slide outline.
- PR #20 — báo cáo cuối, eval, review, biểu đồ, README.
- PR #21 — xác minh số liệu, biểu đồ, Q&A của Phong.
- PR closeout — chốt trạng thái, release `v1.0.1`.
- Bộ số liệu, screenshot, biểu đồ, tài liệu và kiểm chứng tái lập.

Không nằm trong phạm vi: thêm model, metric, dependency, tuning hyperparameter/trọng số/threshold/K trên test.

## 2. PR #18 — Day 4 finalization

- Branch `docs/day4-finalize-day5-plan`, commit `d2b0151`, `90e8f00`.
- Điền kết quả Day 4, tạo `notes/day4_report.md`, thêm CI `run_svd_eval.py` và `smoke_svd_hybrid.py`, thêm task plan Day 5.
- CI xanh; merge tại `066bcd8`.
- Không có data/model/secret trong diff.
- Kết luận: **approved và merged**.

## 3. PR #19 — Linh

- Branch `linh-day5`, commit gốc `0a25e33`, commit retake screenshot `b9a8620`.
- Nội dung: README, `notes/demo_script.md`, `notes/day5_slides.md`, 5 screenshot.
- PR body có What / Why / How tested / Screenshot.
- CI xanh tại `b9a8620`; Huy approve; merge tại `d0ade04`.

### 3.1 Vấn đề phát hiện và xử lý

| Vấn đề | Xử lý |
|---|---|
| Screenshot còn browser chrome/tab cá nhân | Huy retake bằng Selenium/Firefox |
| Recommendations/Similar chưa có kết quả | Retake user 196, movie 1, Hybrid |
| `day5_evaluation.png` bị gán nhầm thành Compare | Retake đúng trang Evaluation |
| Ảnh Evaluation bị cắt bảng | Chụp full page 1600×1714 |
| README thiếu `day5_eval.md`, report/review, figure | Bổ sung ở PR #20 |
| Chưa có rehearsal thuyết trình | Thay bằng dry-run kỹ thuật 2 lần, ghi tại closeout |

### 3.2 Screenshot sau retake

| File | Kích thước | Nội dung |
|---|---:|---|
| `day5_home.png` | 1600×914 | Home, dataset và phương pháp |
| `day5_recommendations.png` | 1600×914 | User 196, Hybrid, top-K có kết quả |
| `day5_similar.png` | 1600×914 | Toy Story, Hybrid, danh sách tương tự |
| `day5_compare.png` | 1600×914 | User 196, 5 tab, Hybrid active |
| `day5_evaluation.png` | 1600×1714 | Bảng RMSE/MAE và ranking đầy đủ |

- Ảnh lấy từ app thật, không chỉnh sửa nội dung.
- Không còn browser chrome, tab cá nhân hoặc trạng thái rỗng.
- Kết luận: **approved và merged**, có hỗ trợ retake.

## 4. PR #20 — Huy

- Branch `feat/day5-final`, commit `a35bd66`.
- Thêm `notes/day5_report.md`, `notes/day5_eval.md`, `notes/day5_review.md`.
- Thêm `scripts/make_day5_figures.py` và 4 biểu đồ metrics.
- Cập nhật README: link report/eval/review, section biểu đồ.
- CI xanh tại `a35bd66`; merge tại `20178b4`.
- Release `v1.0.0` tạo tại `20178b4`.
- Kết luận: **approved và merged**.

## 5. PR #21 — Phong

- Branch `phong-day5-evaluation`, commit `b4262ff`.
- Bổ sung `notes/day5_eval.md`, thêm `notes/day5_phong_details.md`.
- Cập nhật `scripts/make_day5_figures.py`: validate model/metric, nhãn giá trị trade-off, tạo lại 4 PNG.
- Cập nhật checklist Phong trong task plan.
- CI xanh tại `b4262ff`; merge tại `2104c8b`.

### 5.1 Review post-merge

- PR được merge trước khi có review trực tiếp; Huy đã bổ sung review post-merge tại PR #21.
- Body PR được điền lại đầy đủ What / Why / How tested / Screenshot.
- Nội dung đạt: bảng số liệu khớp JSON, top-5/similar/fallback khớp service, 42 test chuyên biệt pass.
- Bootstrap CI là optional, không thực hiện; đã ghi rõ trong eval.
- Kết luận: **nội dung approved; release `v1.0.0` không gồm PR #21 nên cần `v1.0.1`**.

## 6. Số liệu và biểu đồ

### 6.1 Số liệu

- `baseline.json`: Popularity RMSE `1.0669849661484991`, MAE `0.8630965089060417`.
- `svd.json`: RMSE `0.956119767639409`, MAE `0.7524468775134182`.
- SVD giảm `0,110865` RMSE (10,3905%) và `0,110650` MAE (12,8201%).
- `ranking.json`: 5 model, 10 metric/model, 456 user đánh giá, 487 user bỏ, relevance `>= 4.0`, K chính `10`.
- NDCG@10: Popularity `0.174714`, SVD `0.137267`, Hybrid `0.109632`, Content-Based `0.055068`, Item-CF `0.031481`.
- Coverage@10: Item-CF `0.508323`, Hybrid `0.315101`, Content-Based `0.237812`, SVD `0.105826`, Popularity `0.023187`.
- Không phát hiện số liệu sửa tay hoặc tune trên test.

### 6.2 Biểu đồ

- Script `scripts/make_day5_figures.py` chỉ đọc `reports/metrics/*.json`.
- Có validate model/metric hữu hạn trước khi vẽ.
- 4 PNG có title, axis label, value label; trade-off có nhãn tọa độ.
- Chạy 2 lần liên tiếp: hash ổn định trong cùng môi trường.
- Đã mở kiểm tra trực quan cả 4 ảnh; bố cục và nhãn đọc được.

### 6.3 SHA-256 metrics

```text
845fcc2aa4a3991d15ca332c06848545bf484a0fb5c71b0c7c1de2985eb2a251  reports/metrics/baseline.json
cdbae3c189caccb23d3aef9ea8c08ce2eac5db626b1595ed904ff3f77d186879  reports/metrics/svd.json
51107d99c9bfdf2834362464336ee631e589b578b512bd6d67f258c1221d51fa  reports/metrics/ranking.json
```

## 7. Kiểm chứng cuối

| Kiểm tra | Kết quả |
|---|---|
| `pytest -q` | 106 passed trong 9,82 giây |
| `pytest tests/test_svd.py tests/test_hybrid.py tests/test_ranking_eval_script.py -q` | 42 passed trong 0,94 giây |
| `ruff check .` | pass |
| Smoke SVD/Hybrid, Item-CF, Content-Based, Surprise | pass |
| Metric hash trước/sau | giống hệt |
| Baseline hash | không đổi |
| Figure script 2 lần | hash ổn định trong cùng môi trường |
| Demo dry-run 2 lần | 0,1285 giây và 0,1136 giây; signature giống hệt |
| Top-5 user 196, Similar 1/50/56, fallback | khớp service |
| Link Markdown nội bộ | 42 link, 0 hỏng |
| CI PR #21 / `main` | success |
| Streamlit | HTTP 200 ở PR #20; app không đổi ở PR #21/closeout |

## 8. Trạng thái task

| Thành viên | Trạng thái | Ghi chú |
|---|---|---|
| Huy | Hoàn thành | Day 4, report/eval/review, figure, review/merge, closeout, release |
| Phong | Hoàn thành nội dung | Metrics, details, figures, Q&A; review post-merge đã bổ sung; bootstrap optional không làm |
| Linh | Hoàn thành phần lớn, có hỗ trợ | README/demo/slide/screenshot; Huy retake ảnh và bổ sung figure/link; rehearsal thay bằng dry-run |

## 9. Vệ sinh repo

- `git status` sạch sau closeout; chỉ có file dự kiến trong commit.
- Không có data, model artifact, cache, secret hoặc file tạm.
- Không thêm comment/docstring mới vào code.
- Không sửa metrics ngoài việc chạy lại evaluator cho kết quả giống hệt.

## 10. Rủi ro còn lại

- Chưa có rehearsal thuyết trình trực tiếp; đã có dry-run kỹ thuật và screenshot dự phòng.
- Một split/seed; chưa có cross-validation, bootstrap CI hoặc kiểm định thống kê.
- Explicit feedback, dữ liệu cũ, popularity bias; 487 user không có relevant item trong test.
- Content-Based chỉ dùng genre thô; fallback Popularity chưa giải quyết cold-start thực sự.
- CI không kiểm tra trực quan screenshot; đã review thủ công.

## 11. Kết luận

- PR #18, #19, #20, #21 đều đã merge; CI xanh.
- Báo cáo, eval, review, biểu đồ, screenshot, demo script và slide đã đủ.
- `v1.0.1` là release đầy đủ cuối cùng, bao gồm PR #21 và closeout.
- Dự án **hoàn thành** và đủ điều kiện bàn giao.
