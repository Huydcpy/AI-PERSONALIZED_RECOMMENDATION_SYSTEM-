# TASK DAY 5 — 11/11/2026

> Trạng thái tại thời điểm lập kế hoạch: `main`/`origin/main` tại `184ecdd`, 106 test pass, 5 phương pháp đã tích hợp. Các thay đổi hoàn thiện Day 4 (README, `notes/day4_report.md`, CI, notes) đang ở working tree và chưa push; CI mới chưa chạy hai bước `run_svd_eval.py` và `smoke_svd_hybrid.py`. Cần chốt các thay đổi này trước khi bắt đầu Day 5.
>
> **Trạng thái cuối (12/11/2026):** dự án đã hoàn thành; PR #18, #19, #20, #21 đã merge, CI xanh và release đầy đủ là `v1.0.1`. File này giữ checklist kế hoạch gốc để truy vết; trạng thái thực tế, ngoại lệ và bằng chứng nằm trong [day5_closeout.md](day5_closeout.md).

**Dự án:** AI Personalized Recommendation System (MovieLens 100K)

**Mục tiêu Day 5:** chốt sản phẩm, đánh giá cuối, viết báo cáo và chuẩn bị demo:
**5 phương pháp → số liệu cuối → biểu đồ/phân tích → báo cáo → slide & demo 5–7 phút**.

**Demo cuối ngày:**
- Chọn 3 user khác nhau, xem top-10 SVD và top-10 Hybrid.
- Chọn 3 phim khác nhau, xem Similar Movies theo SVD và Hybrid.
- So sánh 5 phương pháp trên cùng một user: Popularity, Content-Based, Item-CF, SVD, Hybrid.
- Trang Evaluation hiển thị RMSE/MAE của Popularity và SVD, cùng ranking metrics 5 phương pháp.
- Kiểm tra fallback: user lạ, user không có rating trong train, phim không có tương tác.
- Không có phim đã xem trong top-K khi `exclude_seen=True`.
- Trình bày trung thực: Popularity dẫn đầu NDCG@10, SVD cải thiện rating, Item-CF dẫn đầu coverage, Hybrid không tốt nhất mọi tiêu chí.

---

## 0. PHÂN CÔNG TỔNG QUAN

| Thành viên | Vai trò | Phụ trách chính | Deliverable | Branch |
|---|---|---|---|---|
| **Huy (Trưởng nhóm)** | Integration & final report | Chốt Day 4, kiểm chứng cuối, báo cáo tổng hợp, review, merge, release | `notes/day5_report.md`, `notes/day5_review.md`, tag/release | `feat/day5-final` |
| **Phong** | Data & Evaluation | Số liệu cuối, biểu đồ, phân tích lỗi, `notes/day5_eval.md` | `scripts/make_day5_figures.py`, `reports/figures/day5_*.png`, `notes/day5_eval.md` | `feat/day5-final` |
| **Linh** | Product & Demo | README cuối, screenshot, demo script, slide, AppTest, PR/CI | `README.md`, `reports/figures/day5_*.png`, `notes/demo_script.md`, `notes/day5_slides.md` | `feat/day5-final` |

**Nguyên tắc phối hợp:**
- Tất cả làm trên **một branch chung** `feat/day5-final`, tạo từ `origin/main` sau khi Day 4 finalization đã merge.
- **Code freeze lúc 11:00**: sau mốc này chỉ sửa bug chặn demo, lỗi số liệu hoặc tài liệu; mọi thay đổi code phải được Huy duyệt.
- Không thêm model, metric, dependency hoặc tuning mới. Day 5 là đánh giá, báo cáo và demo.
- Không tune hyperparameter, trọng số Hybrid, threshold hoặc K trên test.
- Không ai sửa file của người khác khi chưa trao đổi.
- Review chéo qua PR trước khi merge.
- Không thêm comment/docstring mới vào code theo `AGENTS.md`.
- Số liệu trong README/report/slide phải lấy từ JSON, không sửa tay.
- Screenshot và hình phải lấy từ app/JSON thật, không dựng lại bằng tay.

### Quyết định kỹ thuật mặc định

- Giữ nguyên 5 phương pháp: `popularity`, `content_based`, `item_cf`, `svd`, `hybrid`.
- Giữ nguyên hyperparameter SVD: `n_factors=100`, `n_epochs=20`, `lr_all=0.005`, `reg_all=0.02`, `random_state=42`.
- Giữ nguyên trọng số Hybrid:
  - Recommend: `svd=0.5`, `item_cf=0.3`, `content_based=0.2`.
  - Similar: `item_cf=0.4`, `svd=0.3`, `content_based=0.3`.
- Giữ nguyên protocol ranking: relevance `rating >= 4.0`, K `5/10/20`, K chính `10`, macro-average trên user có relevant item, coverage trên toàn catalog.
- Không đổi `reports/metrics/baseline.json`, `svd.json`, `ranking.json` trừ khi chạy lại evaluator cho kết quả giống hệt.
- Không commit data, model artifact, cache hoặc secret.
- Báo cáo cuối dùng tiếng Việt; thuật ngữ kỹ thuật có thể giữ tiếng Anh.
- Hình báo cáo/slide dùng PNG trong `reports/figures/`; ưu tiên font đọc được, kích thước ổn định.

