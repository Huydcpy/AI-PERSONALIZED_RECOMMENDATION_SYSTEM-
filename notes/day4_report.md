# Báo cáo Day 4 — 09/11/2026

Base tích hợp: `ea4a550`. Hoàn thiện tài liệu và CI ngày 10/11/2026.

## Đã triển khai

- SVD dùng `surprise.SVD` với `n_factors=100`, `n_epochs=20`, `lr_all=0.005`, `reg_all=0.02`, `random_state=42`; chỉ fit trên train, dự đoán rating trong [1,5], similar movies dùng vector hóa latent factors và fallback Popularity.
- Hybrid kết hợp SVD, Item-CF và Content-Based; trọng số recommend 0.5/0.3/0.2, similar 0.4/0.3/0.3; min-max từng component, chỉ blend item native, pool `max(50, 3*K)`, tie-break `movie_id`; fallback Popularity có reason cold-start/thiếu tín hiệu.
- Service đăng ký đủ 5 phương pháp (`popularity`, `content_based`, `item_cf`, `svd`, `hybrid`), giữ response contract và expose metrics SVD.
- `scripts/run_svd_eval.py` ghi `reports/metrics/svd.json`; `scripts/run_ranking_eval.py` mở rộng lên 5 model; `scripts/smoke_svd_hybrid.py` kiểm tra recommend/similar, fallback và các case biên.
- Giao diện Recommendations, Similar Movies, Compare Methods, Evaluation và Home hiển thị đủ 5 phương pháp với `method`, `score`, `reason` thực tế.
- CI bổ sung SVD rating evaluation và smoke SVD/Hybrid; README điền kết quả, ví dụ thực tế và liên kết báo cáo.

## Kiểm thử local

- `python -m pytest -q`: 106 passed.
- `python -m ruff check .`: pass.
- `python scripts/smoke_svd_hybrid.py`: pass; phủ 3 user, 3 phim, seen filtering, user lạ, user metadata-only, phim zero-interaction, movie không tồn tại và kiểm tra tái lập.
- `python scripts/run_svd_eval.py` và `python scripts/run_ranking_eval.py`: pass, chạy lại cho SHA-256 giống hệt `svd.json` và `ranking.json`.
- Ranking evaluation: khoảng 18,35 giây cho toàn lệnh, đạt mục tiêu dưới 5 phút.
- Warm service cho 3 user và 3 phim ở cả SVD/Hybrid: khoảng 0,08 giây cho 12 lời gọi; khởi tạo service khoảng 1,18 giây trên máy local.
- AppTest: 3 user/3 phim cho SVD/Hybrid, Compare đủ 5 tab/50 card, Evaluation có 2 dòng rating và 5 dòng ranking.
- Không có comment/docstring mới trong code; `git diff --check` không lỗi whitespace.

## Rating prediction

| Model | RMSE | MAE |
|---|---:|---:|
| Popularity | 1.066985 | 0.863097 |
| SVD | 0.956120 | 0.752447 |

SVD giảm khoảng 10,39% RMSE và 12,82% MAE so với Popularity. Baseline Day 1 giữ nguyên; không claim rating metrics cho các phương pháp còn lại.

## Ranking metrics

| Model | Precision@5 | Precision@10 | Recall@10 | NDCG@10 | Coverage@10 |
|---|---:|---:|---:|---:|---:|
| Popularity | 0.163158 | 0.164474 | 0.070910 | 0.174714 | 0.023187 |
| Content-Based | 0.058772 | 0.047368 | 0.022264 | 0.055068 | 0.237812 |
| Item-CF | 0.028947 | 0.029167 | 0.018530 | 0.031481 | 0.508323 |
| SVD | 0.136842 | 0.127851 | 0.048426 | 0.137267 | 0.105826 |
| Hybrid | 0.108333 | 0.100658 | 0.040805 | 0.109632 | 0.315101 |

