# Báo cáo Day 3 — 07/11/2026

## Đã triển khai

- Item-CF adjusted cosine trên rating đã trừ trung bình user từ train; top-50 láng giềng, clip similarity âm, loại diagonal, tie-break movie_id.
- Gợi ý theo weighted centered ratings, clip predicted_rating vào [1,5]; lọc phim đã xem, fallback Popularity với reason cold-start/thiếu tín hiệu.
- Ranking metrics thuần túy và evaluator K=5/10/20, relevance threshold 4.0, macro-average, Coverage@10; ghi JSON tất định.
- Service đăng ký item_cf, đọc ranking.json, thông báo method chưa hỗ trợ Day 4; giữ response contract và baseline RMSE/MAE.
- Tích hợp với giao diện PR #13 của Linh: Recommendations, Similar Movies, Compare Methods và Evaluation hoạt động với Item-CF.
- CI thêm evaluator và smoke Item-CF; giữ lint, test, app boundary và smoke cũ.

## Kiểm thử local

- `python -m pytest -q`: 67 passed.
- `python -m ruff check .`: pass.
- `python scripts/smoke_item_cf.py`: pass, gồm 3 user, 3 phim, seen filtering, cold-start, metadata-only user, zero-interaction movie và invalid movie.
- `python scripts/run_ranking_eval.py`: pass, tái lập số liệu với cấu hình cố định.
- AppTest kiểm tra các trang và tương tác Item-CF cho user 1/196/405, phim Toy Story/Star Wars/Pulp Fiction, Compare đủ 3 phương pháp và bảng ranking.
- Đo warm service recommend + similar_items cho 3 user: tối đa 0,037 giây; đây là thời gian service local, không phải cam kết độ trễ qua mạng.

Trên workspace Windows dùng `.\.venv\python.exe` thay cho `python`.

## Đánh giá và hạn chế

Đánh giá 456 user; bỏ qua 487 user không có relevant test item. Popularity tốt nhất theo NDCG@10; Item-CF coverage cao hơn nhưng precision thấp. Không tune trên test, không thay baseline Day 1, chưa đánh giá SVD/Hybrid. Chi tiết protocol và phát hiện: [day3_eval.md](day3_eval.md). Review tích hợp: [day3_review.md](day3_review.md).

## Trạng thái bàn giao

Phần code và kiểm chứng local đã hoàn tất. Trạng thái GitHub CI, review độc lập và merge phải được ghi theo bằng chứng thực tế trên PR. Stash gốc được giữ nguyên; không chứa thay đổi chưa bàn giao duy nhất.

## Ranking metrics

| Model | Precision@5 | Precision@10 | Recall@10 | NDCG@10 | Coverage@10 |
|---|---:|---:|---:|---:|---:|
| popularity | 0.163158 | 0.164474 | 0.070910 | 0.174714 | 0.023187 |
| content_based | 0.058772 | 0.047368 | 0.022264 | 0.055068 | 0.237812 |
| item_cf | 0.028947 | 0.029167 | 0.018530 | 0.031481 | 0.508323 |

### Top-5 user 1

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 236 | Citizen Ruth (1996) | 5.000000 | item_cf |
| 266 | Kull the Conqueror (1997) | 5.000000 | item_cf |
| 297 | Ulee's Gold (1997) | 5.000000 | item_cf |
| 301 | In & Out (1997) | 5.000000 | item_cf |
| 303 | Ulee's Gold (1997) | 5.000000 | item_cf |

### Top-5 user 196

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 127 | Godfather, The (1972) | 5.000000 | item_cf |
| 154 | Monty Python's Life of Brian (1979) | 5.000000 | item_cf |
| 182 | GoodFellas (1990) | 5.000000 | item_cf |
| 293 | Donnie Brasco (1997) | 5.000000 | item_cf |
| 311 | Wings of the Dove, The (1997) | 5.000000 | item_cf |

### Top-5 user 405

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 1362 | American Strays (1996) | 5.000000 | item_cf |
| 1654 | Chairman of the Board (1998) | 5.000000 | item_cf |
| 1235 | Big Bang Theory, The (1994) | 4.000000 | item_cf |
| 258 | Contact (1997) | 3.883526 | item_cf |
| 318 | Schindler's List (1993) | 3.789973 | item_cf |

### Similar movie 1

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 174 | Raiders of the Lost Ark (1981) | 0.232298 | item_cf |
| 50 | Star Wars (1977) | 0.218316 | item_cf |
| 28 | Apollo 13 (1995) | 0.205302 | item_cf |
| 318 | Schindler's List (1993) | 0.198516 | item_cf |
| 181 | Return of the Jedi (1983) | 0.197914 | item_cf |

### Similar movie 50

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 181 | Return of the Jedi (1983) | 0.599913 | item_cf |
| 172 | Empire Strikes Back, The (1980) | 0.537217 | item_cf |
| 174 | Raiders of the Lost Ark (1981) | 0.486604 | item_cf |
| 127 | Godfather, The (1972) | 0.357530 | item_cf |
| 173 | Princess Bride, The (1987) | 0.351493 | item_cf |

### Similar movie 56

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 12 | Usual Suspects, The (1995) | 0.245916 | item_cf |
| 357 | One Flew Over the Cuckoo's Nest (1975) | 0.245394 | item_cf |
| 127 | Godfather, The (1972) | 0.245316 | item_cf |
| 182 | GoodFellas (1990) | 0.241382 | item_cf |
| 187 | Godfather: Part II, The (1974) | 0.233212 | item_cf |
