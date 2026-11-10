# TASK DAY 4 — 09/11/2026

> Trạng thái 10/11/2026: code Day 4 đã merge vào `main` tại `184ecdd`. README, `notes/day4_report.md`, CI và checklist đã được cập nhật. Mục mô tả PR/screenshot của Linh vẫn để mở vì PR đã merge với body trống và không có ảnh; nội dung What/Why/How tested, ví dụ và metrics tương ứng đã có trong README và `notes/day4_report.md`. CI mới cần xác nhận sau push.

## Hướng dẫn chi tiết cho 3 thành viên

**Dự án:** AI Personalized Recommendation System (MovieLens 100K)

**Mục tiêu Day 4:** có **SVD** và **Hybrid** hoàn chỉnh, mở rộng đánh giá lên **5 phương pháp**:
**user → top-K SVD/Hybrid → so sánh 5 phương pháp → RMSE/MAE cho SVD → Precision@K / Recall@K / NDCG@K / Coverage@K trên Streamlit**.

**Demo cuối ngày:**
- Chọn 3 user khác nhau, xem top-10 SVD và top-10 Hybrid.
- Chọn 3 phim khác nhau, xem phim tương tự theo SVD và Hybrid.
- So sánh 5 phương pháp trên cùng một user: Popularity, Content-Based, Item-CF, SVD, Hybrid.
- Trang Evaluation hiển thị RMSE/MAE của Popularity và SVD, cùng bảng ranking metrics của 5 phương pháp.
- Kiểm tra fallback với user lạ, user không có rating trong train, phim không có tương tác.
- Không có phim đã xem trong top-K khi `exclude_seen=True`.
- Kết quả tất định khi chạy lại; không dùng test để fit hoặc tune.

---

## 0. PHÂN CÔNG TỔNG QUAN

| Thành viên | Vai trò | Phụ trách chính | Deliverable | Branch |
|---|---|---|---|---|
| **Huy (Trưởng nhóm)** | ML core + tích hợp | SVD model, Hybrid model, service, unit test, review, merge | `src/models/svd.py`, `src/models/hybrid.py`, `src/service/recommender_service.py`, `tests/test_svd.py`, `tests/test_hybrid.py` | `feat/svd-hybrid` |
| **Phong** | Data & Evaluation | Rating evaluation SVD, mở rộng ranking evaluation 5 model, smoke SVD/Hybrid, đánh giá định tính | `scripts/run_svd_eval.py`, `scripts/run_ranking_eval.py`, `scripts/smoke_svd_hybrid.py`, `reports/metrics/svd.json`, `reports/metrics/ranking.json`, `notes/day4_eval.md` | `feat/svd-hybrid` |
| **Linh** | Product & Integration | App 5 phương pháp, trang Evaluation, README, CI, PR | `app/pages/2_Recommendations.py`, `app/pages/3_Similar_Movies.py`, `app/pages/4_Compare_Methods.py`, `app/pages/5_Evaluation.py`, `app/Home.py`, `app/components/service.py`, `README.md` | `feat/svd-hybrid` |

**Nguyên tắc phối hợp:**
- Tất cả làm trên **một branch chung** `feat/svd-hybrid` để tránh conflict.
- Huy chốt API SVD + Hybrid và service trước **11:30** để Phong và Linh tích hợp.
- Phong làm `run_svd_eval.py` và khung ranking 5 model trước, chạy lại khi SVD/Hybrid xong.
- Linh làm UI bằng method key `svd`, `hybrid`; dùng empty state nếu model chưa xong.
- Không ai sửa file của người khác khi chưa trao đổi.
- Review chéo qua PR trước khi merge.
- Không thêm comment/docstring mới vào code theo `AGENTS.md`.
- Không dùng test để chọn hyperparameter, trọng số Hybrid hay ngưỡng nào.

### Quyết định kỹ thuật mặc định

- SVD dùng `surprise.SVD`; fit **chỉ trên train**; không dùng Surprise ở phần khác ngoài model SVD và evaluator.
- Hyperparameter SVD chốt trước khi đánh giá:
  - `n_factors=100`
  - `n_epochs=20`
  - `lr_all=0.005`
  - `reg_all=0.02`
  - `random_state=42`
- Không tune SVD trên test. Nếu RMSE không tốt hơn Popularity, ghi nhận trung thực.
- Candidate khi SVD recommend: các phim có **ít nhất một rating trong train**; loại phim đã xem nếu `exclude_seen=True`.
- Điểm SVD: dự đoán rating, clip `[1, 5]`; sort giảm dần, tie-break `movie_id` tăng dần.
- Similar Items của SVD: cosine trên **item latent factors**; clip âm về `0`, bỏ chính nó; phim không có factor fallback Popularity.
- Hybrid kết hợp **SVD + Item-CF + Content-Based** bằng min-max normalization từng danh sách rồi weighted sum.
- Trọng số Hybrid chốt trước khi đánh giá:
  - Recommend: `svd=0.5`, `item_cf=0.3`, `content_based=0.2`.
  - Similar: `item_cf=0.4`, `svd=0.3`, `content_based=0.3`.
- Hybrid chỉ blend các item do chính component sinh ra (`method` trùng tên component); item fallback Popularity của component bị loại trước khi blend, sau đó mới fill Popularity ở cấp Hybrid nếu thiếu.
- Method key: `svd`, `hybrid`.
- Fallback: Popularity.
- Relevance threshold cho ranking metrics giữ nguyên: `rating >= 4.0`.
- K đánh giá giữ nguyên: `5`, `10`, `20`; K chính: `10`.
- Macro-average trên các user có ít nhất một relevant item trong test; giữ nguyên tập user và coverage denominator của Day 3.
- Không đổi contract `src/models/base.py`.
- Không thêm dependency mới; `scikit-surprise==1.1.4` đã có trong `requirements.txt`.
- Không đọc test data khi fit/tạo profile. Test chỉ dùng một lần cho đánh giá cuối.
- Đổi thông báo method không hỗ trợ từ cụm “Day 4” thành **`Method {method} không được hỗ trợ`**.
- Giữ nguyên `reports/metrics/baseline.json` và số liệu Day 1; thêm `reports/metrics/svd.json`; cập nhật `reports/metrics/ranking.json` thành 5 model.
- Commit `reports/metrics/svd.json` và `reports/metrics/ranking.json` vì nhỏ và tất định; không commit model artifact.

### Trạng thái đầu vào

- Day 3 đã merge vào `main`, PR #14 tại commit `1fa84bb`.
- 67 test pass; `ruff check .` pass; smoke Item-CF và ranking eval pass.
- Service đã hỗ trợ `popularity`, `content_based`, `item_cf`.
- App có 5 trang; Compare đang so sánh 3 phương pháp; Evaluation có baseline RMSE/MAE và ranking 3 model.
- `scikit-surprise==1.1.4` đã cài và `scripts/smoke_surprise.py` chạy được (RMSE tham khảo 0.9540, không phải kết quả chính thức).
- `ranking.json` hiện có Popularity tốt nhất NDCG@10; Item-CF coverage cao nhất nhưng precision thấp.
- 32 phim không có tương tác trong train; 487 user không có relevant item trong test.
- Data `train.parquet`, `test.parquet`, `movies.parquet`, `users.parquet` sẵn sàng.

