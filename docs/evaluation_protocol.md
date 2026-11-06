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

Sẽ bổ sung ở Day 3:

- Precision@K
- Recall@K
- NDCG@K

## Chống leakage

- Không đưa test vào trainset.
- Không dùng rating test khi tính hồ sơ user.
- Không điều chỉnh model dựa trên kết quả test.
