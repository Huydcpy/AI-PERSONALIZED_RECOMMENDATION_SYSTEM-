# MovieLens 100K — Data card

## Nguồn và quyền sử dụng

- Đơn vị cung cấp: GroupLens, University of Minnesota.
- Dataset: https://grouplens.org/datasets/movielens/100k/
- Archive: https://files.grouplens.org/datasets/movielens/ml-100k.zip
- Điều khoản: đọc `data/raw/ml-100k/README` trong archive gốc. Dữ liệu có
  điều kiện sử dụng riêng của GroupLens, không xem là dữ liệu public domain;
  giữ thông tin nguồn và kiểm tra điều khoản trước khi phân phối/sử dụng thương mại.

## Kích thước và ý nghĩa

100.000 đánh giá tường minh, thang nguyên 1–5, từ 943 người dùng cho 1.682 phim.
Độ thưa: `1 - 100000 / (943 * 1682)` ≈ 93,70%.
Mỗi dòng rating là một cặp user–movie; timestamp là Unix seconds.
ID gốc được giữ nguyên để các lớp model/service dùng chung.

## Schema

| File gốc → Parquet | Cột và cách đọc |
|---|---|
| `u.data` → `ratings.parquet` | Tab; `user_id`, `movie_id`, `rating`, `timestamp` (integer) |
| `u.item` → `movies.parquet` | `|`, Latin-1; `movie_id`, `title`, `release_date`, `video_release_date`, `imdb_url` và 19 genre flags |
| `u.user` → `users.parquet` | `|`; `user_id`, `age`, `gender`, `occupation`, `zip_code`; mã bưu điện giữ dạng chuỗi để bảo toàn số 0 đầu |
| `u1.base` → `train.parquet` | Schema giống `u.data`, 80.000 dòng |
| `u1.test` → `test.parquet` | Schema giống `u.data`, 20.000 dòng |

Genre flags: `unknown`, `action`, `adventure`, `animation`, `children`, `comedy`,
`crime`, `documentary`, `drama`, `fantasy`, `film_noir`, `horror`, `musical`,
`mystery`, `romance`, `sci_fi`, `thriller`, `war`, `western`.
Một phim có thể thuộc nhiều thể loại. Ngày phát hành và URL có thể thiếu;
`video_release_date` không phải trường bắt buộc. ID, title, genre và thông tin user
được kiểm tra không null; rating nằm trong [1, 5], metadata ID khớp ratings.

## Split và chống leakage

Dùng nguyên split chuẩn `u1.base` / `u1.test`, không random split lại.
Kiểm tra không trùng cặp `(user_id, movie_id)`, không trùng cặp trong mỗi tập,
và hợp hai tập khớp toàn bộ `u.data` kể cả rating/timestamp.
Split cố định không cần random seed; cấu hình dự án dùng seed 42.
Chỉ fit/tuning và tính lịch sử gợi ý trên train. Test dành cho đánh giá.
EDA toàn bộ dữ liệu chỉ mô tả dataset, không dùng để chọn tham số mô hình.

## Tái tạo từ repository root

Yêu cầu Python 3.11 và dependencies trong `requirements.txt`.
Môi trường kiểm chứng dùng NumPy 1.26.4, pandas 2.3.3, PyArrow 19.0.1;
PyArrow 26 yêu cầu NumPy 2 và không tương thích với ràng buộc NumPy `<2`
của dự án. Khi cần, cài `python -m pip install pyarrow==19.0.1`.

```bash
python -m src.data.download
python -m src.data.preprocess
python -m src.data.splits
python -m pytest tests/test_preprocess.py -q
```

Mở và chạy toàn bộ `notebooks/01_eda.ipynb` để tạo 4 PNG trong
`reports/figures/`: phân bố rating, số rating theo user, long tail theo phim,
top 10 genres theo số rating. Notebook nhận diện repo root khi chạy từ root
hoặc thư mục `notebooks/`. Output notebook được clear để dễ review.
Raw data và Parquet được `.gitignore` loại khỏi commit.

## Hạn chế

Dữ liệu thu thập 1997–1998, không đại diện thị hiếu hiện nay. Chỉ có explicit
feedback, không có click/thời gian xem. Genre thô, thiếu nội dung phim phong phú.
Dữ liệu thưa và có popularity/selection bias; không suy diễn các ô thiếu là
không thích. Không diễn giải metadata nhân khẩu học như đại diện toàn bộ dân số.
