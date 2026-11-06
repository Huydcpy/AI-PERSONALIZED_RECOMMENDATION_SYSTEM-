# Báo cáo Day 1

- Đã tích hợp pipeline MovieLens 100K, Popularity, service và giao diện Streamlit trên main tại commit 2d9f0fc.
- Dữ liệu local: 100.000 ratings, 943 users, 1.682 movies; train 80.000 và test 20.000.
- Baseline đã lưu: RMSE 1.066985, MAE 0.863097.
- Có data card, evaluation protocol, 4 biểu đồ EDA và workflow CI.
- Kiểm tra lại local trong Day 2 phát hiện môi trường chưa có Surprise; không xác nhận lại smoke Surprise hay trạng thái CI từ xa.
