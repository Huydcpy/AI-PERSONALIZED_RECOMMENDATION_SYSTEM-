# TASK DAY 2 — 06/11/2026

## Hướng dẫn chi tiết cho 3 thành viên

**Dự án:** AI Personalized Recommendation System (MovieLens 100K)

**Mục tiêu Day 2:** Có luồng Content-Based Filtering hoàn chỉnh:
**user → top-K theo nội dung → similar movies → hiển thị trên Streamlit**.

**Demo cuối ngày:**
- Chọn 3 user khác nhau, xem top-10 Content-Based.
- Chọn 3 phim khác nhau, xem phim tương tự.
- So sánh nhanh với Popularity để thấy sự khác biệt.
- Kiểm tra fallback với user lạ và phim không có genre.

---

## 0. PHÂN CÔNG TỔNG QUAN

| Thành viên | Vai trò | Phụ trách chính | Deliverable | Branch |
|---|---|---|---|---|
| **Huy (Trưởng nhóm)** | ML core + tích hợp | Content-Based model, service, unit test, review, merge | `src/models/content_based.py`, `src/service/recommender_service.py`, `tests/test_content_based.py` | `feat/content-based` |
| **Phong** | Data & Evaluation | Kiểm tra feature thể loại, đánh giá định tính, smoke script, demo | `scripts/smoke_content_based.py`, `notes/day2_eval.md` | `feat/content-based` |
| **Linh** | Product & Integration | App Recommendations / Similar Movies / Compare, README, CI, PR | `app/pages/2_Recommendations.py`, `app/pages/3_Similar_Movies.py`, `app/pages/4_Compare_Methods.py`, `README.md` | `feat/content-based` |

**Nguyên tắc phối hợp:**
- Tất cả làm trên **một branch chung** `feat/content-based` để tránh conflict.
- Huy chốt model/service trước 11:00 để Linh và Phong tích hợp.
- Linh có thể làm UI trước bằng method key `content_based`, empty state nếu model chưa xong.
- Phong có thể làm feature audit ngay từ đầu, chưa cần chờ model.
- Không ai sửa file của người khác khi chưa trao đổi.
- Review chéo qua PR trước khi merge.

### Quyết định kỹ thuật mặc định

- Dùng **genre-only** với 18 cột thể loại đã biết; bỏ `unknown`.
- Không dùng title TF-IDF ở Day 2 để tránh nhiễu và giữ khả năng giải thích.
- Method key: `content_based`.
- Fallback: Popularity.
- Không đổi contract `src/models/base.py`.
- Không đọc test data khi fit/tạo profile.
- Không thêm dependency mới; `scikit-learn` đã có trong `requirements.txt`.

### Trạng thái đầu vào

- Day 1 đã merge vào `main`, CI xanh.
- Data, baseline, app 5 trang, service layer đã có.
- Contract `src/models/base.py` đã chốt.
- PR #5 (`linh-day1`) còn open, cần đóng vì đã được thay bằng PR #6.

### Việc cần dọn trước khi bắt đầu

- [ ] Sync local `main` lên `origin/main` mới nhất.
- [ ] Đóng PR #5 với ghi chú “superseded by #6”.
- [ ] Tạo `notes/day1_report.md` ngắn.
- [ ] Tạo branch `feat/content-based`.
- [ ] Xác nhận `git status` sạch.

