# Review Day 4 — Phong

Ngày 09/11/2026, base ea4a550. Review cục bộ phần model của Huy và app của Linh để hoàn thành nhiệm vụ Data & Evaluation.

- SVD constructor chỉ nhận train/movies, trainset tạo từ train, factors/bias căn theo movie_id; seed cố định. Predict dùng Surprise; vector hóa được kiểm tra trên dữ liệu thật, sai số tối đa 8,88e-16. Unit tests xác nhận fallback, loại seen, score, tie-break.
- Hybrid min-max từng component, max=min gán 1, pool cố định theo K, chỉ lấy native, missing component đóng góp 0; fallback nối sau blend. Fake-model tests kiểm tra blend tính tay và tie-break.
- Phát hiện Hybrid cold-start chuyển thẳng kết quả Popularity nên reason là “Phổ biến toàn hệ thống”. Sửa duy nhất đường trả fallback để ghi “Fallback phổ biến (cold-start)”; assertion mới và smoke metadata-only/unknown user xác nhận.
- Service khởi tạo model bằng train/movies, không đưa test vào fit. Model/service không import Streamlit. App không import src.models; service có cache_resource, metrics có cache_data.
- AppTest bổ sung xác nhận method/reason thực tế cho SVD/Hybrid trên 3 user và 3 phim, Compare 5 tab/50 cards, Evaluation 2 dòng rating và 5 dòng ranking. Các trang load không exception trong bộ test hiện có.
- Rating evaluator tái sử dụng validation train/test/catalog của ranking evaluator, kiểm tra prediction hữu hạn/[1,5], ghi file tạm. Tests dùng fake prediction xác minh công thức metric, train-only fit và giữ báo cáo cũ khi prediction sai.
- Validation bổ sung từ chối input rỗng ở cả train/test/movies; unit tests xác nhận.
- Ranking giữ quy ước loại duplicate lần đầu, relevance 4, K 5/10/20, macro-average và toàn catalog denominator; 5 model/10 metrics mỗi model. Không đổi thuật toán hoặc cấu hình sau khi xem test.

Đây là review tích hợp trong cùng phiên làm việc, không phải approval độc lập. Chưa xác nhận GitHub CI hay thực hiện merge/push. CI hiện chưa gọi hai script mới run_svd_eval.py và smoke_svd_hybrid.py; đây là đầu việc CI của Linh, cần bổ sung trước merge. Không sửa README/CI thuộc phần Linh.

## Kết quả xác minh cuối

- Toàn bộ test: 106 passed trong 19,97 giây.
- Ruff: All checks passed; git diff --check không có lỗi whitespace.
- Smoke SVD/Hybrid pass; AppTest Day 4 pass.
- Chạy lại cả rating và ranking evaluator: SHA-256 của svd.json và ranking.json giống lần đầu.
- baseline.json không có diff; không thêm comment/docstring vào code mới.

## Cập nhật sau merge (10/11/2026)

PR #15, #16 và #17 đã merge vào `main` tại `184ecdd`; CI `main` xanh tại commit này. Trong đợt hoàn thiện Day 4, CI đã bổ sung `run_svd_eval.py` và `smoke_svd_hybrid.py`; README và `notes/day4_report.md` đã được cập nhật. Cần xác nhận CI trên commit mới sau khi push. Đây vẫn là review tích hợp trong cùng phiên làm việc, không phải approval độc lập.