### Trạng thái đầu vào

- `main` tại `184ecdd`; PR #15, #16, #17 đã merge.
- 106 test pass; `ruff check .` pass; smoke SVD/Hybrid pass.
- `reports/metrics/svd.json`: RMSE `0.956119767639409`, MAE `0.7524468775134182`.
- `reports/metrics/ranking.json`: 5 model, 10 metric/model; 456 user được đánh giá, 487 user bị bỏ; catalog 1.682 phim.
- NDCG@10: Popularity `0.174714`, SVD `0.137267`, Hybrid `0.109632`, Content-Based `0.055068`, Item-CF `0.031481`.
- Coverage@10: Item-CF `0.508323`, Hybrid `0.315101`, Content-Based `0.237812`, SVD `0.105826`, Popularity `0.023187`.
- Ranking evaluation chạy khoảng 18,35 giây; SVD rating evaluation khoảng 1,70 giây; warm service khoảng 0,08 giây cho 12 lời gọi.
- App đã có 5 trang; Streamlit khởi động trả HTTP 200; AppTest phủ 5 phương pháp.
- Chưa có screenshot Day 4/Day 5; PR #15/#16/#17 có body trống, chưa có mô tả What/Why/How tested/Screenshot.
- CI `main` xanh tại `184ecdd` cho workflow cũ; workflow hiện tại đã thêm Day 4 nhưng chưa chạy trên GitHub.

### Việc cần dọn trước khi bắt đầu

- [ ] Chốt và commit/push các thay đổi hoàn thiện Day 4 đang ở working tree.
- [ ] Tạo PR cho Day 4 finalization; xác nhận CI chạy `run_svd_eval.py` và `smoke_svd_hybrid.py` xanh.
- [ ] Merge Day 4 finalization vào `main`; ghi lại commit SHA mới.
- [ ] Sync local `main` lên `origin/main`; xác nhận `git status` sạch.
- [ ] Tạo branch `feat/day5-final` từ `origin/main`.
- [ ] Đọc lại `notes/day4_report.md`, `notes/day4_eval.md`, `notes/day4_review.md`, `docs/evaluation_protocol.md`.
- [ ] Chạy baseline kiểm tra: `pytest -q`, `ruff check .`, `python scripts/run_ranking_eval.py`.
- [ ] Kiểm tra dung lượng `data/` và không có file lớn sắp bị commit.

**Lệnh gợi ý:**

```bash
git fetch origin
git switch main
git pull --ff-only
git switch -c feat/day5-final
git status
```

---

## 1. MỐC THỜI GIAN & BÀN GIAO

| Giờ | Việc chung | Huy | Phong | Linh |
|---|---|---|---|---|
| 09:00–09:30 | Chốt Day 4 finalization, sync main, tạo branch | Chủ trì, commit/PR | Xác nhận số liệu | Xác nhận README/CI |
| **09:30** | **Day 4 finalization merge + CI xanh** | Báo tiến độ | Báo tiến độ | Báo tiến độ |
| 09:30–10:30 | Kiểm chứng cuối, chốt số liệu | Chạy full verification | Tổng hợp metrics, bắt đầu figures | Rà README, chuẩn bị screenshot |
| **10:30** | **Số liệu cuối + figure đầu tiên** | Chốt metric hash | Báo tiến độ | Báo tiến độ |
| 10:30–11:00 | Chốt nội dung báo cáo, demo flow | Khung report | Phân tích lỗi | Demo script/slide outline |
| **11:00** | **Code freeze** | Chủ trì | Dừng sửa code | Dừng sửa code |
| 11:00–12:00 | Viết báo cáo/eval, hoàn thiện figure | Viết report | `day5_eval.md` | README + screenshot |
| 12:00 | Sync nhanh 5 phút | Báo tiến độ | Báo tiến độ | Báo tiến độ |
| 13:30–15:00 | Review chéo, hoàn thiện slide/demo | Review report | Review số liệu/hình | Slide, demo script, AppTest |
| 15:00–15:45 | Rehearse demo lần 1 | Điều phối | Trả lời phần metrics | Trình bày phần app |
| **15:45** | **Demo chạy end-to-end 2 lần** | Xác nhận | Xác nhận | Xác nhận |
| 15:45–16:30 | PR, CI, review, merge | Review/merge | Review | PR/CI/screenshot |
| 16:30–17:00 | Chốt Day 5 | Tag/release, báo cáo | Chốt eval | Chốt README/demo |

---

## 2. HƯỚNG DẪN CHO HUY (TRƯỞNG NHÓM)

### 2.1 Mục tiêu cá nhân

Chốt được Day 4 finalization, kiểm chứng toàn bộ hệ thống, hoàn thiện báo cáo cuối, review/merge PR Day 5 và tạo release/tag nếu đủ điều kiện.

### 2.2 Phụ thuộc

- Các thay đổi Day 4 finalization đang ở working tree; cần xử lý trước 09:30.
- CI mới cần chạy thực tế để xác nhận hai bước Day 4.
- Phong cần số liệu cuối trước 10:30 để chốt report.
- Linh cần screenshot/demo script trước 15:00 để rehearse.
- Không phụ thuộc vào thay đổi model mới.