**Lệnh gợi ý:**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch -c feat/content-based
```

---

## 1. MỐC THỜI GIAN & BÀN GIAO

| Giờ | Việc chung | Huy | Phong | Linh |
|---|---|---|---|---|
| 09:00–09:30 | Sync, đóng PR #5, chốt genre-only | Chủ trì | Tham gia | Tham gia |
| 09:30–10:30 | Model + feature audit | Viết model | Audit genre | Review UI hiện tại |
| **10:30** | **Model content-based chạy được** | Báo tiến độ | Báo cáo feature | Bắt đầu page 2 |
| 10:30–11:30 | Service + test | Service, unit test | Viết smoke script | Page 2, method selector |
| 12:00 | Sync nhanh 5 phút | Báo tiến độ | Báo tiến độ | Báo tiến độ |
| 13:30–15:00 | App + đánh giá | Review/integration | Chạy eval định tính | Page 3/4, README |
| 15:00–15:45 | Smoke test, demo data | Chạy service | Tổng hợp ví dụ | Chạy AppTest |
| 15:45–16:30 | Review, CI, merge | Review/merge | Review | PR/CI |
| 16:30–17:00 | Chốt Day 2 | Viết báo cáo | Cập nhật eval | Cập nhật README |

---

## 2. HƯỚNG DẪN CHO HUY (TRƯỞNG NHÓM)

### 2.1 Mục tiêu cá nhân

Có `ContentBasedRecommender` đúng contract, tích hợp vào service, có unit test bằng dữ liệu giả, review và merge toàn bộ Day 2.

### 2.2 Phụ thuộc

- Day 1 đã merged; data `train.parquet`, `movies.parquet` sẵn sàng.
- Không phụ thuộc Phong/Linh để bắt đầu model.
- Service cần xong trước 11:30 để Linh tích hợp app.
- Phong cần model/service để chạy đánh giá định tính.

### 2.3 Checklist công việc chi tiết

#### Task 1 — Tạo `src/models/content_based.py`

**Feature matrix:**
- [ ] Lấy 18 genre từ `movies_df`, bỏ `unknown`:
  `action`, `adventure`, `animation`, `children`, `comedy`, `crime`,
  `documentary`, `drama`, `fantasy`, `film_noir`, `horror`, `musical`,
  `mystery`, `romance`, `sci_fi`, `thriller`, `war`, `western`.
- [ ] Tạo `genre_matrix` kích thước `n_movies × 18`.
- [ ] Chuẩn hóa L2 từng vector phim.
- [ ] Lưu mapping:
  - `movie_ids`
  - `movie_id_to_index`
  - `index_to_movie_id`
  - `similarity` — cosine `n_movies × n_movies`
- [ ] Phim không có genre: vector zero, không crash.
- [ ] Không dùng test data.

**Ghi chú:** similarity matrix 1.682 phim khoảng 11 MB, chấp nhận được.

#### Task 2 — Implement `ContentBasedRecommender`

API dự kiến:

```python
class ContentBasedRecommender:
    name = "content_based"

    def __init__(self, train_df, movies_df, fallback=None):
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

**User profile:**
- [ ] Chỉ lấy rating của user trong `train_df`.
- [ ] Trọng số: `max(rating - 3.0, 0.0)`.
- [ ] Profile = weighted average genre vector.
- [ ] Chuẩn hóa profile.
- [ ] Nếu user không có rating / profile zero:
  - fallback Popularity.
  - method `"popularity"`.
  - reason `"Fallback phổ biến (cold-start)"`.

**`recommend`:**
- [ ] Score = cosine(profile, genre vector).
- [ ] Chỉ giữ phim có `score > 0`.
- [ ] `exclude_seen=True`: loại phim user đã rating trong **train**.
- [ ] Sort `score` giảm dần, tie-break `movie_id` tăng dần.
- [ ] Trả tối đa `k`.
- [ ] Item content-based:
  - `method="content_based"`.
  - reason `"Khớp thể loại: Action, Sci-Fi"`.
  - Không giao thể loại: `"Nội dung tương tự"`.
- [ ] Không đủ item / không có tín hiệu: fallback Popularity.

**`similar_items`:**
- [ ] Lấy similarity vector của phim gốc.
- [ ] Loại chính nó.
- [ ] Chỉ giữ `score > 0`.
- [ ] Sort giảm dần, tie-break `movie_id`.
- [ ] `method="content_based"`.
- [ ] reason `"Cùng thể loại: Comedy, Romance"`.
- [ ] Phim không có genre / không có kết quả: fallback Popularity.
- [ ] Movie ID không tồn tại: raise `ValueError("Movie ... không tồn tại")`.

#### Task 3 — Tích hợp service

