# Đánh giá Day 4 — Phong

Ngày 09/11/2026. Base: ea4a550. Phạm vi: rating SVD, ranking 5 phương pháp, smoke SVD/Hybrid và review tích hợp.

## Protocol

Fit chỉ dùng 80.000 ratings train; 20.000 ratings test chỉ dùng đánh giá, không tune. SVD: factors=100, epochs=20, lr=0.005, reg=0.02, seed=42. Hybrid giữ trọng số recommend 0.5/0.3/0.2 và similar 0.4/0.3/0.3 như phân công. Chạy lại chỉ để kiểm tra tái lập, không thay cấu hình theo kết quả test.

Ranking: relevance >=4, K=5/10/20, K chính 10; macro-average trên 456 user, bỏ 487 user không có relevant item. Coverage chia toàn catalog 1.682 phim, gồm 32 phim không tương tác train. 487/943 user bị bỏ là đặc tính split, không phải lỗi model; kết quả chỉ đại diện nhóm có relevant test. Fallback được tính trong metrics.

## Rating prediction

| Model | RMSE | MAE |
|---|---:|---:|
| Popularity | 1.066985 | 0.863097 |
| SVD | 0.956120 | 0.752447 |

SVD cải thiện RMSE khoảng 10,39% và MAE khoảng 12,82% so với Popularity. Baseline Day 1 giữ nguyên. Không claim rating metrics cho các phương pháp còn lại.

## Ranking

| Model | Precision@5 | Precision@10 | Recall@10 | NDCG@10 | Coverage@10 |
|---|---:|---:|---:|---:|---:|
| Popularity | 0.163158 | 0.164474 | 0.070910 | 0.174714 | 0.023187 |
| Content-Based | 0.058772 | 0.047368 | 0.022264 | 0.055068 | 0.237812 |
| Item-CF | 0.028947 | 0.029167 | 0.018530 | 0.031481 | 0.508323 |
| SVD | 0.136842 | 0.127851 | 0.048426 | 0.137267 | 0.105826 |
| Hybrid | 0.108333 | 0.100658 | 0.040805 | 0.109632 | 0.315101 |

Popularity tốt nhất NDCG@10; Item-CF tốt nhất coverage. Hybrid thấp hơn SVD và Popularity về Precision/Recall/NDCG@10, cao hơn Content-Based và Item-CF. Hybrid tăng coverage so với SVD nhưng thấp hơn Item-CF. Không có bằng chứng Hybrid cải thiện mọi tiêu chí; không đổi trọng số để che kết quả. Popularity chỉ phủ khoảng 2,32% catalog, phản ánh thiên lệch phim phổ biến. SVD cải thiện dự đoán rating không đồng nghĩa dẫn đầu ranking.

Ranking thực tế: 18,35 giây cho toàn lệnh, gồm khởi tạo model, fit và ghi báo cáo; đạt mục tiêu dưới 5 phút. Số liệu JSON được sinh bằng script, không sửa tay. Mỗi model có đủ 10 metrics; 3 model Day 3 giữ nguyên số liệu.

## Smoke và kiểm chứng

- Top-10 không trùng, thuộc catalog, không chứa phim đã xem cho user 1/196/405; ghi top-5 bên dưới.
- Similar top-5 SVD/Hybrid cho Toy Story (1), Star Wars (50), Pulp Fiction (56), loại chính nó, có item native.
- Method/reason và score được kiểm tra theo thang native; fallback Popularity giữ thang rating [1,5].
- User 999999 và user 196 metadata-only đều fallback Popularity cho cả hai phương pháp.
- Tạm bỏ tương tác phim 1: SVD similar fallback Popularity; dữ liệu gốc không đổi, dùng TemporaryDirectory.
- Movie ID không tồn tại raise ValueError ở cả SVD và Hybrid.
- SVD vector hóa khớp Surprise trên 9 cặp known, sai số lớn nhất 8,881784197001252e-16, dưới 1e-6.
- Kết quả gọi lại cho 3 user và 3 phim giống nhau.
- Phát hiện và sửa Hybrid cold-start thiếu reason fallback; thêm assertion hồi quy.
- AppTest xác nhận 3 user/3 phim SVD/Hybrid, Compare 5 tab/50 cards, Evaluation 2 dòng rating và 5 dòng ranking.

## Giới hạn và bàn giao

Không tune trên test, chưa có implicit feedback, score giữa phương pháp khác thang đo. Similar SVD có thể không gần nhau về thể loại vì dùng latent factors. Một split và một seed chưa chứng minh khác biệt có ý nghĩa thống kê. Không giảm K hoặc đổi pool theo test.

Bàn giao cho Huy/Linh: scripts/run_svd_eval.py, scripts/run_ranking_eval.py, scripts/smoke_svd_hybrid.py, reports/metrics/svd.json, reports/metrics/ranking.json và docs/evaluation_protocol.md. Review chi tiết tại notes/day4_review.md. Chưa push, chưa mở PR, chưa có approval độc lập hoặc bằng chứng CI remote.

## Ví dụ thực tế

Top-5 dưới đây là prefix của recommend K=10; Hybrid phụ thuộc pool max(50, 3*K), nên cần ghi rõ K khi tái lập. Similar chạy K=5.

