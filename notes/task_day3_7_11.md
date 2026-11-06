# TASK DAY 3 — 07/11/2026

## Hướng dẫn chi tiết cho 3 thành viên

**Dự án:** AI Personalized Recommendation System (MovieLens 100K)

**Mục tiêu Day 3:** có **Item-CF** và **ranking metrics** hoàn chỉnh:
**user → top-K theo Item-CF → so sánh 3 phương pháp → Precision@K / Recall@K / NDCG@K trên Streamlit**.

**Demo cuối ngày:**
- Chọn 3 user khác nhau, xem top-10 Item-CF.
- Chọn 3 phim khác nhau, xem phim tương tự theo Item-CF.
- So sánh Popularity / Content-Based / Item-CF trên cùng một user.
- Trang Evaluation hiển thị bảng ranking metrics của 3 phương pháp.
- Kiểm tra fallback với user lạ và user không có rating trong train.
- Không có phim đã xem trong top-K khi `exclude_seen=True`.

---

## 0. PHÂN CÔNG TỔNG QUAN

| Thành viên | Vai trò | Phụ trách chính | Deliverable | Branch |
|---|---|---|---|---|
| **Huy (Trưởng nhóm)** | ML core + tích hợp | Item-CF model, ranking metrics, service, unit test, review, merge | `src/models/item_cf.py`, `src/evaluation/ranking_metrics.py`, `src/service/recommender_service.py`, `tests/test_item_cf.py`, `tests/test_ranking_metrics.py` | `feat/item-cf-ranking` |
| **Phong** | Data & Evaluation | Evaluation protocol, ranking evaluation, smoke script, đánh giá định tính | `scripts/run_ranking_eval.py`, `scripts/smoke_item_cf.py`, `reports/metrics/ranking.json`, `notes/day3_eval.md` | `feat/item-cf-ranking` |
| **Linh** | Product & Integration | App Recommendations / Similar / Compare / Evaluation, README, CI, PR | `app/pages/2_Recommendations.py`, `app/pages/3_Similar_Movies.py`, `app/pages/4_Compare_Methods.py`, `app/pages/5_Evaluation.py`, `README.md` | `feat/item-cf-ranking` |

**Nguyên tắc phối hợp:**
- Tất cả làm trên **một branch chung** `feat/item-cf-ranking` để tránh conflict.
- Huy chốt `ranking_metrics.py` và API Item-CF trước **10:30** để Phong và Linh tích hợp.
- Phong làm evaluation protocol và khung `run_ranking_eval.py` với Popularity trước, thêm Content-Based/Item-CF sau.
- Linh làm UI trước bằng method key `item_cf`, empty state nếu model chưa xong.
- Không ai sửa file của người khác khi chưa trao đổi.
- Review chéo qua PR trước khi merge.
- Không thêm comment/docstring mới vào code theo `AGENTS.md`.

### Quyết định kỹ thuật mặc định

- Item-CF là **item-item adjusted cosine** trên ma trận user-item của **train**, không dùng Surprise ở runtime.
- Hệ số trung bình theo user được trừ khỏi rating quan sát trước khi tính cosine.
- Giữ tối đa **50 láng giềng** mỗi phim để giảm nhiễu và tăng tốc.
- Method key: `item_cf`.
- Fallback: Popularity.
- Relevance threshold cho ranking metrics: `rating >= 4.0`.
- K đánh giá: `5`, `10`, `20`; K chính: `10`.
- Macro-average trên các user có ít nhất một relevant item trong test.
- Không đổi contract `src/models/base.py`.
- Không đọc test data khi fit/tạo profile.
- Không thêm dependency mới; `numpy`, `scipy`, `scikit-learn` đã có.
- Cập nhật thông báo method chưa hỗ trợ từ “Day 3/4” thành **“Day 4”**.
- `reports/metrics/ranking.json` được commit vì nhỏ và tất định.

### Trạng thái đầu vào

- Day 2 đã merge vào `main`, CI xanh tại commit `f2c64aa`.
- Service đã hỗ trợ `popularity` và `content_based`.
- App có 5 trang; trang Evaluation mới chỉ hiển thị baseline rating metrics.
- Data `train.parquet`, `test.parquet`, `movies.parquet` sẵn sàng.
- Toàn bộ 41 test hiện tại pass; `ruff check .` pass.
- `notes/day2_review.md` đã ghi nhận review Day 2.

### Việc cần dọn trước khi bắt đầu

- [ ] Sync local `main` lên `origin/main` mới nhất.
- [ ] Xác nhận `git status` sạch.
- [ ] Tạo branch `feat/item-cf-ranking`.
- [ ] Đọc lại `notes/task_day2_6_11.md`, `notes/day2_report.md`, `notes/day2_review.md`.
- [ ] Đọc `docs/evaluation_protocol.md` và thống nhất relevance threshold `4.0`.