Sửa `src/service/recommender_service.py`:
- [ ] Khởi tạo Popularity trước.
- [ ] Khởi tạo ContentBased với fallback là Popularity.
- [ ] Thêm `self.models["content_based"]`.
- [ ] `recommend(..., method="content_based")` hoạt động.
- [ ] Method không hỗ trợ:
  `ValueError("Method ... sẽ có từ Day 3/4")`.
- [ ] Thêm `method` optional cho `similar_items`:
  ```python
  def similar_items(
      self, movie_id: int, k: int = 10, method: str = "content_based"
  ) -> list[Recommendation]:
  ```
- [ ] Nếu content-based chưa sẵn sàng, fallback Popularity.
- [ ] Không đổi response contract.
- [ ] Service vẫn không import Streamlit.

**Lưu ý:** app hiện gọi `service.similar_items(movie_id, k=k)` nên mặc định mới sẽ tự dùng Content-Based.

#### Task 4 — Unit test

Tạo `tests/test_content_based.py` với DataFrame giả:
- [ ] `similar_items` trả phim cùng genre trước.
- [ ] `similar_items` loại chính nó và tôn trọng `k`.
- [ ] `recommend` loại phim đã xem khi `exclude_seen=True`.
- [ ] User lạ fallback Popularity, không crash.
- [ ] Phim không genre fallback.
- [ ] Kết quả deterministic khi score bằng nhau.
- [ ] Score trong `[0, 1]`.
- [ ] Method content-based là `"content_based"`.
- [ ] Method fallback là `"popularity"`.
- [ ] Không phụ thuộc data thật.

#### Task 5 — Review & tích hợp

- [ ] Review feature audit của Phong: genre coverage, phim không genre.
- [ ] Review app của Linh: không import trực tiếp model, cache, error handling.
- [ ] Chạy:
  ```bash
  pytest -q
  ruff check .
  python scripts/smoke_content_based.py
  ```
- [ ] Kiểm tra `git status`: không có data/model lớn.
- [ ] Review PR, merge khi CI xanh.
- [ ] Viết `notes/day2_report.md`.

### 2.4 Lệnh kiểm tra của Huy

```bash
pytest tests/test_content_based.py -q
pytest -q
ruff check .
python -c "from src.service.recommender_service import RecommenderService; s=RecommenderService(); print(s.recommend(196, method='content_based', k=5))"
python scripts/smoke_content_based.py
```

### 2.5 Tiêu chí hoàn thành

- [ ] `ContentBasedRecommender` đúng contract.
- [ ] `recommend` trả top-K content-based cho user hợp lệ.
- [ ] `similar_items` trả phim cùng thể loại, loại chính nó.
- [ ] User lạ fallback Popularity, không crash.
- [ ] Phim không genre fallback Popularity.
- [ ] Service hỗ trợ `popularity` và `content_based`.
- [ ] Unit test pass, không phụ thuộc data thật.
- [ ] Review xong PR của Phong và Linh.
- [ ] PR được merge, CI xanh.
- [ ] Có báo cáo Day 2.

### 2.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Genre-only quá thô | Ghi rõ hạn chế; reason theo thể loại |
| User chỉ rating thấp | Profile zero → fallback Popularity |
| Phim không genre | Vector zero → fallback Popularity |
| Similarity matrix tốn RAM | 1.682 phim, ~11 MB; chấp nhận |
| Fallback che lỗi model | Ghi method và reason rõ ràng |
| Test phụ thuộc data thật | Dùng DataFrame giả |
| App import model trực tiếp | Giữ boundary, CI grep kiểm tra |

### 2.7 Báo cáo cuối ngày

Gửi nhóm 5 dòng:
- Đã xong: ...
- Model/method: ...
- Ví dụ top-5: ...
- Fallback/test: ...
- Blocker và đề xuất Day 3: ...

---

## 3. HƯỚNG DẪN CHO PHONG

### 3.1 Mục tiêu cá nhân

Kiểm tra chất lượng feature thể loại, xây dựng đánh giá định tính và smoke script để chứng minh Content-Based hoạt động đúng.

