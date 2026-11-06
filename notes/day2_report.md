# Báo cáo Day 2 — Huy (ML core + tích hợp, bản remote trước tích hợp)

## Đã xong

- `src/models/content_based.py`: `ContentBasedRecommender` với genre-only 18 thể loại, chuẩn hóa L2, cosine similarity, mapping phim và fallback Popularity.
- `src/service/recommender_service.py`: đăng ký `content_based`, hỗ trợ `recommend` và `similar_items(method=...)`, fallback Popularity khi model chưa sẵn sàng.
- `tests/test_content_based.py`: 12 unit test với DataFrame giả, không phụ thuộc dữ liệu thật.
- `notes/day2_report.md`: báo cáo này.

## Kiểm tra

```text
pytest -q        -> 28 passed
ruff check .     -> All checks passed
app boundary     -> app/ không import trực tiếp src.models
```

- Top-10 content-based cho user `1`, `196`, `405`: không có phim đã xem trong train.
- User `999999`: fallback Popularity, method `popularity`, reason `Fallback phổ biến (cold-start)`.
- `similar_items` mặc định dùng `content_based`; phim không tồn tại raise `ValueError`.
- Method chưa hỗ trợ raise `ValueError: Method item_cf sẽ có từ Day 3/4`.

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

## Hạn chế

- Genre-only nên gợi ý còn thô, các phim cùng thể loại có score bằng nhau rất nhiều.
- Chưa dùng title, mô tả, diễn viên; chưa có rating metrics/ranking metrics cho Content-Based.
- Cold-start và phim không có thể loại phụ thuộc Popularity.
- Similarity matrix `1682 × 1682` float32 khoảng 11 MB, chấp nhận được.

## Blocker và đề xuất Day 3

- Chờ Phong chạy smoke script/đánh giá định tính và Linh cập nhật app/README để review, merge PR.
- Day 3: Item-CF, ranking metrics Precision@K/Recall@K/NDCG@K, đánh giá định lượng cho Content-Based.


---

# Báo cáo Day 2

- Đã triển khai ContentBasedRecommender với 18 thể loại, cosine similarity, profile từ train và Popularity fallback. Không thay đổi contract base.
- Service hỗ trợ hai phương pháp; Similar Movies mặc định Content-Based. Hồ sơ user chuyển sang train để tránh dùng lịch sử test.
- Recommendations chọn được hai phương pháp; Similar Movies và Compare hoạt động; card hiển thị method và reason. Home và README đã cập nhật.
- Smoke test dữ liệu thật pass cho user 1, 196, 405 và Toy Story, Star Wars, Pulp Fiction; user lạ và hai phim không genre fallback đúng. Chi tiết trong day2_eval.md.
- Local sau tích hợp remote: toàn bộ 38 test pass, gồm test Surprise, 12 test từ PR #7 và test hồi quy k không dương. Ruff và hai smoke script pass. AppTest chạy Home, 5 trang và các tương tác chính.
- Đã cài MSVC và Windows SDK bằng Microsoft Build Tools trên ổ D, sau đó build và cài thành công scikit-surprise 1.1.4. Không bỏ qua test Surprise trong CI.
- Nhánh tích hợp: feat/day2-integration; giữ lịch sử của origin/feat/content-based và không push đè nhánh chung của PR #7. PR tích hợp được chuẩn bị riêng, chờ review trước khi merge.
- CI tạo dữ liệu bằng download/preprocess/splits trước pytest và chạy cả hai smoke script. AppTest bắt buộc có dữ liệu khi CI chạy, không tự skip do thiếu dữ liệu.
- Kiểm tra Chrome trực tiếp chưa hoàn tất: công cụ báo Computer Use app approval timed out. Đã kiểm chứng các luồng chính bằng Streamlit AppTest, không coi đây là kiểm tra trực quan bằng trình duyệt.
- Hạn chế: genre-only có nhiều điểm bằng nhau; chưa có ranking metrics. Day 3 tiếp tục Item-CF và đánh giá xếp hạng.
