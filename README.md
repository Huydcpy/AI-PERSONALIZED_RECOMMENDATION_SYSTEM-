# AI Personalized Recommendation System

Hệ thống gợi ý phim cá nhân hóa xây dựng trên bộ dữ liệu **MovieLens 100K**, hướng tới một luồng end-to-end hoàn chỉnh: **data → model → service → giao diện Streamlit**.

Mục tiêu của dự án:

- Xây dựng pipeline dữ liệu sạch, chia train/test chống leakage.
- Triển khai nhiều phương pháp gợi ý: Popularity, Content-Based, Item-CF, SVD, Hybrid.
- Đánh giá bằng rating metrics (RMSE/MAE) và ranking metrics (Precision@K, Recall@K, NDCG@K).
- Cung cấp giao diện web để chọn user, xem hồ sơ, nhận top-K gợi ý và so sánh phương pháp.

## Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ | Python 3.11 |
| Xử lý dữ liệu | pandas, NumPy, PyArrow (Parquet) |
| Machine Learning | scikit-surprise, scikit-learn, SciPy |
| Giao diện | Streamlit |
| Trực quan hóa | Matplotlib, Seaborn |
| Kiểm thử & chất lượng code | pytest, ruff |
| CI | GitHub Actions |
| Cấu hình | YAML (`configs/config.yaml`) |

## Kiến trúc tổng quan

Dự án được tổ chức theo kiến trúc phân lớp, tách biệt rõ ràng giữa dữ liệu, model, đánh giá, service và giao diện.

```mermaid
flowchart TD
    A[MovieLens 100K<br/>raw data] --> B[Data Pipeline<br/>download → preprocess → split]
    B --> C[(data/processed<br/>ratings / movies / users / train / test)]

    C --> D[Models<br/>Popularity · Content-Based · Item-CF · SVD · Hybrid]
    C --> E[Evaluation<br/>RMSE/MAE · Precision@K/Recall@K/NDCG@K]
    D --> E
    E --> F[(reports/metrics<br/>baseline.json ...)]

    D --> G[RecommenderService<br/>src/service]
    C --> G
    F --> G

    G --> H[Streamlit App<br/>app/Home.py + pages/]
    H --> I[Người dùng<br/>chọn user → xem top-K gợi ý]
```

### Các lớp chính

1. **Data layer (`src/data`)** — Tải dữ liệu, chuẩn hóa schema, validate, lưu Parquet và chia train/test (`u1.base` / `u1.test`).
2. **Model layer (`src/models`)** — Mỗi recommender implement chung contract `Recommender` (Protocol), trả về danh sách `Recommendation` gồm `movie_id`, `title`, `score`, `method`, `reason`.
3. **Evaluation layer (`src/evaluation`)** — Tính rating metrics và ranking metrics; kết quả ghi ra `reports/metrics/`.
4. **Service layer (`src/service`)** — `RecommenderService` là điểm truy cập duy nhất cho UI: load dữ liệu, quản lý model, xử lý user không tồn tại, trả metrics.
5. **Presentation layer (`app/`)** — Streamlit app gồm 5 trang: Home, User Profile, Recommendations, Similar Movies, Compare Methods, Evaluation.

### Nguyên tắc thiết kế

- **Tách biệt UI và model**: app chỉ gọi qua `RecommenderService`, không import trực tiếp `src.models`.
- **Contract thống nhất**: mọi model tuân theo `src/models/base.py`.
- **Chống leakage**: test chỉ dùng một lần để đánh giá, không dùng để fit/tuning; lịch sử user chỉ lấy từ train.
- **Tái lập được**: seed cố định `42`, cấu hình tập trung trong `configs/`.
- **Cache**: `st.cache_data` cho dữ liệu/JSON, `st.cache_resource` cho service.

## Cấu trúc repository

```text
.
├── .github/
│   └── workflows/ci.yml    # Lint + test trên GitHub Actions
├── app/                    # Streamlit app (Home + pages + components)
├── configs/                # Cấu hình dự án (config.yaml)
├── data/
│   ├── raw/                # Dữ liệu gốc MovieLens (không commit)
│   └── processed/          # Parquet đã xử lý (không commit)
├── docs/                   # Data card, evaluation protocol
├── models/                 # Model artifacts (không commit)
├── notebooks/              # EDA, thử nghiệm
├── reports/
│   ├── figures/            # Biểu đồ EDA
│   └── metrics/            # Kết quả đánh giá (JSON)
├── scripts/                # run_baseline.py, smoke_surprise.py
├── src/
│   ├── data/               # download, preprocess, splits
│   ├── models/             # base contract + các recommender
│   ├── evaluation/         # rating & ranking metrics
│   └── service/            # RecommenderService
├── tests/                  # Unit tests
├── requirements.txt
└── README.md
```

## Dataset

- **MovieLens 100K** (GroupLens): 100.000 ratings, 943 users, 1.682 movies.
- Đánh giá tường minh (explicit feedback), thang điểm 1–5.
- Split chuẩn: `u1.base` (80.000) / `u1.test` (20.000).
- Độ thưa: `1 - 100000 / (943 × 1682) ≈ 93,7%`.
- Nguồn: <https://files.grouplens.org/datasets/movielens/ml-100k.zip>
- License: theo điều khoản sử dụng của GroupLens.

