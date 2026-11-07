# Day 3 — Data & Evaluation

Ngày: 07/11/2026. Base: main tại d4b3dd2 (PR #13), tích hợp trên feat/item-cf-ranking.

## Protocol và dữ liệu

Fit chỉ bằng train/movies. Test dùng làm ground truth với rating >= 4.0. K = 5/10/20, full catalog trừ phim đã xem trong train; macro-average cùng tập user, loại duplicate trước cắt top-K, precision luôn chia K. Coverage@10 chia cho toàn bộ catalog.

| Chỉ số | Giá trị |
|---|---:|
| Train ratings | 80.000 |
| Test ratings | 20.000 |
| Catalog | 1.682 |
| Tổng user | 943 |
| User có relevant test item | 456 |
| User bỏ qua | 487 |
| Phim không tương tác train | 32 |

Không đổi split, threshold hoặc hyperparameter dựa trên test. Các lần chạy lại chỉ kiểm tra tái lập với cấu hình cố định. Không tính RMSE/MAE Item-CF; giữ baseline Day 1. Chưa đánh giá SVD/Hybrid.

## Kết quả thực tế

| Model | Precision@5 | Precision@10 | Recall@10 | NDCG@10 | Coverage@10 |
|---|---:|---:|---:|---:|---:|
| Popularity | 0.163158 | 0.164474 | 0.070910 | 0.174714 | 0.023187 |
| Content-Based | 0.058772 | 0.047368 | 0.022264 | 0.055068 | 0.237812 |
| Item-CF | 0.028947 | 0.029167 | 0.018530 | 0.031481 | 0.508323 |

Popularity tốt nhất theo NDCG@10. Item-CF có precision thấp hơn cả hai model còn lại nhưng coverage cao nhất. Dữ liệu thưa, top-50 láng giềng và nhiều dự đoán clip về 5 gây tie; không tune trên test để cải thiện kết quả. 487 user bị skip là đặc điểm split u1.

JSON đầy đủ: reports/metrics/ranking.json. Ví dụ top-5: notes/day3_report.md.

## Kiểm chứng

Smoke kiểm tra user 1/196/405, phim 1/50/56, method/reason/score, duplicate và seen filtering. User 999999 fallback cold-start. Dữ liệu tạm bỏ rating user 196 và tương tác phim 1 để kiểm tra metadata-only user và zero-interaction movie; không sửa dữ liệu gốc. Movie ID lạ raise ValueError.

Evaluator có kiểm tra overlap train/test, catalog, metric NaN/Inf/ngoài [0,1], phim đã xem, macro-average, coverage và không ghi đè report khi thất bại. AppTest kiểm tra cả trang cũ và Item-CF cho 3 user/3 phim, so sánh 3 phương pháp và bảng ranking.

Ví dụ recommended=[1,2,3,4,5], relevant={2,4,6} trong task có NDCG@5 đúng là 0.4981892575 theo binary DCG/IDCG, không phải 0.6509. Unit test sử dụng công thức tính tay đúng.