### 2.3 Checklist công việc chi tiết

#### Task 1 — Chốt Day 4 finalization & tạo branch

- [ ] Kiểm tra `git status`; xác nhận chỉ có thay đổi docs/CI của Day 4, không có data/model/secret.
- [ ] Tạo branch `docs/day4-finalize` từ `origin/main` nếu chưa commit.
- [ ] Commit các thay đổi Day 4 với message rõ ràng, ví dụ `docs(day4): fill results and finalize CI`.
- [ ] Push branch và tạo PR vào `main`.
- [ ] Xác nhận CI chạy đủ:
  - `python scripts/run_svd_eval.py`
  - `python scripts/smoke_svd_hybrid.py`
- [ ] Ghi lại run URL/commit SHA và trạng thái CI.
- [ ] Merge PR khi CI xanh; sync `main`.
- [ ] Tạo branch `feat/day5-final` từ `origin/main`.
- [ ] Ghi chú mục screenshot/PR description còn mở của Day 4 sẽ được xử lý trong Day 5.

#### Task 2 — Kiểm chứng cuối toàn hệ thống

- [ ] Chạy `git fetch origin` và xác nhận HEAD/base commit.
- [ ] Chạy `python -m pytest -q`; kỳ vọng 106 test pass.
- [ ] Chạy `python -m ruff check .`; kỳ vọng pass.
- [ ] Chạy `python scripts/run_svd_eval.py`; ghi thời gian và kết quả.
- [ ] Chạy `python scripts/run_ranking_eval.py`; ghi thời gian và kết quả.
- [ ] Chạy `python scripts/smoke_svd_hybrid.py`, `smoke_item_cf.py`, `smoke_content_based.py`, `smoke_surprise.py`.
- [ ] Ghi SHA-256 của `reports/metrics/svd.json` và `reports/metrics/ranking.json` trước/sau khi chạy lại; xác nhận giống hệt.
- [ ] Xác nhận `reports/metrics/baseline.json` không thay đổi.
- [ ] Kiểm tra README/report có số liệu khớp JSON.
- [ ] Khởi động Streamlit, xác nhận HTTP 200; đo warm service cho 3 user/3 phim.
- [ ] Kiểm tra AppTest không exception.
- [ ] Kiểm tra `git status`: không có data/model/cache/secret.
- [ ] Ghi kết quả vào `notes/day5_report.md` mục “Kiểm chứng”.

#### Task 3 — Báo cáo cuối

- [ ] Tạo `notes/day5_report.md` theo cấu trúc trong Phụ lục 9.1.
- [ ] Viết phần tóm tắt và bài toán bằng ngôn ngữ rõ ràng, không phóng đại.
- [ ] Mô tả dữ liệu, split 80.000/20.000, catalog 1.682 phim, 943 user.
- [ ] Mô tả kiến trúc service/app và luồng request.
- [ ] Mô tả 5 phương pháp, công thức/ý tưởng chính, fallback.
- [ ] Ghi protocol đánh giá và nguyên tắc không tune trên test.
- [ ] Chèn bảng rating metrics và bảng ranking metrics từ JSON.
- [ ] Chèn 4 biểu đồ Day 5 từ `reports/figures/`.
- [ ] Phân tích trade-off rating vs ranking, coverage vs NDCG, popularity bias.
- [ ] Ghi rõ Hybrid không vượt Popularity/SVD về NDCG@10; không che kết quả.
- [ ] Ghi hạn chế: explicit feedback, một split/seed, chưa có kiểm định thống kê, score khác thang đo.
- [ ] Ghi phân công và bài học kinh nghiệm.
- [ ] Chèn link tới `notes/day5_eval.md`, `notes/demo_script.md`, `README.md`.
- [ ] Nhờ Phong/Linh đọc lại phần liên quan trước 15:00.

#### Task 4 — Review, merge và release

- [ ] Review PR của Phong: figures lấy từ JSON, không sửa số liệu, không tune.
- [ ] Review PR của Linh: README khớp số liệu, screenshot thật, demo script rõ.
- [ ] Kiểm tra PR description có What / Why / How tested / Screenshot.
- [ ] Xác nhận CI xanh trên PR Day 5.
- [ ] Merge PR vào `main`; sync local.
- [ ] Tạo tag `v1.0.0` hoặc `day5-final` sau merge nếu không còn thay đổi.
- [ ] Tạo release notes ngắn gọn: phạm vi, kết quả chính, cách chạy, hạn chế.
- [ ] Ghi lại commit SHA cuối và trạng thái CI.

#### Task 5 — Điều phối demo & Q&A

- [ ] Chốt demo flow 5–7 phút và phân vai nói.
- [ ] Rehearse lần 1 lúc 15:00; ghi các chỗ chậm/lỗi.
- [ ] Rehearse lần 2 lúc 15:45; xác nhận không crash.
- [ ] Chuẩn bị phương án dự phòng: screenshot/video, app local, data đã có.
- [ ] Chuẩn bị Q&A:
  - Vì sao Popularity dẫn đầu NDCG@10?
  - Vì sao SVD tốt rating nhưng không tốt ranking?
  - Vì sao Hybrid không vượt component?
  - Chống leakage bằng cách nào?
  - Cold-start/fallback hoạt động ra sao?
  - Hạn chế và hướng phát triển?