### users / svd / 1

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 603 | Rear Window (1954) | 4.772256 | svd |
| 12 | Usual Suspects, The (1995) | 4.758784 | svd |
| 134 | Citizen Kane (1941) | 4.725992 | svd |
| 318 | Schindler's List (1993) | 4.692015 | svd |
| 180 | Apocalypse Now (1979) | 4.642260 | svd |

### users / svd / 196

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 483 | Casablanca (1942) | 4.287311 | svd |
| 408 | Close Shave, A (1995) | 4.278069 | svd |
| 169 | Wrong Trousers, The (1993) | 4.265532 | svd |
| 318 | Schindler's List (1993) | 4.255841 | svd |
| 923 | Raise the Red Lantern (1991) | 4.253564 | svd |

### users / svd / 405

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 144 | Die Hard (1988) | 3.932542 | svd |
| 172 | Empire Strikes Back, The (1980) | 3.663702 | svd |
| 96 | Terminator 2: Judgment Day (1991) | 3.452524 | svd |
| 121 | Independence Day (ID4) (1996) | 3.446546 | svd |
| 705 | Singin' in the Rain (1952) | 3.277217 | svd |

### users / hybrid / 1

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 236 | Citizen Ruth (1996) | 0.500000 | hybrid |
| 345 | Deconstructing Harry (1997) | 0.500000 | hybrid |
| 603 | Rear Window (1954) | 0.500000 | hybrid |
| 953 | Unstrung Heroes (1995) | 0.500000 | hybrid |
| 1237 | Twisted (1996) | 0.500000 | hybrid |

### users / hybrid / 196

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 127 | Godfather, The (1972) | 0.602944 | hybrid |
| 481 | Apartment, The (1960) | 0.500000 | hybrid |
| 483 | Casablanca (1942) | 0.500000 | hybrid |
| 408 | Close Shave, A (1995) | 0.487263 | hybrid |
| 169 | Wrong Trousers, The (1993) | 0.469986 | hybrid |

### users / hybrid / 405

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 144 | Die Hard (1988) | 0.578132 | hybrid |
| 172 | Empire Strikes Back, The (1980) | 0.512474 | hybrid |
| 96 | Terminator 2: Judgment Day (1991) | 0.415756 | hybrid |
| 316 | As Good As It Gets (1997) | 0.389535 | hybrid |
| 121 | Independence Day (ID4) (1996) | 0.327572 | hybrid |

### similar / svd / 1

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 45 | Eat Drink Man Woman (1994) | 0.405460 | svd |
| 378 | Miracle on 34th Street (1994) | 0.348896 | svd |
| 979 | Trigger Effect, The (1996) | 0.343406 | svd |
| 174 | Raiders of the Lost Ark (1981) | 0.339268 | svd |
| 1459 | Madame Butterfly (1995) | 0.335045 | svd |

### similar / svd / 50

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 181 | Return of the Jedi (1983) | 0.664296 | svd |
| 172 | Empire Strikes Back, The (1980) | 0.649586 | svd |
| 174 | Raiders of the Lost Ark (1981) | 0.446042 | svd |
| 1594 | Everest (1998) | 0.288834 | svd |
| 228 | Star Trek: The Wrath of Khan (1982) | 0.287425 | svd |

### similar / svd / 56

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 93 | Welcome to the Dollhouse (1995) | 0.358159 | svd |
| 127 | Godfather, The (1972) | 0.357513 | svd |
| 475 | Trainspotting (1996) | 0.332093 | svd |
| 182 | GoodFellas (1990) | 0.323840 | svd |
| 180 | Apocalypse Now (1979) | 0.307185 | svd |

### similar / hybrid / 1

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 174 | Raiders of the Lost Ark (1981) | 0.606314 | hybrid |
| 50 | Star Wars (1977) | 0.356538 | hybrid |
| 28 | Apollo 13 (1995) | 0.316084 | hybrid |
| 45 | Eat Drink Man Woman (1994) | 0.312127 | hybrid |
| 95 | Aladdin (1992) | 0.303779 | hybrid |

### similar / hybrid / 50

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 181 | Return of the Jedi (1983) | 1.000000 | hybrid |
| 172 | Empire Strikes Back, The (1980) | 0.859386 | hybrid |
| 174 | Raiders of the Lost Ark (1981) | 0.452337 | hybrid |
| 173 | Princess Bride, The (1987) | 0.247580 | hybrid |
| 271 | Starship Troopers (1997) | 0.213829 | hybrid |

### similar / hybrid / 56

| movie_id | Title | Score | Method |
|---|---|---:|---|
| 182 | GoodFellas (1990) | 0.914443 | hybrid |
| 127 | Godfather, The (1972) | 0.808656 | hybrid |
| 180 | Apocalypse Now (1979) | 0.494007 | hybrid |
| 187 | Godfather: Part II, The (1974) | 0.468407 | hybrid |
| 475 | Trainspotting (1996) | 0.434990 | hybrid |

## Xác minh cuối

106 tests pass, lint pass, smoke SVD/Hybrid pass. Chạy lại hai evaluator cho SHA-256 giống hệt ở cả svd.json và ranking.json. Baseline Day 1 không thay đổi. Checklist phần Phong trong task_day4_9_11.md đã được cập nhật; chưa đánh dấu phần Huy/Linh hoặc checklist chung.