### Việc cần dọn trước khi bắt đầu

- [x] Sync local `main` lên `origin/main` mới nhất.
- [x] Xác nhận `git status` sạch.
- [x] Tạo branch `feat/svd-hybrid`.
- [x] Đọc lại `notes/task_day3_7_11.md`, `notes/day3_report.md`, `notes/day3_eval.md`, `notes/day3_review.md`.
- [x] Đọc `docs/evaluation_protocol.md`, `src/models/base.py`, `src/models/item_cf.py`, `src/models/content_based.py`, `src/service/recommender_service.py`.
- [x] Chạy lại baseline kiểm tra: `pytest -q`, `ruff check .`, `python scripts/run_ranking_eval.py`.

**Lệnh gợi ý:**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch -c feat/svd-hybrid
git status
```

---

## 1. MỐC THỜI GIAN & BÀN GIAO

| Giờ | Việc chung | Huy | Phong | Linh |
|---|---|---|---|---|
| 09:00–09:30 | Sync, chốt protocol SVD/Hybrid, tạo branch | Chủ trì | Tham gia | Tham gia |
| 09:30–10:30 | SVD core + rating eval skeleton | Viết SVD model | Khung `run_svd_eval.py` | Review UI hiện tại |
| **10:30** | **SVD recommend/similar chạy được** | Báo tiến độ | Chạy thử rating eval | Bắt đầu page 2/3 |
| 10:30–11:30 | Hybrid + service + test | Hybrid, service, unit test | Mở rộng ranking eval | Page 2, 3, method selector |
| **11:30** | **Service có `svd`, `hybrid`** | Báo tiến độ | Chạy ranking 5 model | Bắt đầu page 4/5 |
| 12:00 | Sync nhanh 5 phút | Báo tiến độ | Báo tiến độ | Báo tiến độ |
| 13:30–15:00 | App + đánh giá | Review/integration | Chạy SVD eval, smoke | Page 4/5, README |
| 15:00–15:45 | Smoke test, demo data | Chạy service | Tổng hợp số liệu, JSON | Chạy AppTest |
| 15:45–16:30 | Review, CI, merge | Review/merge | Review | PR/CI |
| 16:30–17:00 | Chốt Day 4 | Viết báo cáo | Cập nhật eval | Cập nhật README |

---

## 2. HƯỚNG DẪN CHO HUY (TRƯỞNG NHÓM)

### 2.1 Mục tiêu cá nhân

Có `SVDRecommender` và `HybridRecommender` đúng contract, service tích hợp đủ 5 phương pháp, unit test đầy đủ, review và merge toàn bộ Day 4.

### 2.2 Phụ thuộc

- Day 3 đã merged; service, data và ranking metrics sẵn sàng.
- Surprise đã cài trong môi trường local và CI.
- SVD cần xong trước **10:30** để Phong chạy rating eval.
- Service cần xong trước **11:30** để Linh tích hợp app.
- Hybrid phụ thuộc SVD, Item-CF và Content-Based đã có.

### 2.3 Checklist công việc chi tiết

#### Task 1 — Viết `src/models/svd.py`

**Fit và dữ liệu:**

- [x] Chỉ nhận `train_df` và `movies_df`; không nhận hoặc đọc `test_df`.
- [x] Sort `movies_df` theo `movie_id`; lưu mapping:
  - `movie_ids`
  - `movie_id_to_index`
  - `index_to_movie_id`
- [x] Dùng `src.data.surprise_dataset.build_surprise_trainset(train_df)` để tạo trainset.
- [x] Fit `surprise.SVD` với hyperparameter mặc định đã chốt.
- [x] Lưu tập user có trong train để nhận diện cold-start.
- [x] Căn item factors `qi` và item bias `bi` theo thứ tự `movie_ids`; phim không có trong trainset có vector zero và `has_factors=False`.
- [x] Tính cosine similarity giữa các item đã có factor:
  - Normalize từng hàng factor vector.
  - `similarity = clip(normalized @ normalized.T, 0, 1)`.
  - Đặt diagonal bằng `0`.
- [x] Phim không có tương tác train: không crash, không có similarity dương; fallback Popularity khi cần.

**API dự kiến:**

```python
class SVDRecommender:
    name = "svd"

    def __init__(
        self,
        train_df,
        movies_df,
        fallback=None,
        n_factors: int = 100,
        n_epochs: int = 20,
        lr_all: float = 0.005,
        reg_all: float = 0.02,
        random_state: int = 42,
    ):
        ...

    def predict_rating(self, user_id: int, movie_id: int) -> float:
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

**`predict_rating`:**

- [x] Dùng dự đoán của Surprise cho cặp user/movie; trả `float` đã clip `[1, 5]`.
- [x] User hoặc movie không có trong trainset: trả global mean (hoặc giá trị Surprise trả về), không crash.
- [x] Dùng hàm này trong `scripts/run_svd_eval.py` để chỉ có một đường tính rating.

**`recommend`:**

- [x] `k <= 0`: trả danh sách rỗng.
- [x] User không có trong train: fallback Popularity, method `"popularity"`, reason `"Fallback phổ biến (cold-start)"`.
- [x] Với user hợp lệ, tính điểm cho toàn bộ phim có factor trong train:
  - Vector hóa theo công thức `mu + b_u + b_i + p_u · q_i`.
  - Clip `[1, 5]`.
  - Không lặp từng cặp bằng `algo.predict` để tránh chậm; chỉ dùng vector hóa.
- [x] `exclude_seen=True`: loại phim user đã rating trong **train**.
- [x] Sort score giảm dần, tie-break `movie_id` tăng dần; trả tối đa `k`.
- [x] Item native:
  - `method="svd"`.
  - reason `"Dự đoán theo sở thích cá nhân (SVD)"`.
- [x] Không đủ item / không có tín hiệu:
  - Nối Popularity sau kết quả SVD, chống trùng.
  - method `"popularity"`.
  - reason `"Fallback phổ biến (thiếu tín hiệu)"`.

**`similar_items`:**

- [x] Movie ID không tồn tại: raise `ValueError(f"Movie {movie_id} không tồn tại")`.
- [x] `k <= 0`: trả danh sách rỗng.
- [x] Lấy similarity vector của phim gốc; loại chính nó; chỉ giữ `score > 0`.
- [x] Sort giảm dần, tie-break `movie_id`; trả tối đa `k`.
- [x] Item native:
  - `method="svd"`.
  - reason `"Cùng gu người dùng (SVD)"`.
- [x] Phim không có factor / không đủ kết quả: fallback Popularity, reason `"Fallback phổ biến (thiếu tín hiệu)"`.

**Kiểm chứng bắt buộc:**

- [x] So sánh điểm vector hóa với `algo.predict(uid, iid).est` trên một số cặp known user/item; sai lệch tối đa `1e-6` sau clip.
- [x] Chạy 2 lần cùng dữ liệu cho kết quả giống nhau (random_state + tie-break).
- [x] Không dùng test ở bất kỳ bước fit/profile/similarity.

