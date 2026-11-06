# Báo cáo Day 2

- Đã triển khai ContentBasedRecommender với 18 thể loại, cosine similarity, profile từ train và Popularity fallback. Không thay đổi contract base.
- Service hỗ trợ hai phương pháp; Similar Movies mặc định Content-Based. Hồ sơ user chuyển sang train để tránh dùng lịch sử test.
- Recommendations chọn được hai phương pháp; Similar Movies và Compare hoạt động; card hiển thị method và reason. Home và README đã cập nhật.
- Smoke test dữ liệu thật pass cho user 1, 196, 405 và Toy Story, Star Wars, Pulp Fiction; user lạ và hai phim không genre fallback đúng. Chi tiết trong day2_eval.md.
- Local: toàn bộ 23 test pass, gồm test Surprise. Ruff pass. AppTest chạy Home, 5 trang và các tương tác chính.
- Đã cài MSVC và Windows SDK bằng Microsoft Build Tools trên ổ D, sau đó build và cài thành công scikit-surprise 1.1.4. Không bỏ qua test Surprise trong CI.
- Nhánh triển khai: feat/content-based. Chưa commit, push, tạo PR hay merge; chưa xác nhận CI từ xa. PR #5 chưa được đóng và chưa gửi yêu cầu review cho thành viên nhóm.
- Hạn chế: genre-only có nhiều điểm bằng nhau; chưa có ranking metrics. Day 3 tiếp tục Item-CF và đánh giá xếp hạng.