## Cài đặt

Yêu cầu Python 3.11.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> Nếu cài `scikit-surprise` lỗi, thử: `pip install "numpy<2.0" cython` rồi cài lại `scikit-surprise==1.1.4`.

## Chạy dự án

```bash
# 1. Tải và xử lý dữ liệu
python -m src.data.download
python -m src.data.preprocess
python -m src.data.splits

# 2. Huấn luyện baseline và đánh giá
python scripts/run_baseline.py

# 3. Kiểm tra môi trường Surprise (không phải kết quả chính thức)
python scripts/smoke_surprise.py

# 4. Chạy test và lint
pytest -q
ruff check .

# 5. Chạy giao diện
streamlit run app/Home.py
```

## Kết quả Day 1

| Model | RMSE | MAE | Ghi chú |
|---|---|---|---|
| Popularity (Bayesian average) | 1.06698 | 0.86310 | Baseline, dự đoán theo điểm phổ biến |

Chi tiết trong `reports/metrics/baseline.json`.

## Roadmap

| Ngày | Nội dung |
|---|---|
| Day 1 | Data pipeline, popularity baseline, rating metrics, Streamlit app |
| Day 2 | Đã triển khai Content-Based Filtering, Similar Movies và Compare Methods; kiểm chứng local trong notes/day2_eval.md |
| Day 3 | Item-CF, ranking metrics (Precision@K, Recall@K, NDCG@K) |
| Day 4 | SVD, Hybrid, trang so sánh phương pháp |
| Day 5 | Hoàn thiện đánh giá, báo cáo và demo |

## Hạn chế

- Dữ liệu MovieLens 100K có từ 1997–1998, không phản ánh sở thích hiện tại.
- Chỉ có explicit feedback, không có implicit signals (click, thời gian xem).
- Genre thô, chưa khai thác nội dung phim (mô tả, poster, diễn viên).
- Dữ liệu thưa (~93,7%) và có popularity bias.

## Day 2 results

Content-Based is available in the service, Recommendations, Similar Movies, and Compare Methods. It uses 18 known genres, L2 normalization, cosine similarity, and train-only profiles weighted by max(rating - 3, 0). Cold-start users, zero-genre movies, and short result lists use Popularity fallback. Cards show the actual method and reason.

Method key la `content_based` (goi qua `service.recommend(user_id, method="content_based", k=k)` va mac dinh `service.similar_items(movie_id, k=k)`). Ly do hien thi: `Khop the loai: ...` cho goi y theo user va `Cung the loai: ...` cho Similar Movies.

User `196`, Top-5 goi y Content-Based (`method="content_based"`, `k=5`, `exclude_seen=True`):

| movie_id | Title | Score | Reason |
|---|---|---|---|
| 34 | Doom Generation, The (1995) | 0.9136 | Khop the loai: Comedy, Drama |
| 45 | Eat Drink Man Woman (1994) | 0.9136 | Khop the loai: Comedy, Drama |
| 47 | Ed Wood (1994) | 0.9136 | Khop the loai: Comedy, Drama |
| 65 | What's Eating Gilbert Grape (1993) | 0.9136 | Khop the loai: Comedy, Drama |
| 93 | Welcome to the Dollhouse (1995) | 0.9136 | Khop the loai: Comedy, Drama |

Phim `1` — Toy Story (1995), Top-5 phim tuong tu (`similar_items(movie_id=1, k=5)`):

| movie_id | Title | Score | Reason |
|---|---|---|---|
| 422 | Aladdin and the King of Thieves (1996) | 1.0000 | Cung the loai: Animation, Children, Comedy |
| 95 | Aladdin (1992) | 0.8660 | Cung the loai: Animation, Children, Comedy |
| 1219 | Goofy Movie, A (1995) | 0.8660 | Cung the loai: Animation, Children, Comedy |
| 63 | Santa Clause, The (1994) | 0.8165 | Cung the loai: Children, Comedy |
| 94 | Home Alone (1990) | 0.8165 | Cung the loai: Children, Comedy |

Run `python scripts/smoke_content_based.py` and `python -m pytest -q`. On this workspace, use `.\.venv\python.exe` in place of `python`.

User 1 top-5: 47: Ed Wood (1994); 65: What's Eating Gilbert Grape (1993); 150: Swingers (1996); 236: Citizen Ruth (1996); 316: As Good As It Gets (1997).

Toy Story similar top-5: 422: Aladdin and the King of Thieves (1996); 95: Aladdin (1992); 1219: Goofy Movie, A (1995); 63: Santa Clause, The (1994); 94: Home Alone (1990).

Genre-only features are coarse and often tie. Content and Popularity scores have different scales. No Content-Based RMSE/MAE is claimed; Day 1 baseline metrics remain unchanged. Audit and examples: [Day 2 evaluation](notes/day2_eval.md).

On Windows, building scikit-surprise 1.1.4 requires Microsoft C++ Build Tools. MSVC and Windows SDK are now installed locally; scikit-surprise 1.1.4 built successfully and all 38 tests pass after integrating the remote feature branch. The Surprise smoke script passes with RMSE 0.9540. If Windows console encoding fails on Vietnamese output, set `$env:PYTHONIOENCODING = "utf-8"` before running the script in PowerShell.