**Lệnh gợi ý:**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch -c feat/item-cf-ranking
git status
```

---

## 1. MỐC THỜI GIAN & BÀN GIAO

| Giờ | Việc chung | Huy | Phong | Linh |
|---|---|---|---|---|
| 09:00–09:30 | Sync, chốt protocol ranking, tạo branch | Chủ trì | Tham gia | Tham gia |
| 09:30–10:30 | Ranking metrics + Item-CF core | Viết metrics, model | Cập nhật protocol | Review UI hiện tại |
| **10:30** | **Ranking metrics + Item-CF chạy được** | Báo tiến độ | Bắt đầu eval script | Bắt đầu page 2/3 |
| 10:30–11:30 | Service + test | Service, unit test | Khung `run_ranking_eval.py` | Page 2, method selector |
| 12:00 | Sync nhanh 5 phút | Báo tiến độ | Báo tiến độ | Báo tiến độ |
| 13:30–15:00 | App + đánh giá | Review/integration | Chạy ranking eval, smoke | Page 3/4/5, README |
| 15:00–15:45 | Smoke test, demo data | Chạy service | Tổng hợp ví dụ, `ranking.json` | Chạy AppTest |
| 15:45–16:30 | Review, CI, merge | Review/merge | Review | PR/CI |
| 16:30–17:00 | Chốt Day 3 | Viết báo cáo | Cập nhật eval | Cập nhật README |

---

## 2. HƯỚNG DẪN CHO HUY (TRƯỞNG NHÓM)

### 2.1 Mục tiêu cá nhân

Có `ItemCFRecommender` đúng contract, ranking metrics có test, tích hợp vào service, review và merge toàn bộ Day 3.

### 2.2 Phụ thuộc

- Day 2 đã merged; data và service sẵn sàng.
- Không phụ thuộc Phong/Linh để bắt đầu metrics và model.
- Service cần xong trước **11:30** để Linh tích hợp app.
- Phong cần ranking metrics và model/service trước **10:30** để chạy evaluation.

### 2.3 Checklist công việc chi tiết

#### Task 1 — Viết `src/evaluation/ranking_metrics.py`

API dự kiến:

```python
def precision_at_k(recommended, relevant, k: int) -> float: ...
def recall_at_k(recommended, relevant, k: int) -> float: ...
def ndcg_at_k(recommended, relevant, k: int) -> float: ...
```

Quy ước:
- [ ] `recommended` là danh sách `movie_id` đã sắp xếp theo thứ hạng.
- [ ] `relevant` là tập `movie_id` relevant của user trong test.
- [ ] Loại duplicate trong `recommended` sau lần xuất hiện đầu tiên.
- [ ] `k <= 0` raise `ValueError("k phải > 0")`.
- [ ] `precision@K = số relevant trong top-K / K` (K cố định, kể cả khi trả ít hơn K item).
- [ ] `recall@K = số relevant trong top-K / |relevant|`.
- [ ] Nếu `relevant` rỗng: precision = 0, recall = 0, NDCG = 0, không crash.
- [ ] `ndcg@K` dùng binary relevance:
  - `DCG@K = sum(1 / log2(rank + 1))` cho các vị trí relevant.
  - `IDCG@K` tính với `min(|relevant|, K)` vị trí relevant lý tưởng.
  - Nếu `IDCG = 0` thì trả `0.0`.
- [ ] Kết quả là `float` trong `[0, 1]` với precision, recall, NDCG.
- [ ] Không import model/service; module thuần túy.

#### Task 2 — Viết `src/models/item_cf.py`

**Ma trận và similarity:**

- [ ] Tạo mapping `user_id -> index`, `movie_id -> index` từ `train_df` và `movies_df`.
- [ ] Tạo ma trận thưa user-item từ train.
- [ ] Tính `user_mean` từ rating trong train; user không có rating dùng global mean.
- [ ] Center rating quan sát: `rating - user_mean`.
- [ ] Tính adjusted cosine giữa các item trên ma trận đã center.
- [ ] Clip similarity âm về `0`; đặt diagonal bằng `0`.
- [ ] Giữ tối đa `k_neighbors=50` láng giềng mỗi item; các giá trị còn lại bằng `0`.
- [ ] Lưu mapping:
  - `movie_ids`
  - `movie_id_to_index`
  - `index_to_movie_id`
  - `similarity`
- [ ] Phim không có tương tác: vector zero, không crash.
- [ ] Không dùng test data.

**API dự kiến:**

```python
class ItemCFRecommender:
    name = "item_cf"

    def __init__(
        self,
        train_df,
        movies_df,
        fallback=None,
        k_neighbors: int = 50,
    ):
        ...

    def recommend(
        self, user_id: int, k: int = 10, exclude_seen: bool = True
    ) -> list[Recommendation]:
        ...

    def similar_items(
        self, movie_id: int, k: int = 10
    ) -> list[Recommendation]:
        ...