- [ ] Xác nhận demo chạy được với user 1/196/405 và phim 1/50/56.
- [ ] Xác nhận fallback user lạ và `exclude_seen=True` hoạt động.

### 2.4 Lệnh kiểm tra của Huy

```bash
pytest -q
ruff check .
python scripts/run_svd_eval.py
python scripts/run_ranking_eval.py
python scripts/smoke_svd_hybrid.py
python scripts/smoke_item_cf.py
python scripts/smoke_content_based.py
python scripts/smoke_surprise.py
sha256sum reports/metrics/svd.json reports/metrics/ranking.json
streamlit run app/Home.py
```

### 2.5 Tiêu chí hoàn thành

- [ ] Day 4 finalization đã merge; CI xanh với hai bước mới.
- [ ] 106 test pass, lint pass, toàn bộ smoke/evaluator pass.
- [ ] Metric JSON tái lập đúng SHA-256; baseline không đổi.
- [ ] `notes/day5_report.md` hoàn chỉnh, số liệu khớp JSON.
- [ ] Hình, screenshot, demo script và slide outline có trong repo.
- [ ] PR Day 5 được review, CI xanh và merge.
- [ ] Demo chạy end-to-end 2 lần không lỗi.
- [ ] Tag/release được tạo nếu đủ điều kiện.

### 2.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Day 4 finalization chưa commit gây conflict | Chốt bằng branch/PR riêng trước 09:30 |
| CI mới chưa chạy thực tế | Không merge Day 5 trước khi CI xanh |
| Số liệu report lệch JSON | Sinh bảng bằng script/đọc JSON, review chéo |
| Report quá dài, thiếu trọng tâm | Giữ cấu trúc 9.1, mỗi mục 1–3 đoạn |
| Demo chậm do cold start | Warm cache trước khi demo; có screenshot dự phòng |
| Scope creep sang model mới | Code freeze 11:00; chỉ bugfix chặn demo |
| Merge conflict docs | Chia file rõ ràng; rebase sớm |

### 2.7 Báo cáo cuối ngày

- Đã xong: PR #18, #19, #20, #21 merge; báo cáo/eval/review/closeout; release `v1.0.0` và `v1.0.1`.
- Kết quả kiểm chứng: 106 test pass, 42 test chuyên biệt pass, ruff pass, smoke pass, metric hash không đổi.
- Số liệu chính: SVD RMSE `0.956120`, MAE `0.752447`; Popularity NDCG@10 `0.174714`; Item-CF Coverage@10 `0.508323`.
- Demo: dry-run kỹ thuật 2 lần, 0,1285 giây và 0,1136 giây; không có rehearsal thuyết trình trực tiếp.
- Blocker/đề xuất: không có blocker; release đầy đủ là `v1.0.1`.

---

## 3. HƯỚNG DẪN CHO PHONG

### 3.1 Mục tiêu cá nhân

Chốt số liệu đánh giá cuối, tạo biểu đồ và phân tích lỗi, hoàn thiện `notes/day5_eval.md` để Huy đưa vào báo cáo và demo.

### 3.2 Phụ thuộc

- Metrics JSON đã có; không cần chạy lại model nếu số liệu tái lập.
- Huy chốt protocol/số liệu trước 10:30.
- Linh cần figure trước 13:30 để đưa vào slide/README.
- Không phụ thuộc code mới.

### 3.3 Checklist công việc chi tiết

#### Task 1 — Tổng hợp số liệu cuối

- [x] Đọc `reports/metrics/baseline.json`, `svd.json`, `ranking.json`.
- [x] Kiểm tra schema và số model/metric.
- [x] Lập bảng rating:
  - Popularity RMSE/MAE.
  - SVD RMSE/MAE.
  - Chênh lệch tuyệt đối và phần trăm.
- [x] Lập bảng ranking 5 model:
  - Precision@5, Precision@10, Recall@10, NDCG@10, Coverage@10.
  - Xếp hạng từng cột.
- [x] Ghi rõ Popularity tốt nhất NDCG@10; Item-CF tốt nhất Coverage@10.
- [x] Ghi rõ SVD cải thiện rating nhưng không vượt Popularity ranking.
- [x] Ghi rõ Hybrid không vượt SVD/Popularity về NDCG@10; coverage cao hơn SVD.
- [x] Kiểm tra 456 user đánh giá, 487 user bỏ, catalog 1.682.
- [x] Không sửa tay số liệu; nếu cần, đọc trực tiếp từ JSON.

#### Task 2 — Biểu đồ cuối

- [x] Viết `scripts/make_day5_figures.py` hoặc tương đương.
- [x] Script đọc JSON, validate key/model, không đọc test/raw data.
- [x] Tạo tối thiểu 4 hình:
  - `reports/figures/day5_rating_rmse_mae.png`
  - `reports/figures/day5_ranking_ndcg10.png`
  - `reports/figures/day5_ranking_coverage10.png`
  - `reports/figures/day5_ndcg_vs_coverage.png`