Popularity dẫn đầu NDCG@10; Item-CF dẫn đầu Coverage@10. SVD cải thiện dự đoán rating nhưng không vượt Popularity về ranking. Hybrid thấp hơn SVD và Popularity về Precision/Recall/NDCG@10, cao hơn Content-Based và Item-CF; Hybrid tăng coverage so với SVD nhưng thấp hơn Item-CF.

Protocol: relevance rating >= 4.0, K=5/10/20, K chính 10, macro-average trên 456 user có relevant item; 487 user không có relevant item bị bỏ qua. Coverage tính trên toàn catalog 1.682 phim. Fallback được tính trong metrics. Không tune hyperparameter/trọng số trên test.

## Ví dụ thực tế

### SVD — user 196, Top-5 gợi ý

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 483 | Casablanca (1942) | 4.287311 | svd |
| 408 | Close Shave, A (1995) | 4.278069 | svd |
| 169 | Wrong Trousers, The (1993) | 4.265532 | svd |
| 318 | Schindler's List (1993) | 4.255841 | svd |
| 923 | Raise the Red Lantern (1991) | 4.253564 | svd |

### Hybrid — user 196, Top-5 gợi ý

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 127 | Godfather, The (1972) | 0.602944 | hybrid |
| 481 | Apartment, The (1960) | 0.500000 | hybrid |
| 483 | Casablanca (1942) | 0.500000 | hybrid |
| 408 | Close Shave, A (1995) | 0.487263 | hybrid |
| 169 | Wrong Trousers, The (1993) | 0.469986 | hybrid |

### SVD — similar to Toy Story (1), Top-5

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 45 | Eat Drink Man Woman (1994) | 0.405460 | svd |
| 378 | Miracle on 34th Street (1994) | 0.348896 | svd |
| 979 | Trigger Effect, The (1996) | 0.343406 | svd |
| 174 | Raiders of the Lost Ark (1981) | 0.339268 | svd |
| 1459 | Madame Butterfly (1995) | 0.335045 | svd |

### Hybrid — similar to Toy Story (1), Top-5

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 174 | Raiders of the Lost Ark (1981) | 0.606314 | hybrid |
| 50 | Star Wars (1977) | 0.356538 | hybrid |
| 28 | Apollo 13 (1995) | 0.316084 | hybrid |
| 45 | Eat Drink Man Woman (1994) | 0.312127 | hybrid |
| 95 | Aladdin (1992) | 0.303779 | hybrid |

Đây là prefix Top-5 của recommend K=10; Hybrid phụ thuộc pool `max(50, 3*K)`, nên cần giữ K khi tái lập. Đầy đủ 3 user/3 phim: [day4_eval.md](day4_eval.md).

## Đánh giá và hạn chế

- Không tune trên test; một split và một seed chưa chứng minh khác biệt có ý nghĩa thống kê.
- Chưa có implicit feedback; score giữa các phương pháp khác thang đo nên không so sánh trực tiếp.
- SVD similar dựa trên latent factors nên có thể không gần nhau về thể loại.
- 487/943 user bị bỏ khỏi ranking metrics do không có relevant item trong test; kết quả chỉ đại diện nhóm có relevant item.
- Hybrid chưa cải thiện mọi tiêu chí; không đổi trọng số để che kết quả.

## Trạng thái bàn giao

- PR #15 và #16 tích hợp SVD/Hybrid và app; PR #17 hoàn tất đánh giá Day 4. `main` hiện tại `184ecdd`.
- CI `main` xanh tại `184ecdd` cho workflow trước khi bổ sung hai bước Day 4; workflow hiện tại đã có `run_svd_eval.py` và `smoke_svd_hybrid.py`, cần xác nhận run mới sau khi push.
- Deliverables: `src/models/svd.py`, `src/models/hybrid.py`, `src/service/recommender_service.py`, `scripts/run_svd_eval.py`, `scripts/run_ranking_eval.py`, `scripts/smoke_svd_hybrid.py`, `reports/metrics/svd.json`, `reports/metrics/ranking.json`, app 5 phương pháp, README và CI.
- Review và protocol chi tiết: [day4_eval.md](day4_eval.md), [day4_review.md](day4_review.md).