#### Task 2 — Viết `src/models/hybrid.py`

**API dự kiến:**

```python
class HybridRecommender:
    name = "hybrid"

    def __init__(
        self,
        models: dict,
        train_df,
        fallback=None,
        recommend_weights: dict | None = None,
        similar_weights: dict | None = None,
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

**Khởi tạo và trọng số:**

- [x] `models` phải có đủ key `svd`, `item_cf`, `content_based`; thiếu key raise `ValueError`.
- [x] Trọng số mặc định:
  - `recommend_weights = {"svd": 0.5, "item_cf": 0.3, "content_based": 0.2}`
  - `similar_weights = {"item_cf": 0.4, "svd": 0.3, "content_based": 0.3}`
- [x] Kiểm tra trọng số: không âm, tổng > 0, không có key lạ; normalize về tổng 1.
- [x] Lưu `known_users = set(train_df.user_id)` để nhận diện cold-start; không dùng test.

**Blend:**

- [x] Candidate pool mỗi component: `pool = max(50, k * 3)`.
- [x] Gọi từng component với `k=pool`, `exclude_seen` tương ứng.
- [x] Chỉ giữ item có `item.method == tên component`; loại item fallback Popularity của component.
- [x] Min-max normalize score từng component:
  - `norm = (score - min) / (max - min)`.
  - Nếu `max == min` (một item hoặc toàn bộ bằng nhau), gán `norm = 1.0`.
- [x] Blended score = tổng `weight * norm`; item không xuất hiện ở component nào nhận phần đóng góp `0`.
- [x] Loại trùng `movie_id`; sort blended score giảm dần, tie-break `movie_id` tăng dần.
- [x] Trả tối đa `k`; score cuối trong `[0, 1]`.

**`recommend`:**

- [x] `k <= 0`: trả danh sách rỗng.
- [x] User không có trong train / không có rating trong train:
  - Fallback Popularity.
  - method `"popularity"`.
  - reason `"Fallback phổ biến (cold-start)"`.
- [x] Item native:
  - `method="hybrid"`.
  - reason `"Kết hợp SVD + Item-CF + Content-Based"`.
- [x] Không đủ item sau blend:
  - Nối Popularity, chống trùng.
  - method `"popularity"`.
  - reason `"Fallback phổ biến (thiếu tín hiệu)"`.

**`similar_items`:**

- [x] Movie ID không tồn tại: raise `ValueError(f"Movie {movie_id} không tồn tại")`.
- [x] `k <= 0`: trả danh sách rỗng.
- [x] Blend theo `similar_weights` từ `similar_items` của 3 component; cùng quy tắc pool, lọc native, min-max, tie-break.
- [x] Item native:
  - `method="hybrid"`.
  - reason `"Kết hợp độ tương đồng SVD + Item-CF + Content-Based"`.
- [x] Loại chính nó; không đủ kết quả thì fallback Popularity, reason `"Fallback phổ biến (thiếu tín hiệu)"`.

**Ghi chú thiết kế bắt buộc:**

- [x] Không gọi đệ quy Hybrid từ chính nó.
- [x] Không trộn trực tiếp score thô giữa các component; chỉ dùng score đã normalize.
- [x] Không dùng kết quả test để chọn trọng số hoặc pool.
- [x] Score Hybrid là điểm blend `[0, 1]`, không so sánh trực tiếp với predicted rating của SVD/Item-CF.

#### Task 3 — Tích hợp service

Sửa `src/service/recommender_service.py`:

- [x] Khởi tạo theo thứ tự: Popularity → Content-Based → Item-CF → SVD → Hybrid.
- [x] SVD nhận fallback Popularity.
- [x] Hybrid nhận `models={"svd": ..., "item_cf": ..., "content_based": ...}`, `train_df=self.train_df`, fallback Popularity.
- [x] Bọc import SVD/Hybrid bằng `try/except ImportError` giống Content-Based để app vẫn khởi động nếu thiếu Surprise.
- [x] Nếu SVD/Hybrid chưa đăng ký:
  - `recommend`/`similar_items` với method tương ứng raise `RuntimeError` rõ ràng, ví dụ `"SVDRecommender chưa sẵn sàng: thiếu model hoặc dữ liệu train/movies"`.
- [x] Thêm `self.models["svd"]` và `self.models["hybrid"]`.
- [x] `recommend(..., method="svd"/"hybrid")` hoạt động.
- [x] `similar_items(..., method="svd"/"hybrid")` hoạt động.
- [x] Method không hỗ trợ:
  `ValueError(f"Method {method} không được hỗ trợ")`.
- [x] Thêm `get_svd_metrics() -> dict`:
  - Đọc `reports/metrics/svd.json`.
  - Trả `{}` nếu chưa có.
- [x] Giữ `get_baseline_metrics()` và `get_ranking_metrics()`.
- [x] Không đổi response contract `Recommendation`.
- [x] Service vẫn không import Streamlit.
- [x] Không dùng `self.test_df` trong init/fit của bất kỳ model nào.

#### Task 4 — Unit test

Tạo `tests/test_svd.py` với DataFrame giả (không phụ thuộc data thật):

- [x] `recommend` trả đủ k cho user hợp lệ; method native là `"svd"`; score trong `[1, 5]`.
- [x] `recommend` loại phim đã xem khi `exclude_seen=True`.
- [x] `recommend` với `exclude_seen=False` vẫn có thể trả phim đã xem.
- [x] User lạ fallback Popularity, method `"popularity"`, reason cold-start.
- [x] User không có rating trong train fallback Popularity.
- [x] Phim không có tương tác fallback khi `similar_items`.
- [x] `similar_items` trả item tương tự, loại chính nó, tôn trọng `k`, score trong `(0, 1]` với item native.
- [x] Movie không tồn tại raise `ValueError`.
- [x] `k <= 0` trả danh sách rỗng cho cả `recommend` và `similar_items`.
- [x] Kết quả deterministic khi score bằng nhau (tie-break `movie_id`).
- [x] `predict_rating` trả `float` trong `[1, 5]`, kể cả user/movie lạ.
- [x] Điểm vector hóa khớp `algo.predict` với dung sai `1e-6` trên vài cặp known.
- [x] Test dùng hyperparameter nhỏ (`n_factors=2`, `n_epochs=2`) để nhanh.

Tạo `tests/test_hybrid.py` với fake component models:

- [x] Trọng số mặc định đúng và được normalize.
- [x] Trọng số âm / tổng bằng 0 / key lạ / thiếu key raise `ValueError`.
- [x] Blend đúng một ví dụ tính tay sau min-max.
- [x] Chỉ blend item native; item fallback Popularity của component bị loại.
- [x] Item chỉ có ở một component vẫn nhận đúng phần đóng góp.
- [x] `max == min` trong một component được normalize thành `1.0`.
- [x] `recommend` loại phim đã xem khi `exclude_seen=True`.
- [x] User lạ / cold-start fallback Popularity, method `"popularity"`, reason cold-start.
- [x] Thiếu item sau blend được fill Popularity, method `"popularity"`, reason thiếu tín hiệu.
- [x] `similar_items` loại chính nó; movie không tồn tại raise `ValueError`; `k <= 0` trả rỗng.
- [x] Kết quả deterministic, tie-break `movie_id`.
- [x] Không phụ thuộc data thật hoặc model thật.

Cập nhật test service:

- [x] `svd` và `hybrid` đã đăng ký (surprise có trong môi trường test).
- [x] `recommend` và `similar_items` với `svd`, `hybrid` hoạt động.
- [x] `get_svd_metrics()` trả `{}` khi thiếu file và đọc đúng khi có file.
- [x] Method invalid raise `ValueError` với thông báo `"không được hỗ trợ"`, không còn chuỗi “Day 4”.
- [x] Trường hợp thiếu dependency SVD (monkeypatch import) raise `RuntimeError` rõ ràng.

Cập nhật `tests/test_ranking_eval_script.py`:

- [x] `METHODS` có 5 phương pháp theo đúng thứ tự.
- [x] CLI mock trả đủ 5 model và schema 10 metric/model.
- [x] Hybrid nhận `train_df` chỉ từ train; không thấy test trong factory.
- [x] Test thất bại không ghi đè `ranking.json`.

#### Task 5 — Review & tích hợp

- [x] Review `run_svd_eval.py` và protocol của Phong: SVD chỉ fit train, test dùng một lần, không tune.
- [x] Review ranking eval: đủ 5 model, cùng tập user, macro-average đúng, coverage giữ nguyên.
- [x] Review app của Linh: không import trực tiếp model, cache đúng, hiển thị method/reason, 5 phương pháp không vỡ layout.
- [x] Chạy:
  ```bash
  pytest -q
  ruff check .
  python scripts/run_svd_eval.py
  python scripts/run_ranking_eval.py
  python scripts/smoke_svd_hybrid.py
  python scripts/smoke_item_cf.py
  ```
- [x] Kiểm tra `git status`: không có data/model lớn, không có secret.
- [x] Review PR, merge khi CI xanh.
- [x] Viết `notes/day4_report.md`.

### 2.4 Lệnh kiểm tra của Huy

```bash
pytest tests/test_svd.py tests/test_hybrid.py -q
pytest -q
ruff check .
python -c "from src.service.recommender_service import RecommenderService; s=RecommenderService(); print(s.recommend(196, method='svd', k=5)); print(s.recommend(196, method='hybrid', k=5))"
python -c "from src.service.recommender_service import RecommenderService; s=RecommenderService(); print(s.similar_items(1, method='svd', k=5)); print(s.similar_items(1, method='hybrid', k=5))"
python scripts/run_svd_eval.py
python scripts/run_ranking_eval.py
python scripts/smoke_svd_hybrid.py
```

### 2.5 Tiêu chí hoàn thành

- [x] `SVDRecommender` đúng contract, chỉ dùng train để fit.
- [x] SVD recommend trả top-K predicted rating, clip `[1, 5]`, loại seen đúng.
- [x] SVD similar_items dựa trên latent factors, loại chính nó, fallback đúng.
- [x] `HybridRecommender` blend đúng 3 component, score `[0, 1]`, reason rõ.
- [x] User lạ / user không có rating / phim không tương tác fallback Popularity, không crash.
- [x] Service hỗ trợ đủ 5 method: `popularity`, `content_based`, `item_cf`, `svd`, `hybrid`.
- [x] `get_svd_metrics()` hoạt động.
- [x] Thông báo method invalid không còn “Day 4”.
- [x] Unit test pass, không phụ thuộc data thật.
- [x] Review xong PR của Phong và Linh.
- [x] PR được merge, CI xanh.
- [x] Có báo cáo Day 4.

### 2.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Surprise SVD không cài được trên Windows | Đã cài được; nếu lỗi build, dùng `.venv` hiện có, báo blocker, không đổi thuật toán |
| SVD chậm khi predict từng cặp | Vector hóa `mu + b_u + b_i + p_u·q_i`; chỉ dùng `predict_rating` cho 20k test |
| SVD RMSE không tốt hơn Popularity | Ghi nhận trung thực; không tune trên test |
| SVD thiếu factor cho phim zero-interaction | `has_factors=False`; fallback Popularity |
| Similarity latent factor âm | Clip âm về 0; chỉ giữ `score > 0` |
| Hybrid cộng score khác thang đo | Min-max từng component; chỉ blend item native |
| Hybrid cold-start bị gắn nhãn sai | Kiểm tra `known_users` từ train trước khi gọi component |
| Hybrid thiếu item do component fallback | Fill Popularity ở cấp Hybrid với method/reason đúng |
| Ranking eval lâu hơn Day 3 | Vector hóa SVD, pool Hybrid hợp lý; mục tiêu < 5 phút |
| Test phụ thuộc data thật | Dùng DataFrame giả và hyperparameter nhỏ |
| App import model trực tiếp | Giữ boundary; CI grep kiểm tra |
| Message/test còn “Day 4” | Cập nhật service, test, README, protocol trong cùng PR |

### 2.7 Báo cáo cuối ngày

Gửi nhóm 5 dòng:
- Đã xong: ...
- Model/method: ...
- RMSE/MAE SVD và ranking 5 model: ...
- Fallback/test: ...
- Blocker và đề xuất Day 5: ...

---

## 3. HƯỚNG DẪN CHO PHONG

### 3.1 Mục tiêu cá nhân

Đánh giá rating cho SVD, mở rộng ranking evaluation lên 5 phương pháp, smoke SVD/Hybrid và ghi nhận kết quả thực tế, đúng protocol, không leakage.

### 3.2 Phụ thuộc

- Data đã có.
- SVD model của Huy trước **10:30** để chạy rating eval.
- Service có `svd`, `hybrid` trước **11:30** để chạy ranking eval và smoke.
- App của Linh trước **15:00** để đối chiếu số liệu hiển thị.

### 3.3 Checklist công việc chi tiết

#### Task 1 — Cập nhật `docs/evaluation_protocol.md`

- [x] Ghi rõ Day 4 đánh giá 5 phương pháp: Popularity, Content-Based, Item-CF, SVD, Hybrid.
- [x] Ghi rõ SVD có rating metrics RMSE/MAE; các model còn lại không claim rating metrics nếu không có `predict_rating`.
- [x] Ghi hyperparameter SVD đã chốt trước đánh giá:
  `n_factors=100`, `n_epochs=20`, `lr_all=0.005`, `reg_all=0.02`, `random_state=42`.
- [x] Ghi quy tắc Hybrid:
  - Min-max normalize score từng component.
  - Trọng số recommend `svd=0.5`, `item_cf=0.3`, `content_based=0.2`.
  - Trọng số similar `item_cf=0.4`, `svd=0.3`, `content_based=0.3`.
  - Chỉ blend item native; fallback Popularity sau blend.
- [x] Ghi rõ score Hybrid `[0, 1]` không so sánh trực tiếp với rating score.
- [x] Giữ nguyên relevance threshold `4.0`, K `5/10/20`, K chính `10`, macro-average, coverage denominator.
- [x] Ghi rõ test chỉ dùng một lần để đánh giá; không chọn model/hyperparameter/trọng số từ test.
- [x] Bỏ câu “chưa đánh giá SVD/Hybrid ở Day 3”; thay bằng phạm vi Day 4.
- [x] Ghi rõ chưa tune SVD/Hybrid; kết quả xấu hơn baseline vẫn phải báo cáo.

#### Task 2 — Viết `scripts/run_svd_eval.py`

- [x] Load `train`, `test`, `movies`.
- [x] Validate:
  - Đủ file, không rỗng.
  - Train/test không overlap theo cặp `(user_id, movie_id)`.
  - Movie trong train/test thuộc catalog.
- [x] Khởi tạo `SVDRecommender(train, movies)` với hyperparameter mặc định.
- [x] Với mỗi dòng test: `y_pred = model.predict_rating(user_id, movie_id)`.
- [x] Kiểm tra prediction hữu hạn và trong `[1, 5]`; nếu sai, exit khác 0.
- [x] Tính RMSE/MAE bằng `src.evaluation.rating_metrics`.
- [x] Ghi `reports/metrics/svd.json` theo schema:
  ```json
  {
    "model": "svd",
    "rmse": 0.0,
    "mae": 0.0,
    "n_test": 20000,
    "train_size": 80000,
    "seed": 42,
    "hyperparameters": {
      "n_factors": 100,
      "n_epochs": 20,
      "lr_all": 0.005,
      "reg_all": 0.02
    }
  }
  ```
  Số `rmse`/`mae` phải là kết quả thật, không để placeholder.
- [x] Ghi qua file tạm rồi replace; lỗi không ghi đè kết quả cũ.
- [x] In JSON tóm tắt ra console.
- [x] Sanity check RMSE trong `[0.5, 1.5]`; ngoài khoảng thì cảnh báo rõ, không che giấu.
- [x] Không đọc test khi fit; chỉ dùng test để tính metric một lần.
- [x] Script không import Streamlit, không import app.

**Lệnh chạy:**

```bash
python scripts/run_svd_eval.py
python -c "import json; print(json.load(open('reports/metrics/svd.json')))"
```

#### Task 3 — Mở rộng `scripts/run_ranking_eval.py`

- [x] `METHODS = ("popularity", "content_based", "item_cf", "svd", "hybrid")`.
- [x] Import thêm `SVDRecommender`, `HybridRecommender`.
- [x] Khởi tạo:
  - Popularity trước.
  - Content-Based, Item-CF, SVD nhận fallback Popularity.
  - Hybrid nhận `models={"svd": ..., "item_cf": ..., "content_based": ...}`, `train_df=train`, fallback Popularity.
- [x] Giữ nguyên:
  - Relevance threshold `4.0`.
  - K `5/10/20`.
  - Macro-average cùng tập user.
  - Coverage@10 trên toàn catalog.
  - Validation recommendation thuộc catalog, không trùng, không chứa phim đã xem.
  - Ghi JSON qua file tạm, lỗi không ghi đè.
- [x] Schema `ranking.json` giữ nguyên; `models` có đủ 5 key.
- [x] Không truyền test vào constructor/fit của bất kỳ model nào.
- [x] Cập nhật thông báo lỗi dependency từ “Day 3” thành “Day 4”.
- [x] Mục tiêu thời gian chạy < 5 phút; nếu chậm, ghi thời gian thực tế và tối ưu pool/vector hóa, không giảm K tùy tiện.
- [x] Cập nhật `tests/test_ranking_eval_script.py` theo 5 model.
- [x] Kết quả cũ chỉ được thay bằng kết quả chạy thật; không sửa tay số liệu.

**Lệnh chạy:**

```bash
python scripts/run_ranking_eval.py
python -c "import json; d=json.load(open('reports/metrics/ranking.json')); print(d['config']); print(sorted(d['models'])); print(all(len(v)==10 for v in d['models'].values()))"
```

#### Task 4 — Viết `scripts/smoke_svd_hybrid.py`

- [x] Load `RecommenderService`.
- [x] Kiểm tra `svd`, `hybrid` đã đăng ký.
- [x] In top-5 SVD và top-5 Hybrid cho user `1`, `196`, `405`.
- [x] In similar movies SVD và Hybrid cho:
  - `Toy Story (1)`
  - `Star Wars (50)`
  - `Pulp Fiction (56)`
- [x] Mỗi kết quả kiểm tra:
  - Đủ `k`, không trùng `movie_id`.
  - `method` thuộc `{"svd", "popularity"}` hoặc `{"hybrid", "popularity"}`.
  - Có reason; fallback phải ghi “Fallback”.
  - Score hữu hạn.
  - SVD recommend score trong `[1, 5]`; SVD similar score trong `(0, 1]`.
  - Hybrid score trong `[0, 1]`.
  - Có ít nhất một item native, trừ trường hợp cold-start có chủ đích.
- [x] Kiểm tra không có phim đã xem trong top-10 với `exclude_seen=True` (dùng train).
- [x] Kiểm tra user `999999` fallback Popularity cho cả SVD và Hybrid.
- [x] Kiểm tra user metadata-only (tạm bỏ rating của một user trong bản copy train) fallback Popularity.
- [x] Kiểm tra phim zero-interaction (tạm bỏ tương tác của một phim trong bản copy train) fallback Popularity cho SVD.
- [x] Kiểm tra `movie_id` không tồn tại raise `ValueError` cho cả SVD và Hybrid.
- [x] Không sửa dữ liệu gốc; dùng `TemporaryDirectory` như smoke Day 3.
- [x] Script không import Streamlit, chỉ dùng service.
- [x] Exit code khác 0 nếu có case fail.
- [x] In đủ dữ liệu để Linh/Huy lấy ví dụ cho README và báo cáo.

#### Task 5 — Chạy đánh giá và ghi nhận

- [x] Chạy `python scripts/run_svd_eval.py` sau khi SVD xong.
- [x] Chạy `python scripts/run_ranking_eval.py` sau khi service có đủ 5 model.
- [x] Kiểm tra `ranking.json` có đủ 5 model và 10 metric/model.
- [x] Kiểm tra `svd.json` có đủ trường và giá trị thật.
- [x] So sánh:
  - SVD RMSE/MAE với Popularity baseline.
  - 5 model theo Precision@10, Recall@10, NDCG@10, Coverage@10.
  - Ghi rõ model tốt nhất theo NDCG@10 và theo Coverage@10.
- [x] Ghi các case bất thường:
  - SVD không cải thiện RMSE.
  - Hybrid tệ hơn từng component hoặc tệ hơn Popularity.
  - Coverage thấp/cao bất thường.
  - Nhiều user bị skip.
- [x] Ghi thời gian chạy ranking eval thực tế.
- [x] Ghi kết quả vào `notes/day4_eval.md`, gồm:
  - Protocol tóm tắt.
  - Bảng rating metrics (Popularity, SVD).
  - Bảng ranking metrics 5 model.
  - Nhận xét SVD vs baseline, Hybrid vs component.
  - Fallback/smoke coverage.
  - Giới hạn: không tune trên test, chưa có implicit feedback, score scale khác nhau.
- [x] Không sửa tay số liệu JSON.
- [x] Không so sánh trực tiếp raw score giữa các model.

#### Task 6 — Review chéo

- [x] Review SVD model: chỉ train, vector hóa khớp Surprise, fallback đúng.
- [x] Review Hybrid: normalization, trọng số, lọc native, cold-start, tie-break.
- [x] Review app của Linh: kết quả hiển thị đúng method/reason, đủ 5 phương pháp, không import model.
- [x] Chạy lại lệnh của Huy và Linh trên máy mình.
- [x] Ghi review vào PR hoặc `notes/day4_review.md` nếu cần.

### 3.4 Lệnh kiểm tra của Phong

```bash
python scripts/run_svd_eval.py
python scripts/run_ranking_eval.py
python scripts/smoke_svd_hybrid.py
pytest tests/test_svd.py tests/test_hybrid.py tests/test_ranking_eval_script.py -q
python -c "import json; d=json.load(open('reports/metrics/ranking.json')); print(d['config']); print(sorted(d['models']))"
```

### 3.5 Tiêu chí hoàn thành

- [x] Protocol cập nhật đầy đủ SVD/Hybrid và quy tắc không tune trên test.
- [x] `run_svd_eval.py` chạy được, tất định, ghi đúng `svd.json`.
- [x] `ranking.json` có đủ 5 model và schema cũ.
- [x] `smoke_svd_hybrid.py` chạy được, exit code đúng.
- [x] Đã đánh giá 3 user và 3 phim cho SVD/Hybrid.
- [x] Đã kiểm tra user lạ, user không rating, phim không tương tác.
- [x] Không có phim đã xem trong top-K.
- [x] Có `notes/day4_eval.md` với số liệu thật.
- [x] Review xong model, metrics và app.

### 3.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| SVD eval chậm | `predict_rating` dùng Surprise predict cho 20k dòng; không tối ưu quá mức |
| SVD RMSE tệ hơn baseline | Ghi nhận trung thực; không tune trên test |
| Ranking eval chậm vì 5 model | Vector hóa SVD; Hybrid pool `max(50, k*3)`; đo và ghi thời gian |
| Hybrid score không trong `[0, 1]` | Kiểm tra normalization và clip trước khi ghi JSON |
| JSON sai schema | Validate trước khi replace file |
| Kết quả không tất định | SVD `random_state=42`; tie-break `movie_id` |
| Test data bị dùng khi fit | Constructor chỉ nhận train/movies; review code |
| Script phụ thuộc app | Chỉ dùng service/model |

### 3.7 Báo cáo cuối ngày

- Đã xong: ...
- RMSE/MAE SVD so với Popularity: ...
- Ranking 5 phương pháp: ...
- Smoke/fallback: ...
- Blocker, đề xuất Day 5: ...

---

## 4. HƯỚNG DẪN CHO LINH

### 4.1 Mục tiêu cá nhân

Đưa SVD và Hybrid lên Streamlit, mở rộng Compare/Evaluation lên 5 phương pháp, cập nhật README/CI, giữ app chỉ gọi service, có cache và xử lý lỗi.

### 4.2 Phụ thuộc

- Huy giao service có `svd`, `hybrid` trước **11:30**.
- Phong cung cấp `reports/metrics/svd.json` và `ranking.json` cập nhật trước **15:00**.
- Có thể làm UI trước bằng method key; dùng empty state nếu model/file chưa có.

### 4.3 Checklist công việc chi tiết

#### Task 1 — Review UI hiện tại

- [x] Đọc `app/pages/2_Recommendations.py`, `3_Similar_Movies.py`, `4_Compare_Methods.py`, `5_Evaluation.py`, `app/Home.py`.
- [x] Xác nhận app chỉ import `src.service`, không import `src.models`.
- [x] Xác nhận `st.cache_resource` cho service và `st.cache_data` cho metrics.
- [x] Ghi lại các chỗ hard-code 3 phương pháp để cập nhật đồng bộ.

#### Task 2 — Cập nhật Recommendations page

- [x] Selectbox phương pháp gồm 5 lựa chọn:
  - `Popularity` → `popularity`
  - `Content-Based` → `content_based`
  - `Item-Based CF` → `item_cf`
  - `SVD` → `svd`
  - `Hybrid` → `hybrid`
- [x] Cập nhật `help` text: SVD dự đoán rating theo latent factors; Hybrid kết hợp SVD + Item-CF + Content-Based.
- [x] Giữ slider K 5–20 và checkbox “Loại bỏ phim đã xem”.
- [x] Hiển thị method và reason trên card.
- [x] Xử lý danh sách rỗng và lỗi service.
- [x] Không thay đổi hành vi mặc định nếu không cần.

#### Task 3 — Cập nhật Similar Movies page

- [x] Thêm lựa chọn phương pháp:
  - `content_based`
  - `item_cf`
  - `svd`
  - `hybrid`
- [x] Cập nhật caption: Content-Based theo thể loại; Item-CF/SVD theo latent/co-occurrence; Hybrid kết hợp; phim thiếu tín hiệu dùng Popularity.
- [x] Giữ tìm kiếm phim + selectbox + slider K.
- [x] Gọi `service.similar_items(movie_id, k=k, method=method)`.
- [x] Hiển thị method/reason thực tế; không tự suy diễn reason.
- [x] Xử lý phim không tồn tại / không có kết quả.

#### Task 4 — Cập nhật Compare Methods page

- [x] So sánh đủ 5 phương pháp: Popularity, Content-Based, Item-CF, SVD, Hybrid.
- [x] Dùng `st.tabs` để tránh 3 cột bị chật; mỗi tab một phương pháp.
- [x] Hiển thị method/reason/score trên card.
- [x] Ghi rõ thang đo khác nhau:
  - Popularity: điểm phổ biến.
  - Content-Based: cosine `[0, 1]`.
  - Item-CF/SVD: predicted rating `[1, 5]`.
  - Hybrid: blended score `[0, 1]`.
- [x] Không so sánh raw score giữa các tab; chỉ so sánh danh sách.
- [x] Xử lý lỗi từng tab độc lập, không làm sập cả trang.
- [x] AppTest kỳ vọng 5 tab × 10 card = 50 metric với K mặc định 10.

#### Task 5 — Cập nhật Evaluation page

- [x] Đọc baseline qua `get_metrics()` và SVD qua service/`get_svd_metrics()`.
- [x] Hiển thị bảng Rating Prediction:
  - Model
  - RMSE
  - MAE
  - Ghi chú
- [x] Hàng Popularity lấy từ `baseline.json`; hàng SVD lấy từ `svd.json`.
- [x] Nếu thiếu `svd.json`:
  “Chưa có reports/metrics/svd.json. Hãy chạy python scripts/run_svd_eval.py.”
- [x] Giữ phần baseline RMSE/MAE; không ghi đè số liệu Day 1.
- [x] Bảng ranking mở rộng 5 model theo thứ tự:
  Popularity, Content-Based, Item-CF, SVD, Hybrid.
- [x] Giữ các cột: Precision@5, Precision@10, Recall@10, NDCG@10, Coverage@10.
- [x] Cập nhật caption: “5 phương pháp; test set; relevance >= 4.0; không so sánh trực tiếp score”.
- [x] Xử lý `ranking.json` chưa có bằng empty state như hiện tại.
- [x] Bỏ mọi ghi chú còn nói SVD/Hybrid “sẽ có”.

#### Task 6 — Cập nhật Home và cache

- [x] `app/components/service.py`: thêm `get_svd_metrics()` có `@st.cache_data(ttl=60)`, gọi `get_service().get_svd_metrics()`.
- [x] `app/Home.py`:
  - Cập nhật danh sách model: Popularity, Content-Based, Item-CF, SVD, Hybrid.
  - Ghi SVD có rating metrics RMSE/MAE; ranking metrics đủ 5 model.
  - Không thêm metric mới ngoài baseline/SVD.
- [x] Sidebar/home caption phản ánh đủ 5 phương pháp.

#### Task 7 — README và CI

- [x] Cập nhật kiến trúc: SVD và Hybrid đã có.
- [x] Cập nhật roadmap: Day 4 hoàn thành; Day 5 là đánh giá/báo cáo/demo.
- [x] Thêm mục “Kết quả Day 4” chỉ sau khi có số liệu thật:
  - Bảng Rating Prediction: Popularity vs SVD.
  - Bảng ranking metrics 5 model.
  - Ví dụ top-5 SVD và Hybrid cho 1 user.
  - Ví dụ similar movies SVD và Hybrid cho 1 phim.
  - Hạn chế: SVD cần đủ dữ liệu, Hybrid phụ thuộc component, cold-start fallback Popularity, score scale khác nhau.
- [x] Cập nhật lệnh chạy:
  - `python scripts/run_svd_eval.py`
  - `python scripts/smoke_svd_hybrid.py`
- [x] Không ghi đè RMSE/MAE của Popularity.
- [x] Cập nhật CI:
  - `ruff check .`
  - `pytest -q`
  - `python scripts/run_svd_eval.py`
  - `python scripts/run_ranking_eval.py`
  - `python scripts/smoke_item_cf.py`
  - `python scripts/smoke_content_based.py`
  - `python scripts/smoke_svd_hybrid.py`
  - Giữ bước app boundary grep và smoke Surprise nếu thời gian cho phép.
- [x] Nếu tổng thời gian CI vượt 20 phút, tăng `timeout-minutes` lên 30 và ghi lý do trong PR.

#### Task 8 — Kiểm tra app, AppTest và PR

- [x] Chạy `streamlit run app/Home.py`.
- [x] Chọn 3 user, top-10 SVD và Hybrid hiển thị.
- [x] Chọn 3 phim, similar movies SVD và Hybrid hiển thị.
- [x] Compare hiển thị đủ 5 tab, không vỡ layout.
- [x] Evaluation hiển thị rating table và ranking 5 model.
- [x] User không tồn tại không crash.
- [x] `exclude_seen=True` không trả phim đã xem.
- [x] App không import trực tiếp model.
- [x] Sau cache, phản hồi < 2 giây.
- [x] Cập nhật `tests/test_app.py`:
  - Tất cả trang load không exception.
  - Recommendations với `svd`, `hybrid` cho user 1/196/405.
  - Similar Movies với `svd`, `hybrid` cho 3 phim.
  - Compare đủ 5 tab, 50 metric với K=10.
  - Evaluation có 2 dataframe: rating table + ranking table.
- [x] Branch `feat/svd-hybrid`.
- [x] PR title: `feat(model): add SVD and hybrid recommender`.
- [ ] Mô tả What / Why / How tested / Screenshot.
- [x] Gắn ví dụ top-5, rating/ranking metrics, fallback cases.
- [x] Nhờ Huy/Phong review.

### 4.4 Lệnh kiểm tra của Linh

```bash
pytest -q
ruff check .
if grep -R "from src.models" app/; then exit 1; fi
streamlit run app/Home.py
```

### 4.5 Tiêu chí hoàn thành

- [x] Page 2 chọn được 5 phương pháp.
- [x] Page 3 chọn được Content-Based / Item-CF / SVD / Hybrid.
- [x] Page 4 so sánh 5 phương pháp bằng tab, không vỡ layout.
- [x] Page 5 hiển thị RMSE/MAE của Popularity + SVD và ranking 5 model.
- [x] Home mô tả đúng 5 phương pháp.
- [x] App không import trực tiếp model.
- [x] Cache hoạt động.
- [x] README cập nhật.
- [x] AppTest pass.
- [x] CI xanh.
- [x] PR được review + merge.

### 4.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Service API chưa xong | Dùng method key, empty state; tích hợp sau |
| `svd.json` chưa có | Empty state + hướng dẫn chạy script |
| `ranking.json` chưa cập nhật | Empty state hoặc hiển thị model có trong file |
| Cache stale | Clear cache/restart Streamlit khi test |
| Trùng title | Dùng `movie_id` trong selectbox |
| Fallback gây nhầm method | Hiển thị method/reason rõ ràng |
| App import model | CI grep boundary |
| 5 tab bị chật | Dùng tab, card gọn; không dùng 5 cột |
| AppTest đếm metric sai | K=10, 5 tab × 10 card = 50 metric |
| Page config sai thứ tự | `set_page_config` trước UI commands |

### 4.7 Báo cáo cuối ngày

- Đã xong: ...
- App URL/trạng thái: ...
- Trang nào chạy/chưa chạy: ...
- Ví dụ top-5/similar/rating/ranking: ...
- Blocker, đề xuất Day 5: ...

---

## 5. REVIEW CHÉO & TÍCH HỢP

| Người review | Nội dung review | Deadline |
|---|---|---|
| Huy → Phong | SVD rating eval, ranking 5 model, smoke SVD/Hybrid, `svd.json` | 15:00 |
| Huy → Linh | App boundary, cache, error handling, Compare 5 tab, Evaluation | 15:30 |
| Phong → Huy | SVD chỉ dùng train, vector hóa khớp Surprise, Hybrid normalization | 15:00 |
| Linh → Huy | Service API 5 method, app hiển thị method/reason, fallback | 15:30 |
| Cả nhóm | Chạy lại lệnh của nhau trên máy mình | 16:00 |

**Quy tắc review:**
- Ưu tiên correctness, leakage, khả năng chạy, interface.
- Không bắt lỗi style nhỏ nếu không ảnh hưởng.
- Mỗi PR có ít nhất 1 approval.
- Không merge PR của mình khi chưa có người khác review.
- Ghi review vào PR hoặc `notes/day4_review.md` nếu repo chỉ có một tài khoản maintainer.

---

## 6. CHECKLIST CHUNG CUỐI DAY 4

### Model

- [x] `SVDRecommender` đúng contract.
- [x] `HybridRecommender` đúng contract.
- [x] Chỉ dùng train để fit và tạo profile.
- [x] SVD vector hóa khớp `algo.predict`.
- [x] Hybrid normalize đúng, score `[0, 1]`.
- [x] Similar items loại chính nó.
- [x] Fallback Popularity cho cold-start/không tín hiệu.
- [x] Không đọc test data khi fit.
- [x] Kết quả deterministic.

### Rating metrics

- [x] SVD có RMSE/MAE trên test.
- [x] `reports/metrics/svd.json` đúng schema, số liệu thật.
- [x] Baseline Day 1 giữ nguyên.
- [x] Không tune hyperparameter SVD trên test.

### Ranking metrics

- [x] Precision@K đúng công thức.
- [x] Recall@K đúng công thức.
- [x] NDCG@K đúng công thức.
- [x] Relevance threshold 4.0.
- [x] K = 5, 10, 20.
- [x] Macro-average trên user hợp lệ.
- [x] `ranking.json` có đủ 5 model.
- [x] Coverage@10 giữ nguyên định nghĩa.

### Service

- [x] `svd`, `hybrid` đã đăng ký.
- [x] `recommend` và `similar_items` hoạt động với 5 method.
- [x] `get_svd_metrics()` hoạt động.
- [x] Method không hỗ trợ raise `ValueError` rõ ràng, không còn “Day 4”.
- [x] App không import trực tiếp model.

### App

- [x] Page 2 chọn 5 phương pháp.
- [x] Page 3 chọn 4 phương pháp similar.
- [x] Page 4 so sánh 5 phương pháp bằng tab.
- [x] Page 5 hiển thị rating + ranking 5 model.
- [x] Hiển thị method/reason.
- [x] User không tồn tại không crash.
- [x] `exclude_seen=True` hoạt động.
- [x] AppTest pass.

### Test & tài liệu

- [x] `pytest -q` pass, số test tăng so với 67.
- [x] `ruff check .` pass.
- [x] CI xanh.
- [x] `run_svd_eval.py` chạy.
- [x] `run_ranking_eval.py` chạy.
- [x] `smoke_svd_hybrid.py` chạy.
- [x] README cập nhật Day 4.
- [x] `docs/evaluation_protocol.md` cập nhật.
- [x] Có `notes/day4_eval.md` và `notes/day4_report.md`.
- [x] Không commit data/model/secret.
- [x] PR có review.

---

## 7. QUY TẮC GIT

### Branch

- Dùng chung branch `feat/svd-hybrid`.
- Không push trực tiếp lên `main`.
- Không dùng lại nhánh Day 1/Day 2/Day 3.

### Commit message gợi ý

```text
feat(model): add SVD recommender
feat(model): add hybrid recommender
feat(eval): add SVD rating evaluation and extend ranking to five models
feat(service): integrate svd and hybrid methods
feat(app): show five methods and SVD metrics
test(model): add SVD and hybrid tests
docs(readme): document Day 4 results
```

### PR

- PR nhỏ, có mô tả What / Why / How tested / Screenshot.
- Ít nhất 1 reviewer.
- Squash merge.
- Không commit raw data, model artifact, `.env`, secret.
- `svd.json` và `ranking.json` được commit vì nhỏ và tất định.

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

1. SVD model đúng + fallback.
2. SVD rating eval + `svd.json`.
3. Service tích hợp `svd`, `hybrid`.
4. Hybrid model đúng + test.
5. Ranking eval 5 model + `ranking.json`.
6. App page 2, 3, 4, 5.
7. Unit test + smoke script.
8. README + đánh giá định tính.
9. PR/CI.

---

## 9. PHỤ LỤC — CÔNG THỨC & QUY ƯỚC

### SVD prediction

```text
est(u, i) = mu + b_u + b_i + p_u · q_i
predicted_rating(u, i) = clip(est(u, i), 1, 5)
```

Trong đó:
- `mu`: global mean của train.
- `b_u`, `b_i`: user/item bias.
- `p_u`, `q_i`: user/item latent factors.
- Chỉ dùng cho phim có factor trong trainset.

### SVD similar items

```text
sim(i, j) = cosine(q_i, q_j)
similarity = clip(sim, 0, 1)
```

- Bỏ diagonal.
- Chỉ giữ `score > 0`.
- Phim không có factor: không tham gia similarity.

### Hybrid blend

```text
norm_m(i) = (score_m(i) - min_m) / (max_m - min_m)
hybrid(i) = sum_m weight_m * norm_m(i)
```

- Nếu `max_m == min_m`: `norm_m(i) = 1.0`.
- Item không có trong component `m`: phần đóng góp bằng `0`.
- Chỉ blend item native của component.
- Fallback Popularity sau blend.

### Trọng số mặc định

| Thành phần | Recommend | Similar |
|---|---:|---:|
| SVD | 0.5 | 0.3 |
| Item-CF | 0.3 | 0.4 |
| Content-Based | 0.2 | 0.3 |

### Hyperparameter SVD

| Tham số | Giá trị |
|---|---:|
| `n_factors` | 100 |
| `n_epochs` | 20 |
| `lr_all` | 0.005 |
| `reg_all` | 0.02 |
| `random_state` | 42 |

### Thang đo score

| Phương pháp | Ý nghĩa score | Khoảng |
|---|---|---:|
| Popularity | Điểm phổ biến/Bayesian average | Tùy dữ liệu |
| Content-Based | Cosine thể loại | `[0, 1]` |
| Item-CF recommend | Predicted rating | `[1, 5]` |
| Item-CF similar | Cosine centered ratings | `(0, 1]` |
| SVD recommend | Predicted rating | `[1, 5]` |
| SVD similar | Cosine latent factors | `(0, 1]` |
| Hybrid | Blended normalized score | `[0, 1]` |

Không so sánh trực tiếp score giữa các phương pháp; chỉ so sánh ranking metrics.

### Reason strings

| Trường hợp | method | reason |
|---|---|---|
| SVD recommend native | `svd` | `Dự đoán theo sở thích cá nhân (SVD)` |
| SVD similar native | `svd` | `Cùng gu người dùng (SVD)` |
| SVD/Hybrid cold-start | `popularity` | `Fallback phổ biến (cold-start)` |
| SVD/Hybrid thiếu tín hiệu | `popularity` | `Fallback phổ biến (thiếu tín hiệu)` |
| Hybrid recommend native | `hybrid` | `Kết hợp SVD + Item-CF + Content-Based` |
| Hybrid similar native | `hybrid` | `Kết hợp độ tương đồng SVD + Item-CF + Content-Based` |

### Quy ước chung

- Duplicate `movie_id` chỉ tính lần đầu.
- Nếu `relevant(u)` rỗng: bỏ user khỏi evaluation, tăng `n_users_skipped`.
- Nếu K lớn hơn số recommendation trả về: precision vẫn chia cho K.
- Tie-break score bằng `movie_id` tăng dần.
- Không dùng test để chọn hyperparameter/trọng số/ngưỡng.
- Không so sánh trực tiếp score giữa các phương pháp; chỉ so sánh ranking metrics.
- Không thêm comment/docstring mới vào code theo `AGENTS.md`.
- Windows local: dùng `.\.venv\python.exe` thay cho `python`; nếu lỗi encoding tiếng Việt, đặt `$env:PYTHONIOENCODING = "utf-8"`.