- [x] Mỗi hình có title, axis label, value label, font đọc được.
- [x] Không dùng màu gây nhầm lẫn; thống nhất thứ tự model.
- [x] Chạy script 2 lần; xác nhận file tạo được, không lỗi.
- [x] Kiểm tra dung lượng PNG hợp lý (< 1 MB/hình nếu có thể).
- [x] Chèn link hình vào `notes/day5_eval.md` và báo Huy/Linh.
- [x] Không commit hình nếu hình quá lớn hoặc chứa dữ liệu nhạy cảm; MovieLens là dữ liệu công khai.

#### Task 3 — Phân tích lỗi và ví dụ định tính

- [x] Chạy smoke SVD/Hybrid để lấy ví dụ user 196 và phim 1/50/56.
- [x] So sánh top-5 giữa 5 phương pháp cho cùng user 196.
- [x] Ghi nhận khác biệt:
  - Popularity thiên về phim phổ biến.
  - Content-Based tạo nhiều tie theo genre.
  - Item-CF thưa, precision thấp.
  - SVD đa dạng latent nhưng có thể lệch genre.
  - Hybrid dung hòa nhưng bị dilution.
- [x] Kiểm tra fallback:
  - User 999999.
  - User metadata-only.
  - Phim zero-interaction.
- [x] Ghi rõ fallback dùng Popularity và reason tương ứng.
- [x] Ghi hạn chế: một split/seed, chưa kiểm định thống kê.
- [ ] (Tuỳ chọn) Nếu còn thời gian, tính bootstrap 95% CI cho NDCG@10 trên 456 user; output `reports/metrics/uncertainty.json`; ghi rõ là phân tích thăm dò, không đổi metric chính.
- [x] Không tune threshold/K/trọng số từ kết quả.

#### Task 4 — Viết `notes/day5_eval.md`

- [x] Tạo file với các mục:
  - Protocol tóm tắt.
  - Bảng rating.
  - Bảng ranking.
  - Biểu đồ.
  - Phân tích trade-off.
  - Fallback/error cases.
  - Hạn chế.
  - Kết luận.
