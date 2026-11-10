# Đánh giá cuối Day 5 — tổng hợp

Ngày 11/11/2026. Base tích hợp: `main` sau PR #19. Nguồn số liệu: `reports/metrics/baseline.json`, `reports/metrics/svd.json`, `reports/metrics/ranking.json`. Phần tổng hợp dựa trên evaluator và ghi chú Day 4 của Phong; Huy kiểm chứng lại và hợp nhất cho báo cáo cuối.

## Protocol

- Fit chỉ trên 80.000 ratings train; 20.000 ratings test chỉ dùng để đánh giá.
- SVD: `n_factors=100`, `n_epochs=20`, `lr_all=0.005`, `reg_all=0.02`, `random_state=42`.
- Hybrid: recommend `svd=0.5`, `item_cf=0.3`, `content_based=0.2`; similar `item_cf=0.4`, `svd=0.3`, `content_based=0.3`.
- Ranking: relevance `rating >= 4.0`; K `5/10/20`, K chính `10`; macro-average trên 456 user có relevant item; 487 user không có relevant item bị bỏ qua.
- Coverage@10 tính trên toàn catalog 1.682 phim.
- Không tune hyperparameter, trọng số, threshold hoặc K trên test.

## Rating prediction

| Model | RMSE | MAE | Ghi chú |
|---|---:|---:|---|
| Popularity | 1.066985 | 0.863097 | Baseline Day 1, giữ nguyên |
| SVD | 0.956120 | 0.752447 | Fit train-only, clip [1,5] |

SVD giảm khoảng **10,39% RMSE** và **12,82% MAE** so với Popularity. Đây là cải thiện trên bài toán dự đoán rating; không đồng nghĩa SVD dẫn đầu ranking.

![Rating metrics](../reports/figures/day5_rating_rmse_mae.png)

## Ranking metrics

| Model | Precision@5 | Precision@10 | Recall@10 | NDCG@10 | Coverage@10 |
|---|---:|---:|---:|---:|---:|
| Popularity | 0.163158 | 0.164474 | 0.070910 | 0.174714 | 0.023187 |
| Content-Based | 0.058772 | 0.047368 | 0.022264 | 0.055068 | 0.237812 |
| Item-CF | 0.028947 | 0.029167 | 0.018530 | 0.031481 | 0.508323 |
| SVD | 0.136842 | 0.127851 | 0.048426 | 0.137267 | 0.105826 |
| Hybrid | 0.108333 | 0.100658 | 0.040805 | 0.109632 | 0.315101 |

Thứ hạng NDCG@10: Popularity → SVD → Hybrid → Content-Based → Item-CF. Thứ hạng Coverage@10: Item-CF → Hybrid → Content-Based → SVD → Popularity.

![NDCG@10](../reports/figures/day5_ranking_ndcg10.png)

![Coverage@10](../reports/figures/day5_ranking_coverage10.png)

![NDCG vs Coverage](../reports/figures/day5_ndcg_vs_coverage.png)

## Phân tích

- **Popularity** dẫn đầu NDCG@10 và Precision/Recall@10 trên split này, nhưng chỉ phủ khoảng 2,32% catalog. Mô hình tận dụng popularity bias của MovieLens.
- **SVD** cải thiện rõ rating prediction nhưng NDCG@10 chỉ đạt 0,137267, thấp hơn Popularity. Dự đoán rating tốt không đảm bảo xếp hạng top-K tốt.
- **Hybrid** đạt NDCG@10 0,109632 và Coverage@10 0,315101; dung hòa giữa SVD và Item-CF nhưng chưa vượt SVD/Popularity về NDCG@10. Kết quả cho thấy trade-off giữa accuracy và đa dạng, không có bằng chứng Hybrid tốt nhất mọi tiêu chí.
- **Item-CF** có coverage cao nhất (0,508323) nhưng NDCG@10 thấp nhất (0,031481), phù hợp với dữ liệu thưa và tín hiệu item-item còn yếu.
- **Content-Based** có coverage 0,237812 nhưng NDCG@10 0,055068; đặc trưng genre thô tạo nhiều tie và chưa đủ phân biệt sở thích.
- 487/943 user bị bỏ khỏi ranking metrics do không có relevant item trong test; kết quả đại diện nhóm user có relevant item, không phải toàn bộ người dùng.

## Fallback và kiểm chứng

- User 999999 fallback Popularity với reason cold-start.
- User metadata-only fallback Popularity.
- Phim zero-interaction: SVD similar fallback Popularity.
- Movie ID không tồn tại raise `ValueError`.
- `exclude_seen=True` không trả phim đã xem trong top-10.
- SVD vector hóa khớp Surprise trên các cặp known; sai số tối đa khoảng `8,88e-16`.
- Kết quả gọi lại cho 3 user và 3 phim giống nhau; evaluator tái lập SHA-256.
- AppTest xác nhận 5 phương pháp, Compare 5 tab/50 card, Evaluation 2 bảng.

## Tái lập

```bash
pytest -q
ruff check .
python scripts/run_svd_eval.py
python scripts/run_ranking_eval.py
python scripts/smoke_svd_hybrid.py
python scripts/make_day5_figures.py
```

Kết quả local: 106 test pass; lint pass; SVD evaluation khoảng 1,42 giây; ranking evaluation khoảng 15,09 giây; warm service khoảng 0,09 giây cho 12 lời gọi; Streamlit trả HTTP 200. Baseline Day 1 không thay đổi.

## Hạn chế

- MovieLens 100K có từ 1997–1998, chủ yếu explicit feedback, độ thưa khoảng 93,7%.
- Một split và một seed; chưa có cross-validation hoặc kiểm định thống kê.
- Chưa có implicit feedback, metadata phong phú hoặc fairness analysis.
- Score giữa các phương pháp khác thang đo nên không so sánh trực tiếp.
- Kết quả ranking không đại diện cho 487 user không có relevant item trong test.

## Kết luận

Hệ thống đã có đủ 5 phương pháp, đánh giá rating và ranking, fallback rõ ràng và app demo end-to-end. Kết quả thực tế cho thấy Popularity vẫn là baseline mạnh về NDCG@10, SVD cải thiện rating, Item-CF tăng coverage, còn Hybrid là điểm cân bằng nhưng chưa vượt các baseline về accuracy. Báo cáo tổng hợp: [day5_report.md](day5_report.md).