### 3.2 Phụ thuộc

- Data `movies.parquet`, `train.parquet` đã có.
- Có thể làm feature audit ngay.
- Cần model/service của Huy trước 11:30 để chạy smoke script.
- Cần app của Linh trước 15:00 để đối chiếu kết quả hiển thị.

### 3.3 Checklist công việc chi tiết

#### Task 1 — Audit feature thể loại

- [ ] Đọc `movies.parquet`, xác nhận đủ 1.682 phim.
- [ ] Xác nhận đủ 19 cột genre.
- [ ] Thống kê số phim theo từng genre.
- [ ] Đếm số phim không có genre nào (18 cột known đều bằng 0).
- [ ] Kiểm tra tỷ lệ `unknown`.
- [ ] Liệt kê top genre và các genre ít phổ biến.
- [ ] Ghi nhận các phim không có genre để dùng làm case fallback.
- [ ] Ghi kết quả vào `notes/day2_eval.md`.

#### Task 2 — Chuẩn bị case đánh giá định tính

- [ ] Chọn 3 user: `1`, `196`, `405`.
- [ ] Chọn 3 phim:
  - `Toy Story (1)`
  - `Star Wars (50)`
  - `Pulp Fiction (296)`
- [ ] Xác định thể loại kỳ vọng của từng phim.
- [ ] Định nghĩa tiêu chí đánh giá:
  - Top-5 có cùng genre với profile không?
  - Có phim đã xem bị lọt vào không?
  - Similar movies có cùng genre với phim gốc không?
  - Có phim không genre bị trả về không?
  - Fallback có đúng method/reason không?

#### Task 3 — Viết `scripts/smoke_content_based.py`

- [ ] Load `RecommenderService`.
- [ ] In top-5 content-based cho user `1`, `196`, `405`.
- [ ] In similar movies cho 3 phim ở trên.
- [ ] In method và reason của từng item.
- [ ] Kiểm tra không có phim đã xem trong top-10 (dùng train).
- [ ] Kiểm tra user `999999` fallback Popularity.
- [ ] Kiểm tra phim không genre fallback.
- [ ] Script không import Streamlit, chỉ dùng service.
- [ ] Exit code khác 0 nếu có case fail.

#### Task 4 — Chạy đánh giá và ghi nhận

- [ ] Chạy script sau khi Huy xong service.
- [ ] Ghi kết quả thực tế vào `notes/day2_eval.md`.
- [ ] Ghi các case bất thường:
  - Similarity thấp.
  - Gợi ý lệch genre.
  - Fallback ngoài dự kiến.
- [ ] Chưa tính RMSE/MAE cho Content-Based.
- [ ] Ranking metrics để Day 3.

#### Task 5 — Review chéo

- [ ] Review model của Huy: chỉ dùng train, không leakage.
- [ ] Review app của Linh: kết quả hiển thị đúng method/reason.
- [ ] Chạy lại lệnh của Huy và Linh trên máy mình.

### 3.4 Lệnh kiểm tra của Phong

```bash
python scripts/smoke_content_based.py
pytest tests/test_content_based.py -q
python -c "import pandas as pd; m=pd.read_parquet('data/processed/movies.parquet'); print(m.shape); print(m.filter(like='action').sum())"
```

### 3.5 Tiêu chí hoàn thành

- [ ] Feature audit đầy đủ.
- [ ] Smoke script chạy được, exit code đúng.
- [ ] Đã đánh giá 3 user và 3 phim.
- [ ] Đã kiểm tra user lạ và phim không genre.
- [ ] Không có phim đã xem trong top-K.
- [ ] Có `notes/day2_eval.md`.
- [ ] Review xong model và app.

### 3.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Genre quá thô, đánh giá chủ quan | Ghi rõ tiêu chí và ví dụ |
| Trùng title | Dùng `movie_id` |
| User cold-start | Kiểm tra fallback Popularity |
| Phim không genre | Dùng làm case fallback |
| Data chưa có | Chạy pipeline trước, báo Huy |
| Script phụ thuộc app | Chỉ dùng service |

