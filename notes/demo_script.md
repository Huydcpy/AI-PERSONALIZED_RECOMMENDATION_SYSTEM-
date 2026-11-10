# Kịch bản demo — Day 5

**Thời lượng:** 5–7 phút  
**Sản phẩm:** AI Personalized Recommendation System (MovieLens 100K)

## Phân công trình bày

| Thời gian | Người trình bày | Nội dung chính |
|---|---|---|
| 0:00–1:30 | Huy | Mở đầu, bài toán, kiến trúc hệ thống (App → Service → Models), 5 phương pháp |
| 1:30–3:00 | Phong | Số liệu đánh giá: Rating Prediction và Ranking Metrics, phân tích trade-off |
| 3:00–6:30 | Linh | Demo trực tiếp trên Streamlit app, fallback cases, kết luận ngắn |
| 6:30–7:00 | Cả nhóm | Q&A |

## Dữ liệu mẫu và kịch bản demo

### User mẫu
- **User 1**
- **User 196**
- **User 405**

### Phim mẫu
- **Movie 1:** Toy Story (1995)
- **Movie 50:** Star Wars (1977)
- **Movie 56:** Pulp Fiction (1994)

### Kịch bản fallback
- **User mới / user không tồn tại:** nhập/chọn user ngoài tập train (ví dụ user lạ) → hệ thống fallback về Popularity, hiển thị `method`/`reason` thực tế, không crash.
- **User thưa dữ liệu / thiếu lịch sử trong train:** user có ít hoặc không có tín hiệu phù hợp → model thiếu dữ liệu, service áp dụng fallback phù hợp để vẫn trả gợi ý.
- **Kiểm tra `exclude_seen=True`:** danh sách Top-K không chứa phim user đã xem.

## Kịch bản chi tiết

### 1. Mở đầu & kiến trúc (Huy, 0:00–1:30)

- Giới thiệu bài toán: gợi ý phim cá nhân hóa trên MovieLens 100K, pipeline end-to-end data → model → service → Streamlit.
- Trình bày kiến trúc: App chỉ gọi `RecommenderService`, service quản lý dữ liệu/model/metrics và fallback.
- Liệt kê 5 phương pháp và method key: `popularity`, `content_based`, `item_cf`, `svd`, `hybrid`.

**Điểm nhấn:** chống leakage (train-only fit, test chỉ đánh giá), contract thống nhất, fallback rõ ràng.

### 2. Phân tích số liệu & metrics (Phong, 1:30–3:00)

- **Rating Prediction (từ `reports/metrics/baseline.json`, `reports/metrics/svd.json`):**
  - Popularity: RMSE 1.066985, MAE 0.863097 (baseline Day 1, giữ nguyên).
  - SVD: RMSE 0.956120, MAE 0.752447 → cải thiện ~10,39% RMSE và ~12,82% MAE.
- **Ranking Metrics @10 (từ `reports/metrics/ranking.json`, 456 users đánh giá, 487 skipped, relevance >= 4.0):**
  - Popularity: NDCG@10 0.174714 (cao nhất), Coverage@10 0.023187.
  - Item-CF: Coverage@10 0.508323 (cao nhất), NDCG@10 0.031481.
  - SVD: NDCG@10 0.137267, Coverage@10 0.105826.
  - Hybrid: NDCG@10 0.109632, Coverage@10 0.315101.
  - Content-Based: NDCG@10 0.055068, Coverage@10 0.237812.

**Điểm nhấn:** Popularity mạnh về NDCG trên split này; SVD tốt hơn về dự đoán rating nhưng không vượt Popularity về ranking; Hybrid đánh đổi và không tốt nhất mọi tiêu chí.

### 3. Demo trực tiếp trên App (Linh, 3:00–6:30)

#### 3.1 Home / tổng quan (ngắn)
- Mở `streamlit run app/Home.py`, giới thiệu các trang: Recommendations, Similar Movies, Compare Methods, Evaluation.

#### 3.2 Recommendations (Top-K gợi ý)
- Chọn **User 196**, K=10.
- Xem **Top-10 SVD** (`method=svd`) và **Top-10 Hybrid** (`method=hybrid`).
- Nhấn mạnh hiển thị `score`, `method`, `reason` thực tế; xác nhận `exclude_seen=True`.
- (Nếu còn thời gian) chuyển nhanh User 1 hoặc User 405 để thấy khác biệt cá nhân hóa.

#### 3.3 Similar Movies
- Chọn **Movie 1 (Toy Story, 1995)** → xem phim tương tự theo **SVD** và **Hybrid**.
- Chọn nhanh **Movie 50 (Star Wars, 1977)** hoặc **Movie 56 (Pulp Fiction, 1994)** để minh họa.

#### 3.4 Compare Methods
- Chọn **User 196**, K=10, so sánh 5 phương pháp trên cùng một user: Popularity, Content-Based, Item-CF, SVD, Hybrid.
- Quan sát sự khác nhau về danh sách, score và coverage/đa dạng.

#### 3.5 Evaluation
- Mở trang Evaluation: hiển thị bảng RMSE/MAE (Popularity vs SVD) và bảng ranking metrics cho 5 phương pháp, khớp với `reports/metrics/*.json`.

#### 3.6 Fallback cases
- Thử **user lạ / user không tồn tại** → nhận gợi ý fallback Popularity, app không crash.
- Minh họa **user thưa dữ liệu** (hoặc user không có lịch sử trong train) → fallback/hành vi theo service.
- Nhắc lại: với `exclude_seen=True`, không trả phim đã xem.

### 4. Kết luận & Q&A (6:30–7:00)

- Tóm tắt: hệ thống hoàn chỉnh 5 phương pháp, có đánh giá định lượng và demo trực quan.
- Nêu hạn chế chính: dữ liệu cũ/thưa, một split, feature genre thô, score khác thang đo.
- Trả lời câu hỏi: vì sao Popularity dẫn đầu NDCG@10, SVD tốt rating nhưng chưa dẫn ranking, Hybrid trade-off, cách xử lý cold-start/leakage.

## Checklist trước demo

- [ ] Dữ liệu đã chuẩn bị (`data/processed/`), app chạy được: `streamlit run app/Home.py`
- [ ] Kiểm tra nhanh: User 1/196/405, Phim 1/50/56
- [ ] Xác nhận trang Evaluation hiển thị đúng số liệu từ JSON
- [ ] Thử 1 fallback case (user lạ) và `exclude_seen=True`
- [ ] Chuẩn bị phương án dự phòng: screenshot trong `reports/figures/day5_*.png`
- [ ] Warm cache trước khi demo để giảm thời gian chờ