```

**`recommend`:**

- [ ] Chỉ dùng rating của user trong `train_df`.
- [ ] Score cho item `i`:
  - Tử số: `sum(similarity[i, j] * centered_rating[u, j])` trên các item `j` user đã rating.
  - Mẫu số: `sum(abs(similarity[i, j]))` trên các item `j` user đã rating.
  - Nếu mẫu số bằng 0: score = 0.
- [ ] `predicted_rating = clip(user_mean + weighted_score, 1, 5)`.
- [ ] Chỉ giữ item có `weighted_score > 0` trước khi clip; dùng `predicted_rating` làm score trả về.
- [ ] `exclude_seen=True`: loại item user đã rating trong **train**.
- [ ] Sort `score` giảm dần, tie-break `movie_id` tăng dần.
- [ ] Trả tối đa `k`.
- [ ] Item Item-CF:
  - `method="item_cf"`.
  - reason `"Dựa trên phim tương tự bạn đã rating"`.
- [ ] User không có rating / profile rỗng:
  - fallback Popularity.
  - method `"popularity"`.
  - reason `"Fallback phổ biến (cold-start)"`.
- [ ] Không đủ item / không có tín hiệu:
  - fallback Popularity.
  - method `"popularity"`.
  - reason `"Fallback phổ biến (thiếu tín hiệu)"`.

**`similar_items`:**

- [ ] Lấy similarity vector của phim gốc.
- [ ] Loại chính nó.
- [ ] Chỉ giữ `score > 0`.
- [ ] Sort giảm dần, tie-break `movie_id`.
- [ ] `method="item_cf"`.
- [ ] reason `"Cùng gu người dùng"`.
- [ ] Phim không có tương tác / không có kết quả: fallback Popularity, reason `"Fallback phổ biến (thiếu tín hiệu)"`.
- [ ] Movie ID không tồn tại: raise `ValueError(f"Movie {movie_id} không tồn tại")`.
- [ ] `k <= 0`: trả danh sách rỗng.

#### Task 3 — Tích hợp service

Sửa `src/service/recommender_service.py`:

- [ ] Khởi tạo Popularity trước.
- [ ] Khởi tạo Content-Based với fallback Popularity.
- [ ] Khởi tạo Item-CF với fallback Popularity.
- [ ] Thêm `self.models["item_cf"]`.
- [ ] `recommend(..., method="item_cf")` hoạt động.
- [ ] `similar_items(..., method="item_cf")` hoạt động.
- [ ] Method chưa hỗ trợ:
  `ValueError(f"Method {method} sẽ có từ Day 4")`.
- [ ] Thêm `get_ranking_metrics() -> dict`:
  - Đọc `reports/metrics/ranking.json`.
  - Trả `{}` nếu chưa có.
- [ ] Giữ `get_baseline_metrics()`.
- [ ] Không đổi response contract.
- [ ] Service vẫn không import Streamlit.

#### Task 4 — Unit test

Tạo `tests/test_ranking_metrics.py`:
- [ ] Ví dụ tính tay:
  `recommended=[1,2,3,4,5]`, `relevant={2,4,6}`:
  - Precision@5 = 0.4
  - Recall@5 = 2/3
  - NDCG@5 ≈ 0.6509
- [ ] `k` lớn hơn độ dài danh sách.
- [ ] `relevant` rỗng.
- [ ] `k <= 0` raise `ValueError`.
- [ ] Duplicate trong `recommended` không được tính hai lần.
- [ ] Kết quả trong `[0, 1]`.

Tạo `tests/test_item_cf.py` với DataFrame giả:
- [ ] `similar_items` trả item tương tự trước.
- [ ] `similar_items` loại chính nó và tôn trọng `k`.
- [ ] `recommend` loại phim đã xem khi `exclude_seen=True`.
- [ ] User lạ fallback Popularity, không crash.
- [ ] User không có rating trong train fallback Popularity.
- [ ] Phim không có tương tác fallback.
- [ ] Kết quả deterministic khi score bằng nhau.
- [ ] Score trong `[1, 5]`.
- [ ] Method Item-CF là `"item_cf"`.
- [ ] Method fallback là `"popularity"`.
- [ ] `similar_items` movie không tồn tại raise `ValueError`.
- [ ] `k <= 0` trả danh sách rỗng.
- [ ] Không phụ thuộc data thật.

Cập nhật test service:
- [ ] `item_cf` đã đăng ký.
- [ ] `recommend` và `similar_items` với `item_cf` hoạt động.
- [ ] `get_ranking_metrics()` trả `{}` khi thiếu file và đọc đúng khi có file.
- [ ] Method invalid raise `ValueError` với thông báo “Day 4”.

#### Task 5 — Review & tích hợp

- [ ] Review evaluation protocol và script của Phong: đúng relevance threshold, không leakage.
- [ ] Review app của Linh: không import trực tiếp model, cache, error handling.
- [ ] Chạy:
  ```bash
  pytest -q
  ruff check .
  python scripts/smoke_item_cf.py
  python scripts/run_ranking_eval.py
  ```
- [ ] Kiểm tra `git status`: không có data/model lớn.
- [ ] Review PR, merge khi CI xanh.
- [ ] Viết `notes/day3_report.md`.

### 2.4 Lệnh kiểm tra của Huy

```bash
pytest tests/test_ranking_metrics.py tests/test_item_cf.py -q
pytest -q
ruff check .
python -c "from src.service.recommender_service import RecommenderService; s=RecommenderService(); print(s.recommend(196, method='item_cf', k=5))"
python scripts/smoke_item_cf.py
python scripts/run_ranking_eval.py
```

### 2.5 Tiêu chí hoàn thành

- [ ] `ItemCFRecommender` đúng contract.
- [ ] `recommend` trả top-K Item-CF cho user hợp lệ.
- [ ] `similar_items` trả phim tương tự, loại chính nó.
- [ ] User lạ / user không có rating fallback Popularity, không crash.
- [ ] Phim không có tương tác fallback Popularity.
- [ ] Service hỗ trợ `popularity`, `content_based`, `item_cf`.
- [ ] Ranking metrics đúng công thức, có test tính tay.
- [ ] Unit test pass, không phụ thuộc data thật.
- [ ] Review xong PR của Phong và Linh.
- [ ] PR được merge, CI xanh.
- [ ] Có báo cáo Day 3.

### 2.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Item-CF quá thưa, ít láng giềng | Fallback Popularity; báo coverage trong `ranking.json` |
| Tính similarity toàn ma trận tốn RAM | 1.682 item, ma trận ~11 MB float32; giữ top-50 láng giềng |
| Ranking eval chậm | Vector hóa theo batch, dùng ma trận thưa; mục tiêu < 2 phút |
| Popularity bias | Ghi rõ hạn chế; so sánh định lượng bằng ranking metrics |
| Content-Based ties | Tie-break `movie_id`; đã có từ Day 2 |
| Fallback che lỗi model | Ghi method và reason rõ ràng |
| Test phụ thuộc data thật | Dùng DataFrame giả |
| App import model trực tiếp | Giữ boundary, CI grep kiểm tra |

### 2.7 Báo cáo cuối ngày

Gửi nhóm 5 dòng:
- Đã xong: ...
- Model/method: ...
- Ranking metrics: ...
- Fallback/test: ...
- Blocker và đề xuất Day 4: ...

---

## 3. HƯỚNG DẪN CHO PHONG

### 3.1 Mục tiêu cá nhân

Chuẩn hóa evaluation protocol cho ranking, xây dựng script đánh giá định lượng, smoke test Item-CF và ghi nhận kết quả so sánh 3 phương pháp.

### 3.2 Phụ thuộc

- Data `train.parquet`, `test.parquet`, `movies.parquet` đã có.
- Ranking metrics và Item-CF của Huy trước **10:30** để chạy đánh giá.
- App của Linh trước **15:00** để đối chiếu kết quả hiển thị.
- Có thể viết khung `run_ranking_eval.py` với Popularity ngay từ đầu.

### 3.3 Checklist công việc chi tiết

#### Task 1 — Cập nhật `docs/evaluation_protocol.md`

- [ ] Ghi rõ relevance threshold: `rating >= 4.0`.
- [ ] Ghi rõ K đánh giá: `5`, `10`, `20`; K chính `10`.
- [ ] Ghi công thức Precision@K, Recall@K, NDCG@K.
- [ ] Ghi quy ước duplicate và tie-break.
- [ ] Ghi quy ước user không có relevant item bị bỏ qua.
- [ ] Ghi rõ test chỉ dùng một lần để đánh giá, không dùng để fit/tune.
- [ ] Ghi rõ ranking metrics dùng cho cả Popularity, Content-Based, Item-CF.
- [ ] Ghi rõ chưa đánh giá SVD/Hybrid ở Day 3.

#### Task 2 — Viết `scripts/run_ranking_eval.py`

- [ ] Load `train`, `test`, `movies`.
- [ ] Khởi tạo 3 models: Popularity, Content-Based, Item-CF.
- [ ] Với mỗi user có ít nhất một relevant item trong test:
  - [ ] Lấy top `max(K)` recommendation từ train history.
  - [ ] `exclude_seen=True`.
  - [ ] Tính Precision@K, Recall@K, NDCG@K cho K = 5, 10, 20.
- [ ] Macro-average trên các user hợp lệ.
- [ ] Tính coverage@10: tỷ lệ phim xuất hiện ít nhất một lần trong top-10.
- [ ] Ghi `reports/metrics/ranking.json`.
- [ ] In bảng tóm tắt ra console.
- [ ] Exit code khác 0 nếu thiếu file hoặc metric ngoài `[0, 1]`.
- [ ] Không dùng test để fit/tune.
- [ ] Script không import Streamlit.

**Schema gợi ý cho `reports/metrics/ranking.json`:**

```json
{
  "config": {
    "k_values": [5, 10, 20],
    "primary_k": 10,
    "relevance_threshold": 4.0,
    "seed": 42,
    "n_users_evaluated": 943,
    "n_users_skipped": 0
  },
  "models": {
    "popularity": {
      "precision@5": 0.0,
      "recall@5": 0.0,
      "ndcg@5": 0.0,
      "precision@10": 0.0,
      "recall@10": 0.0,
      "ndcg@10": 0.0,
      "precision@20": 0.0,
      "recall@20": 0.0,
      "ndcg@20": 0.0,
      "coverage@10": 0.0
    },
    "content_based": {},
    "item_cf": {}
  }
}
```

#### Task 3 — Viết `scripts/smoke_item_cf.py`

- [ ] Load `RecommenderService`.
- [ ] In top-5 Item-CF cho user `1`, `196`, `405`.
- [ ] In similar movies Item-CF cho:
  - `Toy Story (1)`
  - `Star Wars (50)`
  - `Pulp Fiction (56)`
- [ ] In method và reason của từng item.
- [ ] Kiểm tra không có phim đã xem trong top-10 (dùng train).
- [ ] Kiểm tra user `999999` fallback Popularity.
- [ ] Kiểm tra user không có rating trong train fallback Popularity.
- [ ] Kiểm tra phim không có tương tác fallback.
- [ ] Kiểm tra `movie_id` không tồn tại raise `ValueError`.
- [ ] Script không import Streamlit, chỉ dùng service.
- [ ] Exit code khác 0 nếu có case fail.

#### Task 4 — Chạy đánh giá và ghi nhận

- [ ] Chạy `python scripts/run_ranking_eval.py` sau khi Huy xong service.
- [ ] Kiểm tra `ranking.json` có đủ 3 model và 3 giá trị K.
- [ ] So sánh 3 phương pháp, ghi nhận phương pháp tốt nhất theo NDCG@10.
- [ ] Ghi các case bất thường:
  - [ ] Item-CF có precision thấp hơn Popularity.
  - [ ] Coverage thấp.
  - [ ] Nhiều user bị skip vì không có relevant item.
- [ ] Ghi kết quả thực tế vào `notes/day3_eval.md`.
- [ ] Ghi rõ ranking metrics chỉ dùng test một lần.
- [ ] Không tính RMSE/MAE cho Item-CF nếu model không hỗ trợ `predict_rating`.
- [ ] Không đánh giá SVD/Hybrid ở Day 3.

#### Task 5 — Review chéo

- [ ] Review model Item-CF của Huy: chỉ dùng train, không leakage.
- [ ] Review ranking metrics: công thức, duplicate, user không có relevant.
- [ ] Review app của Linh: kết quả hiển thị đúng method/reason.
- [ ] Chạy lại lệnh của Huy và Linh trên máy mình.

### 3.4 Lệnh kiểm tra của Phong

```bash
python scripts/run_ranking_eval.py
python scripts/smoke_item_cf.py
pytest tests/test_ranking_metrics.py -q
python -c "import json; d=json.load(open('reports/metrics/ranking.json')); print(d['config']); print(sorted(d['models']))"
```

### 3.5 Tiêu chí hoàn thành

- [ ] Evaluation protocol có đầy đủ ranking metrics.
- [ ] `run_ranking_eval.py` chạy được, tất định, ghi đúng JSON.
- [ ] `ranking.json` có đủ Popularity, Content-Based, Item-CF.
- [ ] Smoke script Item-CF chạy được, exit code đúng.
- [ ] Đã đánh giá 3 user và 3 phim.
- [ ] Đã kiểm tra user lạ, user không rating và phim không tương tác.
- [ ] Không có phim đã xem trong top-K.
- [ ] Có `notes/day3_eval.md`.
- [ ] Review xong model, metrics và app.

### 3.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Ranking eval quá chậm | Vector hóa, giữ top-50 láng giềng; nếu vẫn chậm, giảm K và ghi rõ |
| Item-CF tệ hơn Popularity | Ghi nhận trung thực; không tune trên test |
| Test ít relevant item | Báo `n_users_evaluated` và `n_users_skipped` |
| Metric không tất định | Tie-break `movie_id`; seed 42 |
| Script phụ thuộc app | Chỉ dùng service/model |
| JSON sai schema | Validate trong script và test |

### 3.7 Báo cáo cuối ngày

- Đã xong: ...
- Ranking metrics 3 phương pháp: ...
- Item-CF so với Popularity/Content-Based: ...
- Smoke/fallback: ...
- Blocker, đề xuất Day 4: ...

---

## 4. HƯỚNG DẪN CHO LINH

### 4.1 Mục tiêu cá nhân

Đưa Item-CF và ranking metrics lên Streamlit, cập nhật README/CI, đảm bảo app chỉ gọi service, có cache và xử lý lỗi.

### 4.2 Phụ thuộc

- Huy giao service có method `item_cf` trước **11:30**.
- Phong cung cấp `reports/metrics/ranking.json` trước **15:00**.
- Có thể làm UI trước bằng method key, dùng empty state nếu model chưa xong.

### 4.3 Checklist công việc chi tiết

#### Task 1 — Review UI hiện tại

- [ ] Đọc `app/pages/2_Recommendations.py`.
- [ ] Đọc `app/pages/3_Similar_Movies.py`.
- [ ] Đọc `app/pages/4_Compare_Methods.py`.
- [ ] Đọc `app/pages/5_Evaluation.py`.
- [ ] Xác nhận app chỉ import `src.service`, không import `src.models`.
- [ ] Xác nhận cache đang dùng đúng.

#### Task 2 — Cập nhật Recommendations page

- [ ] Selectbox phương pháp:
  - `Popularity` → `popularity`
  - `Content-Based` → `content_based`
  - `Item-CF` → `item_cf`
- [ ] Giữ slider K 5–20.
- [ ] Giữ checkbox “Loại bỏ phim đã xem”.
- [ ] Hiển thị method và reason trên card.
- [ ] Xử lý danh sách rỗng.
- [ ] Xử lý lỗi service.
- [ ] Không thay đổi hành vi mặc định nếu không cần.

#### Task 3 — Cập nhật Similar Movies page

- [ ] Thêm selectbox phương pháp:
  - `Content-Based` → `content_based`
  - `Item-CF` → `item_cf`
- [ ] Giữ tìm kiếm phim + selectbox.
- [ ] Gọi `service.similar_items(movie_id, k=k, method=method)`.
- [ ] Hiển thị lý do “Cùng thể loại: ...” hoặc “Cùng gu người dùng”.
- [ ] Xử lý phim không tồn tại / không có kết quả.
- [ ] Không thêm `list_movies` nếu không cần.

#### Task 4 — Cập nhật Compare/Home

- [ ] `app/pages/4_Compare_Methods.py`:
  - So sánh 3 phương pháp: Popularity, Content-Based, Item-CF.
  - Dùng tab hoặc 3 cột; đảm bảo không vỡ layout.
  - Ghi rõ điểm 3 phương pháp khác thang đo.
- [ ] `app/Home.py`:
  - Cập nhật mô tả model hiện có.
  - Ghi Item-CF và ranking metrics đã có.
  - Không cần thêm metric mới ngoài baseline.

#### Task 5 — Cập nhật Evaluation page

- [ ] Đọc `ranking.json` qua `service.get_ranking_metrics()`.
- [ ] Hiển thị config: K, relevance threshold, số user đánh giá.
- [ ] Hiển thị bảng:
  - Model
  - Precision@5
  - Precision@10
  - Recall@10
  - NDCG@10
  - Coverage@10
- [ ] Giữ phần baseline RMSE/MAE.
- [ ] Xử lý `ranking.json` chưa có:
  “Chưa có reports/metrics/ranking.json. Hãy chạy python scripts/run_ranking_eval.py.”
- [ ] Bỏ ghi chú “Ranking metrics sẽ có ở Day 3”.
- [ ] Ghi rõ ranking metrics dùng test và threshold 4.0.

#### Task 6 — README và CI

- [ ] Cập nhật kiến trúc: Item-CF đã có.
- [ ] Cập nhật roadmap Day 3.
- [ ] Thêm mục “Kết quả Day 3”:
  - Phương pháp.
  - Bảng ranking metrics 3 model.
  - Ví dụ top-5 Item-CF cho 1 user.
  - Ví dụ similar movies Item-CF cho 1 phim.
  - Hạn chế: Item-CF thưa, cold-start, popularity fallback.
- [ ] Cập nhật lệnh chạy:
  - `python scripts/run_ranking_eval.py`
  - `python scripts/smoke_item_cf.py`
- [ ] Không ghi đè RMSE/MAE của Popularity.
- [ ] Cập nhật CI:
  - `ruff check .`
  - `pytest -q`
  - `python scripts/run_ranking_eval.py`
  - `python scripts/smoke_content_based.py`
  - `python scripts/smoke_item_cf.py`
- [ ] Giữ bước app boundary grep.

#### Task 7 — Kiểm tra app và PR

- [ ] Chạy `streamlit run app/Home.py`.
- [ ] Chọn 3 user, top-10 Item-CF hiển thị.
- [ ] Chọn 3 phim, similar movies Item-CF hiển thị.
- [ ] So sánh 3 phương pháp hiển thị.
- [ ] Trang Evaluation hiển thị ranking metrics.
- [ ] User không tồn tại không crash.
- [ ] `exclude_seen=True` không trả phim đã xem.
- [ ] App không import trực tiếp model.
- [ ] Sau cache, phản hồi < 2 giây.
- [ ] Chạy AppTest cho 5 trang và tương tác Item-CF.
- [ ] Branch `feat/item-cf-ranking`.
- [ ] PR title: `feat(model): add item-based CF and ranking evaluation`.
- [ ] Mô tả What / Why / How tested / Screenshot.
- [ ] Gắn ví dụ top-5, ranking metrics, fallback cases.
- [ ] Nhờ Huy/Phong review.

### 4.4 Lệnh kiểm tra của Linh

```bash
pytest -q
ruff check .
if grep -R "from src.models" app/; then exit 1; fi
streamlit run app/Home.py
```

### 4.5 Tiêu chí hoàn thành

- [ ] Page 2 chọn được 3 phương pháp.
- [ ] Page 3 chọn được Content-Based / Item-CF.
- [ ] Page 4 so sánh 3 phương pháp.
- [ ] Page 5 hiển thị ranking metrics.
- [ ] App không import trực tiếp model.
- [ ] Cache hoạt động.
- [ ] README cập nhật.
- [ ] CI xanh.
- [ ] PR được review + merge.

### 4.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Service API chưa xong | Dùng method key, empty state; tích hợp sau |
| `ranking.json` chưa có | Empty state + hướng dẫn chạy script |
| Cache stale | Clear cache/restart Streamlit khi test |
| Trùng title | Dùng `movie_id` trong selectbox |
| Fallback gây nhầm method | Hiển thị method/reason rõ ràng |
| App import model | CI grep boundary |
| Layout 3 cột bị chật | Dùng tab hoặc cột có tỷ lệ hợp lý |
| Page config sai thứ tự | `set_page_config` trước UI commands |

### 4.7 Báo cáo cuối ngày

- Đã xong: ...
- App URL/trạng thái: ...
- Trang nào chạy/chưa chạy: ...
- Ví dụ top-5/similar movies/ranking: ...
- Blocker, đề xuất Day 4: ...

---

## 5. REVIEW CHÉO & TÍCH HỢP

| Người review | Nội dung review | Deadline |
|---|---|---|
| Huy → Phong | Evaluation protocol, ranking script, `ranking.json`, smoke Item-CF | 15:00 |
| Huy → Linh | App boundary, cache, error handling, trang Evaluation | 15:30 |
| Phong → Huy | Item-CF chỉ dùng train, ranking metrics đúng công thức | 15:00 |
| Linh → Huy | Service API, app hiển thị method/reason, Item-CF | 15:30 |
| Cả nhóm | Chạy lại lệnh của nhau trên máy mình | 16:00 |

**Quy tắc review:**
- Ưu tiên correctness, leakage, khả năng chạy, interface.
- Không bắt lỗi style nhỏ nếu không ảnh hưởng.
- Mỗi PR có ít nhất 1 approval.
- Không merge PR của mình khi chưa có người khác review.
- Ghi review vào PR hoặc `notes/day3_review.md` nếu repo chỉ có một tài khoản maintainer.

---

## 6. CHECKLIST CHUNG CUỐI DAY 3

### Model

- [ ] `ItemCFRecommender` đúng contract.
- [ ] Chỉ dùng train để fit và tạo profile.
- [ ] Similar items loại chính nó.
- [ ] Fallback Popularity cho cold-start/không tín hiệu.
- [ ] Không đọc test data khi fit.
- [ ] Kết quả deterministic.

### Ranking metrics

- [ ] Precision@K đúng công thức.
- [ ] Recall@K đúng công thức.
- [ ] NDCG@K đúng công thức.
- [ ] Relevance threshold 4.0.
- [ ] K = 5, 10, 20.
- [ ] Macro-average trên user hợp lệ.
- [ ] `ranking.json` có đủ 3 model.

### Service

- [ ] `item_cf` đã đăng ký.
- [ ] `recommend` và `similar_items` hoạt động.
- [ ] `get_ranking_metrics()` hoạt động.
- [ ] Method không hỗ trợ raise `ValueError` rõ ràng.
- [ ] App không import trực tiếp model.

### App

- [ ] Page 2 chọn 3 phương pháp.
- [ ] Page 3 chọn Content-Based / Item-CF.
- [ ] Page 4 so sánh 3 phương pháp.
- [ ] Page 5 hiển thị ranking metrics.
- [ ] Hiển thị method/reason.
- [ ] User không tồn tại không crash.
- [ ] `exclude_seen=True` hoạt động.

### Test & tài liệu

- [ ] `pytest -q` pass.
- [ ] `ruff check .` pass.
- [ ] CI xanh.
- [ ] `smoke_item_cf.py` chạy.
- [ ] `run_ranking_eval.py` chạy.
- [ ] README cập nhật.
- [ ] `docs/evaluation_protocol.md` cập nhật.
- [ ] Có `notes/day3_eval.md` và `notes/day3_report.md`.
- [ ] Không commit data/model/secret.
- [ ] PR có review.

---

## 7. QUY TẮC GIT

### Branch

- Dùng chung branch `feat/item-cf-ranking`.
- Không push trực tiếp lên `main`.
- Không dùng lại nhánh Day 1/Day 2.

### Commit message gợi ý

```text
feat(model): add item-based collaborative filtering
feat(eval): add ranking metrics and evaluation script
feat(service): integrate item_cf and ranking metrics
feat(app): add item_cf and ranking evaluation pages
test(model): add item_cf and ranking metric tests
docs(readme): document Day 3 results
```

### PR

- PR nhỏ, có mô tả What / Why / How tested / Screenshot.
- Ít nhất 1 reviewer.
- Squash merge.
- Không commit raw data, model artifact, `.env`, secret.
- `ranking.json` được commit vì nhỏ và tất định.

---

## 8. KHI BỊ BLOCK

1. Tự thử tối đa 15 phút.
2. Ghi rõ:
   - Lệnh gây lỗi.
   - Thông báo lỗi đầy đủ.
   - Đã thử gì.
3. Báo ngay trong nhóm chat, tag Huy nếu là blocker kỹ thuật.
4. Không tự ý đổi thuật toán/scope để che blocker.

**Thứ tự ưu tiên nếu thiếu thời gian:**

1. Item-CF model đúng + fallback.
2. Ranking metrics + `ranking.json`.
3. Service integration.
4. App page 2 + page 3 + page 5.
5. Unit test + smoke script.
6. README + đánh giá định tính.
7. PR/CI.

---

## 9. PHỤ LỤC — CÔNG THỨC & QUY ƯỚC

### Relevant item

```text
relevant(u) = { movie_id | (u, movie_id, rating) in test và rating >= 4.0 }
```

### Precision@K

```text
precision@K(u) = |relevant(u) ∩ topK(u)| / K
```

### Recall@K

```text
recall@K(u) = |relevant(u) ∩ topK(u)| / |relevant(u)|
```

### NDCG@K

```text
DCG@K(u)  = sum(1 / log2(rank + 1)) cho các item relevant trong topK
IDCG@K(u) = sum(1 / log2(rank + 1)) cho min(|relevant(u)|, K) vị trí đầu
NDCG@K(u) = DCG@K(u) / IDCG@K(u)
```

### Macro-average

```text
metric = mean(metric(u)) trên các user có |relevant(u)| > 0
```

### Coverage@K

```text
coverage@K = |union(topK(u))| / số phim trong catalog
```

### Quy ước

- Duplicate `movie_id` trong danh sách recommendation chỉ tính lần đầu.
- Nếu `relevant(u)` rỗng: bỏ user khỏi evaluation, tăng `n_users_skipped`.
- Nếu `K` lớn hơn số recommendation trả về: precision vẫn chia cho `K`.
- Tie-break score bằng `movie_id` tăng dần.
- Không dùng test để chọn hyperparameter.
- Không so sánh trực tiếp score giữa các phương pháp; chỉ so sánh ranking metrics.