### 3.7 Báo cáo cuối ngày

- Đã xong: ...
- Feature findings: ...
- Ví dụ top-5: ...
- Similar movies: ...
- Fallback/test: ...
- Blocker, đề xuất Day 3: ...

---

## 4. HƯỚNG DẪN CHO LINH

### 4.1 Mục tiêu cá nhân

Đưa Content-Based lên Streamlit app, cập nhật README/CI, đảm bảo app chỉ gọi service, có cache và xử lý lỗi.

### 4.2 Phụ thuộc

- Huy giao service có method `content_based` trước 11:30.
- Phong cung cấp ví dụ/expected genres trước 15:00.
- Có thể làm UI trước bằng method key, dùng empty state nếu model chưa xong.

### 4.3 Checklist công việc chi tiết

#### Task 1 — Review UI hiện tại

- [ ] Đọc `app/pages/2_Recommendations.py`.
- [ ] Đọc `app/pages/3_Similar_Movies.py`.
- [ ] Đọc `app/pages/4_Compare_Methods.py`.
- [ ] Xác nhận app chỉ import `src.service`, không import `src.models`.
- [ ] Xác nhận cache đang dùng đúng.

#### Task 2 — Cập nhật Recommendations page

- [ ] Selectbox phương pháp:
  - `Popularity` → `popularity`
  - `Content-Based` → `content_based`
- [ ] Giữ slider K 5–20.
- [ ] Giữ checkbox “Loại bỏ phim đã xem”.
- [ ] Hiển thị method và reason trên card.
- [ ] Xử lý danh sách rỗng.
- [ ] Xử lý lỗi service.

#### Task 3 — Cập nhật Similar Movies page

- [ ] Bỏ note “Day 1 dùng fallback popularity”.
- [ ] Giữ tìm kiếm phim + selectbox.
- [ ] Dùng `service.similar_items` mặc định content-based.
- [ ] Hiển thị lý do “Cùng thể loại: ...”.
- [ ] Xử lý phim không tồn tại / không có kết quả.
- [ ] Không thêm `list_movies` nếu không cần.

#### Task 4 — Cập nhật Compare/Home

- [ ] `app/pages/4_Compare_Methods.py`:
  - Popularity: có.
  - Content-Based: có.
  - Item-CF, SVD, Hybrid: sẽ làm Day 3–4.
- [ ] `app/Home.py`:
  - Cập nhật mô tả model hiện có.
  - Không cần thêm metric mới.

#### Task 5 — README và CI

- [ ] Cập nhật kiến trúc: Content-Based đã có.
- [ ] Cập nhật roadmap Day 2.
- [ ] Thêm mục “Kết quả Day 2”:
  - phương pháp.
  - ví dụ top-5 cho 1 user.
  - ví dụ similar movies cho 1 phim.
  - hạn chế: genre-only, cold-start, popularity fallback.
- [ ] Cập nhật lệnh chạy smoke test mới.
- [ ] Không ghi đè RMSE/MAE của Popularity.
- [ ] Kiểm tra CI vẫn chạy `ruff check .` và `pytest -q`.

#### Task 6 — Kiểm tra app

- [ ] Chạy `streamlit run app/Home.py`.
- [ ] Chọn 3 user, top-10 content-based hiển thị.
- [ ] Chọn 3 phim, similar movies hiển thị.
- [ ] User không tồn tại không crash.
- [ ] `exclude_seen=True` không trả phim đã xem.
- [ ] App không import trực tiếp model.
- [ ] Sau cache, phản hồi < 2 giây.
- [ ] Chạy AppTest cho 5 trang.

#### Task 7 — PR

- [ ] Branch `feat/content-based`.
- [ ] PR title: `feat(model): add content-based recommender and similar movies`.
- [ ] Mô tả What / Why / How tested / Screenshot.
- [ ] Gắn ví dụ top-5 và similar movies.
- [ ] Ghi rõ fallback cases.
- [ ] Nhờ Huy/Phong review.

### 4.4 Lệnh kiểm tra của Linh

