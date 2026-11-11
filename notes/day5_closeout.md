# Closeout Day 5 — hoàn thành dự án

**Ngày:** 12/11/2026  
**Trạng thái:** Hoàn thành  
**Base:** `main` tại `2104c8b` (sau PR #21)  
**Release đầy đủ:** `v1.0.1`  
**Release trước:** `v1.0.0` tại `20178b4` (không gồm PR #21)  
**Tài liệu liên quan:** [Báo cáo cuối](day5_report.md), [Đánh giá cuối](day5_eval.md), [Review tích hợp](day5_review.md), [README](../README.md)

## 1. Kết quả cuối

- 5 phương pháp: Popularity, Content-Based, Item-CF, SVD, Hybrid.
- App Streamlit 5 trang: Home, Recommendations, Similar Movies, Compare Methods, Evaluation.
- Rating: SVD RMSE `0.956120`, MAE `0.752447`; Popularity RMSE `1.066985`, MAE `0.863097`.
- Ranking: Popularity dẫn NDCG@10 `0.174714`; Item-CF dẫn Coverage@10 `0.508323`; Hybrid NDCG@10 `0.109632`, Coverage@10 `0.315101`.
- Không tune hyperparameter, trọng số, threshold hoặc K trên test.
- 106 test pass; 42 test chuyên biệt SVD/Hybrid/ranking pass; ruff pass.
- CI xanh trên PR #21 head `b4262ff` và `main` `2104c8b`.
- Release đầy đủ: <https://github.com/Huydcpy/AI-PERSONALIZED_RECOMMENDATION_SYSTEM-/releases/tag/v1.0.1>

## 2. Trạng thái task theo thành viên

| Thành viên | Trạng thái | Bằng chứng / ngoại lệ |
|---|---|---|
| Huy | Hoàn thành | PR #18 Day 4, PR #20 báo cáo/eval/figure, PR closeout, review/merge/release |
| Phong | Hoàn thành nội dung | PR #21: metrics, `day5_phong_details.md`, biểu đồ, Q&A; review post-merge và body PR được bổ sung trong closeout. Bootstrap CI là optional, không thực hiện |
| Linh | Hoàn thành phần lớn, có hỗ trợ | PR #19: README, demo script, slide, screenshot; Huy retake screenshot `b9a8620`, bổ sung figure/link ở PR #20. Rehearsal thuyết trình trực tiếp không có; thay bằng dry-run kỹ thuật 2 lần |

## 3. Việc đã đóng trong closeout

- Điền What/Why/How tested/Screenshot cho PR #21 sau merge.
- Thêm review post-merge của Huy cho PR #21, ghi nhận việc merge trước review trực tiếp.
- Tạo tag/release `v1.0.1` bao gồm PR #20, PR #21 và closeout.
- Chạy demo dry-run 2 lần, xác nhận kết quả lặp lại và `exclude_seen`.
- Cập nhật report/eval/review/README và banner trạng thái của task plan.
- Kiểm tra lại link nội bộ, metric hash, biểu đồ và top-5/similar/fallback.

## 4. Kiểm chứng cuối

| Kiểm tra | Kết quả |
|---|---|
| `pytest -q` | 106 passed trong 9,82 giây |
| `pytest tests/test_svd.py tests/test_hybrid.py tests/test_ranking_eval_script.py -q` | 42 passed trong 0,94 giây |
| `ruff check .` | pass |
| Smoke SVD/Hybrid, Item-CF, Content-Based, Surprise | pass |
| Metric SHA-256 trước/sau | giống hệt |
| `baseline.json` | không đổi |
| Figure script 2 lần liên tiếp | hash ổn định trong cùng môi trường |
| Demo dry-run 2 lần | 0,1285 giây và 0,1136 giây; signature giống hệt |
| Top-5 user 196, Similar 1/50/56, fallback | khớp service |
| Link Markdown nội bộ | 42 link, 0 hỏng |
| CI PR #21 / `main` | success |
| Streamlit | HTTP 200 ở lần kiểm tra PR #20; app không đổi ở PR #21/closeout |

### 4.1 Demo dry-run

Dry-run gọi service thật, không phải rehearsal thuyết trình:

- 15 lời gọi Recommendations: 3 user × 5 phương pháp, K=10.
- 12 lời gọi Similar Movies: 3 phim × 4 phương pháp, K=10.
- 5 lời gọi fallback user 999999.
- Kiểm tra `exclude_seen=True` cho user 196.
- Hai lần chạy cho cùng danh sách movie ID; thời gian 0,1285 giây và 0,1136 giây.

### 4.2 Metric hash

```text
845fcc2aa4a3991d15ca332c06848545bf484a0fb5c71b0c7c1de2985eb2a251  reports/metrics/baseline.json
cdbae3c189caccb23d3aef9ea8c08ce2eac5db626b1595ed904ff3f77d186879  reports/metrics/svd.json
51107d99c9bfdf2834362464336ee631e589b578b512bd6d67f258c1221d51fa  reports/metrics/ranking.json
```

## 5. Hạn chế còn lại

- Chưa có rehearsal thuyết trình trực tiếp; đã thay bằng dry-run kỹ thuật và screenshot dự phòng.
- Một split/seed; chưa có cross-validation, bootstrap CI hoặc kiểm định thống kê.
- Explicit feedback, dữ liệu cũ, popularity bias; 487 user không có relevant item trong test.
- Content-Based chỉ dùng genre thô; fallback Popularity chưa giải quyết cold-start thực sự.
- CI không kiểm tra trực quan screenshot; đã review thủ công.

## 6. Kết luận

Dự án đã hoàn thành các deliverable Day 5 và đủ điều kiện bàn giao. `v1.0.1` là release đầy đủ cuối cùng; `v1.0.0` được giữ làm mốc lịch sử trước PR #21.
