# Phong — số liệu dự phòng và ví dụ Day 5

Xác minh ngày 10/11/2026 trên base `20178b4`. Bảng được tạo trực tiếp từ JSON và kết quả service; không tune trên test.

## Chênh lệch rating

| Metric | Popularity | SVD | Giảm tuyệt đối | Giảm so với baseline |
|---|---:|---:|---:|---:|
| RMSE | 1.066985 | 0.956120 | 0.110865 | 10.3905% |
| MAE | 0.863097 | 0.752447 | 0.110650 | 12.8201% |

## Thứ hạng từng cột

Hạng 1 là giá trị cao nhất; dùng số đầy đủ trong JSON để xếp hạng.

| Model | Precision@5 | Precision@10 | Recall@10 | NDCG@10 | Coverage@10 |
|---|---:|---:|---:|---:|---:|
| Popularity | 1 | 1 | 1 | 1 | 5 |
| Content-Based | 4 | 4 | 4 | 4 | 3 |
| Item-CF | 5 | 5 | 5 | 5 | 1 |
| SVD | 2 | 2 | 2 | 2 | 4 |
| Hybrid | 3 | 3 | 3 | 3 | 2 |

## Top-5 user 196

Score khác thang đo giữa các model; chỉ so thứ tự trong cùng phương pháp. Tất cả kết quả dưới đây đã loại phim có trong train của user 196.

| Model | Hạng | Movie ID | Title | Score | Method thực tế | Reason |
|---|---:|---:|---|---:|---|---|
| Popularity | 1 | 318 | Schindler's List (1993) | 4.322012 | popularity | Phổ biến toàn hệ thống |
| Popularity | 2 | 50 | Star Wars (1977) | 4.281681 | popularity | Phổ biến toàn hệ thống |
| Popularity | 3 | 483 | Casablanca (1942) | 4.254765 | popularity | Phổ biến toàn hệ thống |
| Popularity | 4 | 64 | Shawshank Redemption, The (1994) | 4.254277 | popularity | Phổ biến toàn hệ thống |
| Popularity | 5 | 12 | Usual Suspects, The (1995) | 4.231485 | popularity | Phổ biến toàn hệ thống |
| Content-Based | 1 | 34 | Doom Generation, The (1995) | 0.913554 | content_based | Khớp thể loại: Comedy, Drama |
| Content-Based | 2 | 45 | Eat Drink Man Woman (1994) | 0.913554 | content_based | Khớp thể loại: Comedy, Drama |
| Content-Based | 3 | 47 | Ed Wood (1994) | 0.913554 | content_based | Khớp thể loại: Comedy, Drama |
| Content-Based | 4 | 65 | What's Eating Gilbert Grape (1993) | 0.913554 | content_based | Khớp thể loại: Comedy, Drama |
| Content-Based | 5 | 93 | Welcome to the Dollhouse (1995) | 0.913554 | content_based | Khớp thể loại: Comedy, Drama |
| Item-CF | 1 | 127 | Godfather, The (1972) | 5.000000 | item_cf | Dựa trên phim tương tự bạn đã rating |
| Item-CF | 2 | 154 | Monty Python's Life of Brian (1979) | 5.000000 | item_cf | Dựa trên phim tương tự bạn đã rating |
| Item-CF | 3 | 182 | GoodFellas (1990) | 5.000000 | item_cf | Dựa trên phim tương tự bạn đã rating |
| Item-CF | 4 | 293 | Donnie Brasco (1997) | 5.000000 | item_cf | Dựa trên phim tương tự bạn đã rating |
| Item-CF | 5 | 311 | Wings of the Dove, The (1997) | 5.000000 | item_cf | Dựa trên phim tương tự bạn đã rating |
| SVD | 1 | 483 | Casablanca (1942) | 4.287311 | svd | Dự đoán theo sở thích cá nhân (SVD) |
| SVD | 2 | 408 | Close Shave, A (1995) | 4.278069 | svd | Dự đoán theo sở thích cá nhân (SVD) |
| SVD | 3 | 169 | Wrong Trousers, The (1993) | 4.265532 | svd | Dự đoán theo sở thích cá nhân (SVD) |
| SVD | 4 | 318 | Schindler's List (1993) | 4.255841 | svd | Dự đoán theo sở thích cá nhân (SVD) |
| SVD | 5 | 923 | Raise the Red Lantern (1991) | 4.253564 | svd | Dự đoán theo sở thích cá nhân (SVD) |
| Hybrid | 1 | 127 | Godfather, The (1972) | 0.602944 | hybrid | Kết hợp SVD + Item-CF + Content-Based |
| Hybrid | 2 | 481 | Apartment, The (1960) | 0.500000 | hybrid | Kết hợp SVD + Item-CF + Content-Based |
| Hybrid | 3 | 483 | Casablanca (1942) | 0.500000 | hybrid | Kết hợp SVD + Item-CF + Content-Based |
| Hybrid | 4 | 408 | Close Shave, A (1995) | 0.487263 | hybrid | Kết hợp SVD + Item-CF + Content-Based |
| Hybrid | 5 | 169 | Wrong Trousers, The (1993) | 0.469986 | hybrid | Kết hợp SVD + Item-CF + Content-Based |

## Similar Movies SVD/Hybrid

| Method | Phim gốc | Top-5 movie ID theo thứ tự |
|---|---|---|
| SVD | 1: Toy Story (1995) | 45, 378, 979, 174, 1459 |
| SVD | 50: Star Wars (1977) | 181, 172, 174, 1594, 228 |
| SVD | 56: Pulp Fiction (1994) | 93, 127, 475, 182, 180 |
| Hybrid | 1: Toy Story (1995) | 174, 50, 28, 45, 95 |
| Hybrid | 50: Star Wars (1977) | 181, 172, 174, 173, 271 |
| Hybrid | 56: Pulp Fiction (1994) | 182, 127, 180, 187, 475 |

## Fallback user lạ: reason thực tế

| Method yêu cầu | Method trả về | Reason |
|---|---|---|
| popularity | popularity | Phổ biến toàn hệ thống |
| content_based | popularity | Fallback phổ biến (cold-start) |
| item_cf | popularity | Fallback phổ biến (cold-start) |
| svd | popularity | Fallback phổ biến (cold-start) |
| hybrid | popularity | Fallback phổ biến (cold-start) |

Popularity là baseline gốc nên reason của nó không bắt buộc mang nhãn fallback. Case metadata-only và zero-interaction được xác minh bằng smoke script trên dữ liệu train tạm đã loại user 196 và movie 1; không sửa dữ liệu dự án.

Nguồn: [baseline.json](../reports/metrics/baseline.json), [svd.json](../reports/metrics/svd.json), [ranking.json](../reports/metrics/ranking.json).
