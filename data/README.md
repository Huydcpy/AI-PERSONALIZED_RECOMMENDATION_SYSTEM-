# Dữ liệu

## Nguồn

- **MovieLens 100K** — GroupLens Research.
- Link tải: <https://files.grouplens.org/datasets/movielens/ml-100k.zip>
- License: theo điều khoản sử dụng của GroupLens.

## Cách tải

```bash
python -m src.data.download
```

Script sẽ tải và giải nén vào:

```text
data/raw/ml-100k/
```

## Cấu trúc

| File | Mô tả |
|---|---|
| `u.data` | 100.000 ratings: `user_id`, `movie_id`, `rating`, `timestamp` |
| `u.item` | 1.682 phim: tiêu đề, ngày phát hành, thể loại |
| `u.user` | 943 người dùng: tuổi, giới tính, nghề nghiệp |
| `u1.base` | Train split (80.000 ratings) |
| `u1.test` | Test split (20.000 ratings) |

## Lưu ý

- Không commit dữ liệu thô hoặc dữ liệu đã xử lý vào git.
- Dữ liệu đã xử lý được lưu ở `data/processed/*.parquet`.
