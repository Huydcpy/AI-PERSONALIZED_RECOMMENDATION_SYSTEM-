# Evaluation Protocol — Day 4

Đánh giá 5 phương pháp: Popularity, Content-Based, Item-CF, SVD, Hybrid trên MovieLens 100K: train u1.base 80.000 ratings, test u1.test 20.000 ratings; 943 users và 1.682 movies.

## Chống leakage và tái lập

Chỉ dùng train để fit, tạo profile, similarity và lịch sử đã xem. Validate file không rỗng, rating hợp lệ, catalog duy nhất, phim train/test thuộc catalog, không overlap cặp (user_id, movie_id). Test chỉ dùng đánh giá cuối với cấu hình chốt trước; không chọn model, hyperparameter, trọng số, pool hoặc ngưỡng từ test. Chạy lại để xác minh tái lập không phải vòng tuning. Seed cố định 42. Chưa tune SVD/Hybrid; kết quả kém baseline vẫn phải báo cáo.

## Rating metrics

RMSE = sqrt(mean((y_true-y_pred)^2)); MAE = mean(abs(y_true-y_pred)).

Popularity dùng Bayesian average với m=50: score = v/(v+m)*R + m/(v+m)*C; v là số rating phim, R là trung bình phim, C là trung bình train. Giữ nguyên reports/metrics/baseline.json và kết quả Day 1. Khoảng RMSE tham khảo 0,95–1,10.

SVD dùng Surprise: n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02, random_state=42. Chỉ fit train. Chạy `python scripts/run_svd_eval.py`: gọi predict_rating từng cặp test, kiểm tra dự đoán hữu hạn trong [1, 5], tính RMSE/MAE, ghi reports/metrics/svd.json qua file tạm rồi replace. Lỗi không ghi đè báo cáo cũ. RMSE ngoài [0,5; 1,5] phải cảnh báo. Không claim rating metrics cho Content-Based, Item-CF, Hybrid khi chưa có predict_rating.

## Ranking metrics

- Relevant: rating test >= 4.0.
- K = 5, 10, 20; K chính = 10.
- Candidate chung: toàn catalog trừ lịch sử train, không negative sampling. SVD native chỉ xét phim có factor train; Popularity bổ sung khi thiếu.
- Gọi recommend một lần/user/model với K=20, exclude_seen=True; dùng prefix cho K nhỏ hơn.
- Duplicate chỉ tính lần đầu, giữ thứ tự trả về.
- Sort score giảm dần, tie-break movie_id tăng dần. Fallback nối sau native, không sort lại hai thang điểm.

Với R(u) là relevant, L_K(u) là top-K sau loại duplicate:

```text
Precision@K(u) = |R(u) ∩ L_K(u)| / K
Recall@K(u) = |R(u) ∩ L_K(u)| / |R(u)|
DCG@K(u) = sum(1 / log2(rank + 1)) tại vị trí relevant, rank bắt đầu từ 1
IDCG@K(u) = sum(1 / log2(rank + 1)), rank = 1..min(|R(u)|, K)
NDCG@K(u) = DCG@K(u) / IDCG@K(u)
Coverage@10 = |union(L_10(u))| / số phim trong movies
```

Precision vẫn chia K nếu trả thiếu. Hàm metric trả 0 khi relevant rỗng; evaluator bỏ user đó khỏi macro-average. Xét hợp user train/test; n_users_skipped đếm user không có relevant test. Không có user hợp lệ thì báo lỗi. Cả 5 model dùng cùng tập user. Coverage dùng toàn catalog, kể cả phim không tương tác train. Kết quả tính cả fallback Popularity. Giữ nguyên relevance, K, macro-average và mẫu số coverage của Day 3.

`python scripts/run_ranking_eval.py` ghi reports/metrics/ranking.json: config, số user đánh giá/bỏ qua, 9 ranking metrics và coverage@10 mỗi model. Yêu cầu đủ 5 model và module metrics. Kiểm tra kết quả thuộc catalog, không chứa phim đã xem; loại duplicate theo quy ước trên. Thiếu dependency hoặc metric không hữu hạn/ngoài [0, 1] thì exit khác 0, không ghi đè báo cáo. Ghi file tạm rồi replace.

## SVD và Hybrid

SVD recommend vector hóa mu+b_u+b_i+p_u·q_i, clip [1, 5]; kiểm chứng khớp Surprise với dung sai 1e-6. Similar dùng cosine latent factors, clip âm về 0, bỏ chính nó; phim không có factor fallback Popularity.

Hybrid lấy pool max(50, k*3), chỉ blend item native có method trùng component. Min-max normalize từng danh sách; max=min thì gán 1. Trọng số recommend: SVD 0.5, Item-CF 0.3, Content-Based 0.2. Similar: Item-CF 0.4, SVD 0.3, Content-Based 0.3. Item vắng đóng góp 0. Fill Popularity sau blend, chống trùng; cold-start fallback Popularity.

Score Hybrid native trong [0, 1]; fallback giữ thang Popularity. Không so sánh raw score giữa phương pháp hoặc giữa native/fallback. Chưa có implicit feedback; một split cố định không chứng minh hiệu quả trên mọi dữ liệu.
