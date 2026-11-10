# Dàn ý slide báo cáo tổng kết — Day 5

**Đề tài:** AI Personalized Recommendation System (MovieLens 100K)  
**Thời lượng trình bày:** 5–7 phút  
**Số lượng slide:** 12

## Slide 1 — Trang bìa
- **Tiêu đề:** AI Personalized Recommendation System
- **Phụ đề:** Hệ thống gợi ý phim cá nhân hóa trên MovieLens 100K
- **Nội dung:** Tên nhóm/thành viên (Huy, Phong, Linh), môn học/giảng viên (nếu có), ngày báo cáo
- **Hình/ghi chú:** Logo hoặc ảnh minh họa app

## Slide 2 — Bài toán và mục tiêu
- **Bài toán:** Cá nhân hóa gợi ý phim từ dữ liệu rating explicit, dữ liệu thưa.
- **Mục tiêu:**
  - Pipeline end-to-end: data → model → service → Streamlit app
  - Triển khai và so sánh 5 phương pháp gợi ý
  - Đánh giá bằng rating và ranking metrics, demo trực quan
- **Phạm vi:** MovieLens 100K, offline evaluation, không tune trên test

## Slide 3 — Dữ liệu MovieLens 100K
- **Thông tin:** 100.000 ratings, 943 users, 1.682 movies, thang điểm 1–5, độ thưa ~93,7%
- **Tiền xử lý & split:** chuẩn hóa schema, lưu Parquet; split chuẩn `u1.base` (80.000 train) / `u1.test` (20.000 test)
- **Nguyên tắc:** train-only fit, test chỉ dùng đánh giá, lịch sử user lấy từ train, seed 42
- **Hình/ghi chú:** sơ đồ pipeline dữ liệu hoặc thống kê cơ bản

## Slide 4 — Kiến trúc hệ thống
- **Luồng chính:** `App (Streamlit) → RecommenderService → Models`
- **Các lớp:** Data, Model, Evaluation, Service, Presentation
- **Điểm thiết kế:** UI không import trực tiếp model; contract thống nhất; fallback tập trung tại service; cache cho dữ liệu/service
- **Hình/ghi chú:** sơ đồ kiến trúc (mermaid/diagram) và cấu trúc thư mục chính

## Slide 5 — 5 phương pháp gợi ý
| Phương pháp | Method key | Ý tưởng chính |
|---|---|---|
| Popularity | `popularity` | Bayesian average / độ phổ biến, baseline & fallback |
| Content-Based | `content_based` | Genre features, cosine similarity, user profile từ train |
| Item-CF | `item_cf` | Item-item similarity (adjusted cosine) |
| SVD | `svd` | Matrix factorization, dự đoán rating/latent preferences |
| Hybrid | `hybrid` | Kết hợp SVD + Item-CF + Content-Based |

- **Ghi chú:** score khác thang đo giữa các phương pháp; có fallback khi thiếu tín hiệu

## Slide 6 — Giao thức đánh giá
- **Rating prediction:** RMSE, MAE trên test set (Popularity, SVD)
- **Ranking:** Precision@5/10, Recall@10, NDCG@10, Coverage@10
- **Thiết lập:** relevance `rating >= 4.0`, K = 5/10/20 (chính K=10), macro-average trên 456 users, 487 users skipped, coverage trên catalog
- **Nguyên tắc:** không tune hyperparameter/trọng số/K trên test; số liệu lấy từ JSON

## Slide 7 — Kết quả Rating Prediction (Popularity vs SVD)
- **Bảng kết quả (từ `reports/metrics/baseline.json`, `reports/metrics/svd.json`):**

| Model | RMSE | MAE |
|---|---:|---:|
| Popularity | 1.066985 | 0.863097 |
| SVD | 0.956120 | 0.752447 |

- **Nhận xét:** SVD giảm ~10,39% RMSE và ~12,82% MAE so với Popularity
- **Hình/ghi chú:** biểu đồ RMSE/MAE (nếu có)

## Slide 8 — Kết quả Ranking (5 phương pháp, K=10)
- **Bảng kết quả (từ `reports/metrics/ranking.json`):**

| Model | Precision@10 | Recall@10 | NDCG@10 | Coverage@10 |
|---|---:|---:|---:|---:|
| Popularity | 0.164474 | 0.070910 | 0.174714 | 0.023187 |
| Content-Based | 0.047368 | 0.022264 | 0.055068 | 0.237812 |
| Item-CF | 0.029167 | 0.018530 | 0.031481 | 0.508323 |
| SVD | 0.127851 | 0.048426 | 0.137267 | 0.105826 |
| Hybrid | 0.100658 | 0.040805 | 0.109632 | 0.315101 |

- **Nhận xét:** Popularity dẫn đầu NDCG@10; Item-CF dẫn đầu Coverage@10

## Slide 9 — Phân tích & Trade-off
- **Rating vs Ranking:** SVD tốt hơn Popularity về RMSE/MAE nhưng không vượt về NDCG@10 trên split này.
- **NDCG vs Coverage:** Popularity thiên popular items (NDCG cao, coverage thấp); Item-CF đa dạng catalog hơn nhưng precision/NDCG thấp.
- **Hybrid:** kết hợp tín hiệu, coverage tốt hơn SVD nhưng NDCG@10 không vượt SVD/Popularity (trade-off/dilution).
- **Nguyên nhân:** dữ liệu thưa, popularity bias, feature genre thô, score/scale khác nhau.
- **Hình/ghi chú:** biểu đồ NDCG@10, Coverage@10, scatter NDCG vs Coverage

## Slide 10 — Demo ứng dụng Streamlit
- **Các trang:** Home, Recommendations, Similar Movies, Compare Methods, Evaluation
- **Kịch bản demo:**
  - User 1/196/405: Top-10 SVD và Hybrid, Compare 5 phương pháp
  - Phim 1/50/56: Similar Movies (SVD, Hybrid)
  - Evaluation: RMSE/MAE và ranking 5 model
- **Fallback:** user mới/thưa dữ liệu → Popularity; `exclude_seen=True`
- **Hình/ghi chú:** screenshot `day5_recommendations.png`, `day5_compare.png`, `day5_evaluation.png`

## Slide 11 — Hạn chế, bài học & hướng phát triển
- **Hạn chế:** dữ liệu cũ/thưa, explicit-only, một split/seed, genre thô, popularity bias, score khác thang đo
- **Bài học:** tách lớp App-Service-Model giúp tích hợp; cần protocol rõ và báo cáo trung thực trade-off
- **Hướng phát triển:** implicit feedback, nội dung phong phú, mô hình/ hybrid nâng cao, đánh giá đa split và fairness

## Slide 12 — Kết luận & Q&A
- **Kết luận:** hoàn thành hệ thống gợi ý 5 phương pháp, có đánh giá định lượng và demo end-to-end; kết quả cho thấy trade-off rõ giữa accuracy, ranking và coverage
- **Đóng góp:** pipeline tái lập, service thống nhất, giao diện so sánh trực quan
- **Q&A:** dự phòng câu hỏi về Popularity vs SVD, Hybrid, leakage, cold-start, hạn chế
- **Tài liệu:** README, `notes/day5_report.md`, `notes/day5_eval.md`, `reports/metrics/*.json`