- [x] Mọi số liệu khớp JSON.
- [x] Link tới `reports/metrics/*.json` và `reports/figures/day5_*.png`.
- [x] Ghi rõ “không tune trên test”.
- [x] Ghi rõ “một split/seed, chưa kiểm định thống kê” nếu chưa làm bootstrap.
- [x] Review lại với Huy trước 15:00 (thực tế review post-merge PR #21).

#### Task 5 — Hỗ trợ demo/Q&A

- [x] Chuẩn bị 3–5 câu trả lời về metrics.
- [x] Giải thích vì sao Popularity có NDCG@10 cao.
- [x] Giải thích vì sao SVD RMSE tốt nhưng ranking không cao.
- [x] Giải thích coverage và popularity bias.
- [x] Chuẩn bị số liệu dự phòng nếu demo app lỗi.


### 3.4 Lệnh kiểm tra của Phong

```bash
python - <<'PY'
import json
for path in ("reports/metrics/baseline.json", "reports/metrics/svd.json", "reports/metrics/ranking.json"):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    print(path, sorted(d.keys()))
PY
python scripts/make_day5_figures.py
python scripts/smoke_svd_hybrid.py
pytest tests/test_svd.py tests/test_hybrid.py tests/test_ranking_eval_script.py -q
```

### 3.5 Tiêu chí hoàn thành

- [x] Bảng số liệu cuối đầy đủ, khớp JSON.
- [x] 4 hình PNG tồn tại và được dùng trong eval/report/slide.
- [x] `notes/day5_eval.md` hoàn chỉnh, có phân tích và hạn chế.
- [x] Fallback/error cases được ghi nhận.
- [x] Không có thay đổi model/hyperparameter/trọng số.

### 3.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Số liệu JSON và report lệch | Sinh bảng từ JSON, không copy tay |
| Hình lỗi font tiếng Việt | Dùng label tiếng Anh hoặc font hỗ trợ; kiểm tra ảnh |
| Bootstrap CI tốn thời gian | Để optional, không chặn demo |
| Phân tích quá dài | Tập trung 4–5 phát hiện chính |
| Hình quá lớn | Giảm DPI/figsize, vẫn đọc được |

### 3.7 Báo cáo cuối ngày

- Đã xong ngày 10/11/2026: tổng hợp và đối chiếu metrics, tạo lại 4 biểu đồ hai lần, phân tích Top-5 đủ 5 phương pháp, kiểm tra fallback, bổ sung eval và 5 câu Q&A.
- Số liệu/hình: [day5_eval.md](day5_eval.md), [day5_phong_details.md](day5_phong_details.md); 4 PNG được liên kết trong eval, đều dưới 1 MB. 42 test chuyên biệt đạt, smoke SVD/Hybrid và Ruff đạt.
- Phát hiện chính: Popularity dẫn đầu NDCG@10; SVD giảm RMSE 10,3905%; Item-CF có coverage cao nhất; Hybrid tăng coverage so với SVD nhưng giảm NDCG@10. Không tune trên test.
- Đã đóng: Huy review post-merge, xác nhận bàn giao với Huy/Linh trong [day5_closeout.md](day5_closeout.md). Bootstrap là tùy chọn, chưa thực hiện; chưa kiểm định thống kê. Không có blocker kỹ thuật.

---

## 4. HƯỚNG DẪN CHO LINH

### 4.1 Mục tiêu cá nhân

Hoàn thiện README, screenshot, demo script và slide outline; xác nhận app/AppTest; tạo PR/CI cho Day 5.

### 4.2 Phụ thuộc

- Số liệu/hình từ Phong trước 13:30.
- Nội dung report từ Huy trước 14:30.
- App đã có 5 phương pháp; không cần code model mới.
- Screenshot cần app chạy được với data local.

### 4.3 Checklist công việc chi tiết

#### Task 1 — README cuối

- [ ] Rà lại toàn bộ README, xóa placeholder/stale text.
- [ ] Thêm phần Quickstart từ môi trường sạch:
  - Cài dependencies.
  - Chuẩn bị data.
  - Chạy app.
  - Chạy test/eval.
- [ ] Thêm sơ đồ kiến trúc hoặc mô tả luồng app → service → model.
- [ ] Thêm bảng 5 phương pháp và method key.
- [ ] Thêm kết quả rating/ranking cuối, khớp JSON.
- [ ] Thêm 4 hình Day 5 và 5 screenshot.
- [ ] Thêm mục Demo với user/phim mẫu và fallback cases.
- [ ] Thêm hạn chế và hướng phát triển.
- [ ] Thêm phân công nhóm và link report/eval/review.
- [ ] Kiểm tra link tương đối không hỏng.
- [ ] Không ghi đè số liệu baseline Day 1.

#### Task 2 — Screenshot

- [ ] Chạy `streamlit run app/Home.py`.
- [ ] Chụp 5 ảnh với viewport thống nhất:
  - `reports/figures/day5_home.png`
  - `reports/figures/day5_recommendations.png`
  - `reports/figures/day5_similar.png`
  - `reports/figures/day5_compare.png`
  - `reports/figures/day5_evaluation.png`
- [ ] Recommendations: user 196, method SVD hoặc Hybrid, K=10.
- [ ] Similar Movies: phim 1 (Toy Story), method Hybrid.
- [ ] Compare Methods: user 196, đủ 5 tab (có thể chụp 1–2 tab tiêu biểu).
- [ ] Evaluation: rating table + ranking 5 model.
- [ ] Ảnh rõ chữ, không lộ thông tin ngoài dữ liệu công khai.
- [ ] Chèn ảnh vào README/report/slide.
- [ ] Ghi chú ảnh được chụp từ app thật, không chỉnh sửa nội dung.

#### Task 3 — Demo script & slide

- [ ] Tạo `notes/demo_script.md` theo mẫu Phụ lục 9.3.
- [ ] Ghi rõ thời lượng từng phần (tổng 5–7 phút).
- [ ] Phân vai: Huy mở đầu/kiến trúc, Phong số liệu, Linh demo app.
- [ ] Chuẩn bị user 1/196/405 và phim 1/50/56.
- [ ] Chuẩn bị 2 fallback cases: user lạ, user metadata-only.
- [ ] Chuẩn bị câu chuyện: vì sao Popularity vẫn mạnh, SVD cải thiện rating, Hybrid đánh đổi coverage.
- [ ] Tạo `notes/day5_slides.md` outline 10–12 slide theo Phụ lục 9.2.
- [ ] Nếu cần file trình chiếu, export PDF/PPT từ outline; không commit file nặng nếu không cần.
- [ ] Rehearse ít nhất 2 lần; ghi lại thời gian thực tế.

#### Task 4 — App final check

- [ ] Chạy `pytest tests/test_app.py tests/test_day4_app_integration.py -q`.
- [ ] Kiểm tra 5 trang load không exception.
- [ ] Recommendations: 5 phương pháp, user 1/196/405, K=10.
- [ ] Similar Movies: 4 phương pháp similar, phim 1/50/56.
- [ ] Compare Methods: 5 tab, 50 card với K=10.
- [ ] Evaluation: rating table 2 dòng, ranking table 5 dòng.
- [ ] User không tồn tại fallback Popularity, không crash.
- [ ] `exclude_seen=True` không trả phim đã xem.
- [ ] App không import trực tiếp `src.models`.
- [ ] Sau cache, phản hồi < 2 giây.
- [ ] Kiểm tra log không có exception.

#### Task 5 — PR/CI Day 5

- [ ] Tạo PR từ `feat/day5-final` vào `main`.
- [ ] PR title: `docs(day5): finalize report, demo and screenshots`.
- [ ] PR description có:
  - What: báo cáo/eval/hình/screenshot/demo.
  - Why: chốt sản phẩm và demo cuối.
  - How tested: pytest, ruff, evaluator, smoke, AppTest.
  - Screenshot: 5 ảnh hoặc link.
- [ ] Đính kèm số liệu chính và lệnh tái lập.
- [ ] Xác nhận CI xanh.
- [ ] Nhờ Huy/Phong review.
- [ ] Sau merge, xác nhận README/report trên `main` hiển thị đúng.

### 4.4 Lệnh kiểm tra của Linh

```bash
pytest tests/test_app.py tests/test_day4_app_integration.py -q
pytest -q
ruff check .
streamlit run app/Home.py
```

### 4.5 Tiêu chí hoàn thành

- [ ] README cuối không còn placeholder/stale text.
- [ ] 5 screenshot thật, rõ ràng, có trong repo.
- [ ] Demo script 5–7 phút và slide outline hoàn chỉnh.
- [ ] AppTest pass; app chạy ổn với 5 phương pháp.
- [ ] PR có mô tả và screenshot; CI xanh; merge thành công.

### 4.6 Rủi ro & xử lý

| Rủi ro | Xử lý |
|---|---|
| Không chụp được screenshot | Dùng browser/Playwright có sẵn; dự phòng ảnh từ AppTest không thay thế được thì ghi rõ |
| README quá dài | Ưu tiên quickstart, kết quả, demo, link chi tiết |
| Số liệu lệch report | Chỉ dùng số từ JSON/nguồn Huy chốt |
| Demo quá thời gian | Cắt phần lý thuyết, giữ demo và kết quả |
| App cold start chậm | Warm cache trước demo; có ảnh/video dự phòng |
| CI fail do thiếu dependency | Kiểm tra requirements và log CI |

### 4.7 Báo cáo cuối ngày

- Đã xong: README, 5 screenshot, demo script, slide outline, AppTest.
- README/screenshot/demo: Huy retake screenshot tại `b9a8620`; bổ sung figure/link trong PR #20; demo script và slide đã hoàn chỉnh.
- PR/CI: PR #19 merge tại `d0ade04`, CI xanh tại `b9a8620`.
- Blocker: không có live rehearsal; thay bằng dry-run kỹ thuật 2 lần và screenshot dự phòng.

---

## 5. REVIEW CHÉO & TÍCH HỢP

| Người review | Phạm vi | Deadline | Bằng chứng |
|---|---|---|---|
| Huy → Phong | Metrics, figures, `day5_eval.md` | 15:00 | Comment/checklist trong PR |
| Huy → Linh | README, screenshot, demo, AppTest | 15:00 | Comment/checklist trong PR |
| Phong → Huy | Report: số liệu, protocol, hạn chế | 15:00 | Comment/checklist trong PR |
| Linh → Huy | Report: demo, README, link | 15:00 | Comment/checklist trong PR |

**Quy tắc review:**
- [ ] Không approve nếu số liệu không khớp JSON.
- [ ] Không approve nếu report claim quá mức (ví dụ “Hybrid tốt nhất mọi tiêu chí”).
- [ ] Không approve nếu thiếu screenshot hoặc demo script.
- [ ] Không approve nếu CI chưa xanh.
- [ ] Ghi rõ review là nội bộ, không phải approval độc lập bên ngoài.

---

## 6. CHECKLIST CHUNG CUỐI DAY 5

### Code freeze & phạm vi

- [ ] Không thêm model/dependency/metric mới sau 11:00.
- [ ] Mọi thay đổi sau freeze chỉ là bugfix chặn demo hoặc tài liệu.
- [ ] Không tune hyperparameter/trọng số/threshold/K trên test.
- [ ] Không thay đổi baseline Day 1.

### Kiểm chứng

- [ ] `pytest -q` pass, 106 test.
- [ ] `ruff check .` pass.
- [ ] `run_svd_eval.py` pass.
- [ ] `run_ranking_eval.py` pass.
- [ ] `smoke_svd_hybrid.py` pass.
- [ ] `smoke_item_cf.py`, `smoke_content_based.py`, `smoke_surprise.py` pass.
- [ ] SHA-256 của `svd.json` và `ranking.json` tái lập.
- [ ] `baseline.json` không đổi.
- [ ] App khởi động HTTP 200; warm service < 2 giây.
- [ ] AppTest pass.

### Số liệu & báo cáo

- [ ] Bảng rating khớp `svd.json`.
- [ ] Bảng ranking khớp `ranking.json`.
- [ ] 4 hình Day 5 lấy từ JSON.
- [ ] `notes/day5_eval.md` hoàn chỉnh.
- [ ] `notes/day5_report.md` hoàn chỉnh.
- [ ] Report ghi rõ hạn chế và không phóng đại.
- [ ] Report có phân công và bài học.

### Demo & sản phẩm

- [ ] 5 screenshot thật trong `reports/figures/`.
- [ ] `notes/demo_script.md` 5–7 phút.
- [ ] `notes/day5_slides.md` outline 10–12 slide.
- [ ] Demo chạy end-to-end 2 lần.
- [ ] Fallback cases hoạt động.
- [ ] README có quickstart, kết quả, demo, link.

### Git & CI

- [ ] PR Day 5 có mô tả What/Why/How tested/Screenshot.
- [ ] CI xanh trên PR.
- [ ] PR được review và merge.
- [ ] Tag/release `v1.0.0` hoặc `day5-final` sau merge.
- [ ] Không commit data/model/cache/secret.
- [ ] `main` cuối cùng chứa đầy đủ deliverable.

---

## 7. QUY TẮC GIT

### Branch

- Day 4 finalization: `docs/day4-finalize`.
- Day 5: `feat/day5-final`, tạo từ `origin/main` sau khi Day 4 finalization merge.
- Không làm trực tiếp trên `main`.

### Commit message gợi ý

```text
docs(day4): fill results and finalize CI
docs(day5): add final evaluation and figures
docs(day5): add final report
docs(day5): add demo script and screenshots
docs(day5): finalize README and slides
ci(day5): verify final workflow
```

### PR

- PR title: `docs(day5): finalize report, demo and screenshots`.
- PR description:
  - What: báo cáo, eval, hình, screenshot, demo.
  - Why: chốt sản phẩm và demo cuối.
  - How tested: pytest, ruff, evaluator, smoke, AppTest.
  - Screenshot: 5 ảnh hoặc link.
- Không merge khi CI đỏ.
- Không merge khi chưa có review chéo.

---

## 8. KHI BỊ BLOCK

| Tình huống | Cách xử lý |
|---|---|
| Day 4 finalization chưa merge | Tạo PR riêng, chạy CI, merge trước Day 5; không chồng thay đổi |
| CI fail vì thiếu dependency | Kiểm tra `requirements.txt` và log; không bỏ qua test |
| Metrics không tái lập | Dừng, kiểm tra seed/data/code; không sửa JSON tay |
| Không chụp được screenshot | Dùng browser có sẵn; nếu bất khả kháng, ghi rõ và dùng ảnh từ app local |
| App cold start chậm | Warm cache trước demo; chuẩn bị video/ảnh dự phòng |
| Report số liệu lệch | Đọc lại JSON, dùng script, không copy tay |
| Hết thời gian | Ưu tiên demo + report + CI; bỏ optional bootstrap CI |
| Merge conflict | Rebase branch lên `main`, giải quyết theo file owner |

---

## 9. PHỤ LỤC

### 9.1 Cấu trúc `notes/day5_report.md`

1. Tóm tắt
2. Bài toán và mục tiêu
3. Dữ liệu và tiền xử lý
4. Kiến trúc hệ thống
5. Phương pháp
   - Popularity
   - Content-Based
   - Item-CF
   - SVD
   - Hybrid
6. Giao thức đánh giá
7. Kết quả rating
8. Kết quả ranking
9. Phân tích và thảo luận
10. Demo và hướng dẫn chạy
11. Hạn chế và hướng phát triển
12. Phân công và bài học
13. Tài liệu tham khảo

### 9.2 Outline slide 10–12 slide

1. Title: AI Personalized Recommendation System
2. Bài toán và mục tiêu
3. Dữ liệu MovieLens 100K
4. Kiến trúc hệ thống
5. 5 phương pháp
6. Protocol đánh giá
7. Rating results: Popularity vs SVD
8. Ranking results: 5 phương pháp
9. Trade-off: NDCG vs Coverage
10. Demo app
11. Hạn chế và bài học
12. Q&A

### 9.3 Mẫu `notes/demo_script.md`

```text
0:00–0:30  Mở đầu: bài toán, mục tiêu demo
0:30–1:30  Kiến trúc và 5 phương pháp
1:30–2:30  Rating metrics: Popularity vs SVD
2:30–3:30  Ranking metrics: 5 phương pháp
3:30–5:30  Demo app: Recommendations, Similar, Compare, Evaluation
5:30–6:30  Fallback và cold-start
6:30–7:00  Kết luận, hạn chế, Q&A
```

**Checklist demo:**
- [ ] User 1/196/405.
- [ ] Phim 1/50/56.
- [ ] 5 phương pháp ở Compare.
- [ ] 2 fallback cases.
- [ ] `exclude_seen=True`.
- [ ] Không crash, không chờ quá lâu.

### 9.4 Q&A chuẩn bị

- Vì sao Popularity dẫn đầu NDCG@10?
- Vì sao SVD cải thiện RMSE/MAE nhưng không dẫn ranking?
- Vì sao Hybrid không vượt SVD/Popularity?
- Coverage@10 khác gì NDCG@10?
- Làm sao chống leakage từ test?
- Cold-start được xử lý thế nào?
- Hạn chế lớn nhất của hệ thống?
- Nếu có thêm thời gian, cải thiện gì?

### 9.5 Definition of Done

- [ ] Day 4 finalization merge, CI xanh với hai bước mới.
- [ ] 106 test, lint, evaluator, smoke, AppTest pass.
- [ ] Metrics tái lập; report/eval/README khớp JSON.
- [ ] 4 hình metrics + 5 screenshot thật.
- [ ] Report cuối, eval notes, demo script, slide outline.
- [ ] Demo chạy 2 lần; fallback hoạt động.
- [ ] PR Day 5 review/merge; tag/release.
- [ ] Không có data/model/secret trong git.

### 9.6 Lệnh tổng hợp

```bash
pytest -q
ruff check .
python scripts/run_svd_eval.py
python scripts/run_ranking_eval.py
python scripts/smoke_svd_hybrid.py
python scripts/smoke_item_cf.py
python scripts/smoke_content_based.py
python scripts/smoke_surprise.py
python scripts/make_day5_figures.py
streamlit run app/Home.py
```
