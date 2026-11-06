# Báo cáo Day 2 — Trạng thái cuối (07/11/2026)

## Đã xong

- `src/models/content_based.py`: `ContentBasedRecommender` với genre-only 18 thể loại, chuẩn hóa L2, cosine similarity, mapping phim và fallback Popularity.
- `src/service/recommender_service.py`: đăng ký `content_based`, hỗ trợ `recommend` và `similar_items(method=...)`, fallback Popularity khi model chưa sẵn sàng.
- `tests/test_content_based.py`: 12 unit test với DataFrame giả, không phụ thuộc dữ liệu thật.
- `scripts/smoke_content_based.py`: kiểm tra dữ liệu thật cho 3 user, 3 phim, cold-start và phim không genre.
- App: Recommendations chọn Popularity/Content-Based, Similar Movies dùng Content-Based mặc định, Compare/Home đã cập nhật, card hiển thị method và reason.
- Tài liệu: `notes/day2_eval.md`, `notes/day2_review.md`, `notes/day2_report.md`, README và CI.

## Kiểm tra

```text
pytest -q        -> 41 passed
ruff check .     -> All checks passed
app boundary     -> app/ không import trực tiếp src.models
smoke content    -> pass (user 1/196/405, 3 phim, fallback 999999 và phim 267/1373)
smoke surprise   -> RMSE 0.9540
CI GitHub Actions -> success tại commit 7804b97
```

- Top-10 content-based cho user `1`, `196`, `405`: không có phim đã xem trong train.
- User `999999`: fallback Popularity, method `popularity`, reason `Fallback phổ biến (cold-start)`.
- `similar_items` mặc định dùng `content_based`; phim không tồn tại raise `ValueError`.
- Method chưa hỗ trợ raise `ValueError: Method item_cf sẽ có từ Day 3/4`.
- Streamlit chạy headless: health check OK, root HTTP 200; ảnh Home tại `reports/figures/day2_home.png`. AppTest phủ Home, 5 trang, 3 user và 3 phim.

## Ví dụ

User `196`, top-5 content-based:

| movie_id | score | reason | title |
|---|---|---|---|
| 34 | 0.9136 | Khớp thể loại: Comedy, Drama | Doom Generation, The (1995) |
| 45 | 0.9136 | Khớp thể loại: Comedy, Drama | Eat Drink Man Woman (1994) |
| 47 | 0.9136 | Khớp thể loại: Comedy, Drama | Ed Wood (1994) |
| 65 | 0.9136 | Khớp thể loại: Comedy, Drama | What's Eating Gilbert Grape (1993) |
| 93 | 0.9136 | Khớp thể loại: Comedy, Drama | Welcome to the Dollhouse (1995) |

Phim `1` (Toy Story), top-5 tương tự:

| movie_id | score | reason | title |
|---|---|---|---|
| 422 | 1.0000 | Cùng thể loại: Animation, Children, Comedy | Aladdin and the King of Thieves (1996) |
| 95 | 0.8660 | Cùng thể loại: Animation, Children, Comedy | Aladdin (1992) |
| 1219 | 0.8660 | Cùng thể loại: Animation, Children, Comedy | Goofy Movie, A (1995) |
| 63 | 0.8165 | Cùng thể loại: Children, Comedy | Santa Clause, The (1994) |
| 94 | 0.8165 | Cùng thể loại: Children, Comedy | Home Alone (1990) |

Phim `50` (Star Wars), top-3 tương tự:

| movie_id | score | reason | title |
|---|---|---|---|
| 181 | 1.0000 | Cùng thể loại: Action, Adventure, Romance, Sci-Fi, War | Return of the Jedi (1983) |
| 172 | 0.9129 | Cùng thể loại: Action, Adventure, Romance, Sci-Fi, War | Empire Strikes Back, The (1980) |
| 271 | 0.8944 | Cùng thể loại: Action, Adventure, Sci-Fi, War | Starship Troopers (1997) |

## Tích hợp và CI

- PR #7 (model/service/test), PR #8 (tích hợp Day 2) và PR #10 (Linh Day 2) đã được merge vào `main`; PR #5 đã đóng.
- CI tạo dữ liệu bằng download/preprocess/splits trước pytest, chạy `ruff check .`, kiểm tra boundary app, pytest và cả hai smoke script.
- AppTest bắt buộc có dữ liệu khi CI chạy, không tự skip do thiếu dữ liệu.
- Review hồi cứu được ghi tại `notes/day2_review.md`. Repo chỉ có một tài khoản maintainer nên GitHub không thể có approval chéo; toàn bộ kiểm tra đã được chạy lại trước khi chốt.

## Hạn chế

- Genre-only nên gợi ý còn thô, các phim cùng thể loại có score bằng nhau rất nhiều.
- Chưa dùng title, mô tả, diễn viên; chưa có rating metrics/ranking metrics cho Content-Based.
- Cold-start và phim không có thể loại phụ thuộc Popularity.
- Similarity matrix `1682 × 1682` float32 khoảng 11 MB, chấp nhận được.

## Đề xuất Day 3

- Item-CF, ranking metrics Precision@K/Recall@K/NDCG@K, đánh giá định lượng cho Content-Based.