```bash
pytest -q
ruff check .
if grep -R "from src.models" app/; then exit 1; fi
streamlit run app/Home.py
```

### 4.5 Tiêu chí hoàn thành

- [ ] Page 2 chọn được Popularity / Content-Based.
- [ ] Page 3 dùng content-based, hiển thị reason.
- [ ] Page 4/Home cập nhật trạng thái.
- [ ] App không import trực tiếp model.
- [ ] Cache hoạt động.
- [ ] README cập nhật.
- [ ] CI xanh.
- [ ] PR được review + merge.

### 4.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Service API chưa xong | Dùng method key, empty state; tích hợp sau |
| Cache stale | Clear cache/restart Streamlit khi test |
| Trùng title | Dùng `movie_id` trong selectbox |
| Fallback gây nhầm method | Hiển thị method/reason rõ ràng |
| App import model | CI grep boundary |
| Page config sai thứ tự | `set_page_config` trước UI commands |

### 4.7 Báo cáo cuối ngày

- Đã xong: ...
- App URL/trạng thái: ...
- Trang nào chạy/chưa chạy: ...
- Ví dụ top-5/similar movies: ...
- Blocker, đề xuất Day 3: ...

---

## 5. REVIEW CHÉO & TÍCH HỢP

| Người review | Nội dung review | Deadline |
|---|---|---|
| Huy → Phong | Feature audit, smoke script, fallback cases | 15:00 |
| Huy → Linh | App boundary, cache, error handling | 15:30 |
| Phong → Huy | Model chỉ dùng train, similarity/recommend đúng | 15:00 |
| Linh → Huy | Service API, app hiển thị method/reason | 15:30 |
| Cả nhóm | Chạy lại lệnh của nhau trên máy mình | 16:00 |

**Quy tắc review:**
- Ưu tiên correctness, leakage, khả năng chạy, interface.
- Không bắt lỗi style nhỏ nếu không ảnh hưởng.
- Mỗi PR có ít nhất 1 approval.
- Không merge PR của mình khi chưa có người khác review.

---

## 6. CHECKLIST CHUNG CUỐI DAY 2

### Model
- [ ] `ContentBasedRecommender` đúng contract.
- [ ] Chỉ dùng train để tạo profile.
- [ ] Similar items cùng genre, loại chính nó.
- [ ] Fallback Popularity cho cold-start/không genre.
- [ ] Không đọc test data.

### Service
- [ ] `content_based` đã đăng ký.
- [ ] `recommend` và `similar_items` hoạt động.
- [ ] Method không hỗ trợ raise `ValueError` rõ ràng.
- [ ] App không import trực tiếp model.

### App
- [ ] Page 2 chọn 2 phương pháp.
- [ ] Page 3 dùng content-based.
- [ ] Hiển thị method/reason.
- [ ] User không tồn tại không crash.
- [ ] `exclude_seen=True` hoạt động.

### Test & tài liệu
- [ ] `pytest -q` pass.
- [ ] `ruff check .` pass.
- [ ] CI xanh.
- [ ] Smoke script chạy.
- [ ] README cập nhật.
- [ ] Có `notes/day2_eval.md` và `notes/day2_report.md`.
- [ ] Không commit data/model/secret.
- [ ] PR có review.

---

## 7. QUY TẮC GIT

### Branch
- Dùng chung branch `feat/content-based`.
- Không push trực tiếp lên `main`.
- Không dùng nhánh `linh-day1`.

### Commit message gợi ý

```text
feat(model): add content-based recommender
feat(service): integrate content-based recommendations
feat(app): add content-based method and similar movies
test(model): add content-based tests
docs(readme): document Day 2 results
```

### PR
- PR nhỏ, có mô tả What / Why / How tested / Screenshot.
- Ít nhất 1 reviewer.
- Squash merge.
- Không commit raw data, model artifact, `.env`, secret.

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
1. Content-Based model đúng + fallback.
2. Service integration.
3. App page 2 + page 3.
4. Unit test + smoke script.
5. README + đánh giá định tính.
6. PR/CI.
