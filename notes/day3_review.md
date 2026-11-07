# Review tích hợp Day 3

Ngày: 07/11/2026. Base: `d4b3dd2`.

## Phạm vi

Giữ giao diện từ PR #13 của Linh, bổ sung Item-CF, ranking metrics, service, evaluator và smoke từ phần Day 3 local. Stash gốc được giữ lại để phục hồi.

## Kết quả kiểm tra code

- Item-CF chỉ nhận train/movies; center rating quan sát, cosine theo cột item, clip âm, bỏ diagonal, giữ top-50 với tie-break movie_id. Top-50 theo từng hàng có thể làm similarity bất đối xứng; đây là hành vi giữ láng giềng theo item đã chốt.
- Prediction dùng similarity của candidate với phim user đã rating, mẫu số chỉ tính các phim quan sát, giữ weighted_score > 0 rồi clip predicted_rating vào [1,5].
- Seen filtering chỉ dùng train. Fallback nối sau kết quả model, chống trùng, giữ method popularity và phân biệt cold-start/thiếu tín hiệu.
- Ranking metrics loại duplicate trước cắt K, fixed-K precision, binary NDCG, relevant rỗng trả 0. Evaluator macro-average cùng user set, không fit bằng test.
- Service giữ contract Recommendation, không import Streamlit. App không import trực tiếp model; dùng service được cache.
- AppTest bổ sung tương tác Item-CF để khắc phục lỗ hổng bộ test cũ: 41 test pass nhưng chưa phát hiện model chưa đăng ký.
- CI bổ sung evaluator và smoke Item-CF; giữ boundary và các smoke cũ.
- Không thêm comment/docstring vào code mới. Không đưa dữ liệu, model artifact, môi trường Python hoặc secret vào thay đổi.

## Giới hạn review

Đây là kiểm tra tích hợp trong cùng một phiên, không phải approval độc lập của Huy/Phong/Linh. CI và review GitHub phải được xác nhận trên PR trước khi merge; không ghi nhận approval hoặc CI xanh khi chưa có bằng chứng.
