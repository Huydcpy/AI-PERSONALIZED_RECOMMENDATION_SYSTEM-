# Evaluation Protocol

## Mục tiêu

Đánh giá chất lượng dự đoán rating của các model một cách công bằng, tái lập được và không gây rò rỉ dữ liệu (leakage).

## Dữ liệu

- Dataset: MovieLens 100K.
- Train: `u1.base` — 80.000 ratings.
- Test: `u1.test` — 20.000 ratings.
- Tổng: 100.000 ratings, 943 users, 1.682 movies.

## Quy tắc đánh giá

- Chỉ dùng train để fit và tuning.
- Test chỉ dùng một lần để đánh giá cuối cùng.
- Không dùng test để chọn hyperparameter.
- Lịch sử user khi recommend chỉ lấy từ train.
- Seed cố định: 42.

## Rating metrics

- RMSE = `sqrt(mean((y_true - y_pred)^2))`.
- MAE = `mean(|y_true - y_pred|)`.

## Baseline

- Popularity với Bayesian movie average:

```text
score = (v / (v + m)) * R + (m / (v + m)) * C
```

Trong đó:

- `v`: số lượt rating của phim.
- `R`: rating trung bình của phim.
- `C`: rating trung bình toàn hệ thống.
- `m = 50`.

Kỳ vọng RMSE: 0,95–1,10.

## Ranking metrics

Day 3 đánh giá Popularity, Content-Based và Item-CF; chưa đánh giá SVD/Hybrid.

- Relevant item: phim có `rating >= 4.0` trong test của user.
- K = 5, 10, 20; K chính = 10.
- Candidate set là toàn bộ catalog trừ phim user đã rating trong train, không negative sampling.
- Fit model bằng train và movies; chỉ dùng test để tạo ground truth và tính metric.
- Gọi recommend một lần/user/model với K = 20, `exclude_seen=True`; dùng các prefix cho K nhỏ hơn.
- Loại duplicate trước khi lấy top-K, giữ lần xuất hiện đầu tiên và thứ tự model trả về.
- Model sort score giảm dần, tie-break `movie_id` tăng dần. Fallback được nối sau kết quả model, không sort lại hai thang điểm khác nhau.

Với `R(u)` là tập relevant và `L_K(u)` là top-K sau loại duplicate:

```text
Precision@K(u) = |R(u) ∩ L_K(u)| / K
Recall@K(u) = |R(u) ∩ L_K(u)| / |R(u)|
DCG@K(u) = sum(1 / log2(rank + 1)) tại các vị trí relevant, rank bắt đầu từ 1
IDCG@K(u) = sum(1 / log2(rank + 1)), rank = 1..min(|R(u)|, K)
NDCG@K(u) = DCG@K(u) / IDCG@K(u)
Coverage@10 = |union(L_10(u))| / số phim trong movies
```

Precision vẫn chia K khi model trả ít hơn K phim. Metric cho relevant rỗng là 0 ở cấp hàm; evaluator bỏ user đó khỏi macro-average. Tập user được xét là hợp của user trong train/test; `n_users_skipped` đếm user không có relevant test item. Nếu không có user hợp lệ, script báo lỗi thay vì ghi kết quả 0 giả.

Macro-average dùng cùng tập user hợp lệ cho cả 3 model. Coverage dùng tập user này và toàn bộ catalog làm mẫu số, kể cả phim không có tương tác train. Kết quả gồm cả item fallback Popularity; method và reason thực tế được kiểm tra trong smoke script.

Chạy `python scripts/run_ranking_eval.py`; kết quả lưu tại `reports/metrics/ranking.json`, gồm config, số user đánh giá/bỏ qua, 9 ranking metrics/model và coverage@10. Script yêu cầu đủ cả 3 model và module ranking metrics của Huy; thiếu dependency hoặc metric không hữu hạn/ngoài [0, 1] thì exit khác 0 và không ghi đè kết quả hiện có.

Test chỉ dùng một lần cho đánh giá cuối cùng với cấu hình đã chốt; không chọn model/hyperparameter từ kết quả test. Các lần chạy lại để xác minh tái lập không được dùng để tune. Không tính RMSE/MAE cho Item-CF khi chưa có `predict_rating`; baseline Day 1 giữ nguyên.

## Chống leakage

- Không đưa test vào trainset.
- Không dùng rating test khi tính hồ sơ user.
- Không điều chỉnh model dựa trên kết quả test.
