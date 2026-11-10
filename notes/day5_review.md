# Review tích hợp cuối — Day 5

**Ngày:** 11/11/2026  
**Người review:** Huy  
**Base:** `origin/main` tại `d0ade04` (sau merge PR #19)  
**Branch tích hợp:** `feat/day5-final`

## 1. Phạm vi review

- PR #18 — Day 4 finalization.
- PR #19 — README cuối, screenshot, demo script và slide outline.
- Bộ số liệu cuối: `reports/metrics/baseline.json`, `svd.json`, `ranking.json`.
- Báo cáo/eval/review, biểu đồ metrics và README sau tích hợp.
- Kiểm chứng tái lập, CI và điều kiện release.

Không nằm trong phạm vi: thêm model, metric, dependency, tuning hyperparameter/trọng số/threshold/K trên test.

## 2. Kết quả review PR #18

- Branch `docs/day4-finalize-day5-plan`, commit `d2b0151` và `90e8f00`.
- Nội dung: điền kết quả Day 4, tạo `notes/day4_report.md`, cập nhật CI với `run_svd_eval.py` và `smoke_svd_hybrid.py`, thêm `notes/task_day5_11_11.md`.
- CI xanh; merge vào `main` tại `066bcd8`.
- Không có data/model/secret trong diff.
- Kết luận: **approved và merged**.

## 3. Kết quả review PR #19

- Branch `linh-day5`, commit gốc `0a25e33`, commit retake screenshot `b9a8620`.
- Nội dung: README cuối, `notes/demo_script.md`, `notes/day5_slides.md`, 5 screenshot app.
- PR body có What / Why / How tested / Screenshot.
- CI xanh tại `b9a8620`; review approve; merge vào `main` tại `d0ade04`.

### 3.1 Vấn đề phát hiện và xử lý

| Vấn đề | Xử lý |
|---|---|
| Screenshot còn browser chrome/tab cá nhân | Retake bằng Selenium/Firefox, chỉ chụp vùng app |
| Recommendations/Similar chưa có kết quả | Retake với user 196, movie 1, method Hybrid |
| `day5_evaluation.png` bị gán nhầm thành Compare | Retake đúng trang Evaluation, đủ hai bảng |
| Ảnh Evaluation bị cắt bảng | Chụp full page 1600×1714 |
| README link `notes/day5_eval.md` nhưng file chưa có | Tạo file trong PR Day 5 final |
| README thiếu link report/review và biểu đồ | Bổ sung trong PR Day 5 final |

### 3.2 Kiểm tra screenshot sau retake

| File | Kích thước | Nội dung |
|---|---:|---|
| `day5_home.png` | 1600×914 | Home, thông tin dataset và phương pháp |
| `day5_recommendations.png` | 1600×914 | User 196, Hybrid, top-K có kết quả |
| `day5_similar.png` | 1600×914 | Toy Story, Hybrid, danh sách tương tự |
| `day5_compare.png` | 1600×914 | User 196, 5 tab, Hybrid active |
| `day5_evaluation.png` | 1600×1714 | Bảng RMSE/MAE và ranking đầy đủ |

- Ảnh lấy từ app thật, không chỉnh sửa nội dung.
- Không còn browser chrome, tab cá nhân hoặc trạng thái rỗng.
- Kết luận: **approved và merged**.

## 4. Review số liệu

- `baseline.json`: Popularity RMSE `1.0669849661484991`, MAE `0.8630965089060417`.
- `svd.json`: RMSE `0.956119767639409`, MAE `0.7524468775134182`; hyperparameter đúng quyết định Day 4.
- `ranking.json`: 5 model, 10 metric/model, 456 user đánh giá, 487 user bỏ, relevance `>= 4.0`, K chính `10`.
- NDCG@10 và Coverage@10 trong README/report/eval khớp JSON.
- Không phát hiện số liệu sửa tay hoặc tune trên test.
- Kết luận: **số liệu đạt**.

## 5. Review biểu đồ

- Script: `scripts/make_day5_figures.py`.
- Chỉ đọc `reports/metrics/*.json`, không đọc test/raw data.
- Tạo đủ 4 hình:
  - `day5_rating_rmse_mae.png`
  - `day5_ranking_ndcg10.png`
  - `day5_ranking_coverage10.png`
  - `day5_ndcg_vs_coverage.png`
- Có title, axis label, value label, thứ tự model thống nhất.
- Chạy 2 lần: SHA-256 của cả 4 file giống hệt.
- `ruff check` ban đầu báo import order; đã sửa, lint pass.
- Kết luận: **đạt**.

## 6. Kiểm chứng cuối

| Kiểm tra | Kết quả |
|---|---|
| `pytest -q` | 106 passed trong 9,99 giây |
| `ruff check .` | pass |
| `smoke_svd_hybrid.py` | pass; fallback, invalid movie, repeatability, vectorization error `8,88e-16` |
| `smoke_item_cf.py` | pass; fallback và invalid movie |
| `smoke_content_based.py` | pass; 1.682 phim, 2 phim zero-genre |
| `smoke_surprise.py` | pass; RMSE `0.9540` |
| `run_svd_eval.py` | RMSE `0.956119767639409`, MAE `0.7524468775134182`; khoảng 1,42 giây |
| `run_ranking_eval.py` | 5 model; khoảng 15,09 giây |
| Hash metrics trước/sau | giống hệt |
| Baseline hash | không đổi |
| Figure hash 2 lần | giống hệt |
| Warm service 12 lời gọi | khoảng 0,0878 giây |
| Streamlit | HTTP 200 |
| AppTest | pass trong pytest |

### 6.1 SHA-256 metrics

```text
845fcc2aa4a3991d15ca332c06848545bf484a0fb5c71b0c7c1de2985eb2a251  reports/metrics/baseline.json
cdbae3c189caccb23d3aef9ea8c08ce2eac5db626b1595ed904ff3f77d186879  reports/metrics/svd.json
51107d99c9bfdf2834362464336ee631e589b578b512bd6d67f258c1221d51fa  reports/metrics/ranking.json
```

### 6.2 SHA-256 figures

```text
05ffc0812198c5d9b8f0d26f8156d1f8f3bbbf4d80a615e8a5b4fc1d59dc1a1d  day5_rating_rmse_mae.png
620d9343a1cb2934b813d0d19b1cadf3e9e47dfd0d655b8d1e70bcc91141cf0c  day5_ranking_ndcg10.png
2ac8070d2484a57c3f38e008516b2764b228b35ee976eb034f5bec02f845ad95  day5_ranking_coverage10.png
97306a44295ea048ebb1bc41bb40e090b78cd0377f370ab5d7c61f7a3d529381  day5_ndcg_vs_coverage.png
```

## 7. Review tài liệu

- `notes/day5_report.md`: đủ cấu trúc, số liệu khớp JSON, có 4 biểu đồ, 5 screenshot, phân tích trade-off, hạn chế, phân công, tài liệu tham khảo.
- `notes/day5_eval.md`: protocol, bảng rating/ranking, fallback, tái lập, hạn chế; khớp report/README.
- `notes/demo_script.md`: 5–7 phút, phân vai, user 1/196/405, movie 1/50/56, fallback, checklist.
- `notes/day5_slides.md`: 12 slide, bảng số liệu khớp JSON.
- `README.md`: kết quả, biểu đồ, screenshot, demo, hạn chế, link report/eval/review.
- Không phát hiện số liệu mâu thuẫn hoặc tuyên bố quá mức.

## 8. Vệ sinh repo

- `git status` chỉ có file dự kiến: README, report/eval/review, figure script và 4 figure metrics.
- Không có data, model artifact, cache, secret hoặc file tạm.
- Không thêm comment/docstring mới vào code.
- Không sửa `baseline.json`, `svd.json`, `ranking.json` ngoài việc chạy lại evaluator cho kết quả giống hệt.
- `.gitignore` vẫn bao phủ data/model/cache.

## 9. Rủi ro còn lại

- Một split/seed; chưa có cross-validation, bootstrap CI hoặc kiểm định thống kê.
- Explicit feedback, dữ liệu cũ, popularity bias; 487 user không có relevant item trong test.
- Content-Based chỉ dùng genre thô; fallback Popularity chưa giải quyết cold-start thực sự.
- CI không kiểm tra trực quan screenshot; đã review thủ công.
- Tag/release chỉ tạo sau khi PR Day 5 final merge và CI xanh.

## 10. Kết luận

- PR #18 và #19 đạt yêu cầu, đã merge.
- Số liệu, biểu đồ, screenshot, báo cáo và demo đã đủ cho Day 5.
- Điều kiện còn lại: tạo PR Day 5 final, CI xanh, merge, tag/release `v1.0.0`.
- Quyết định: **đủ điều kiện release sau khi PR cuối merge**.
