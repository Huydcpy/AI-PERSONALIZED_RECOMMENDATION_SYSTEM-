# AI-PERSONALIZED_RECOMMENDATION_SYSTEM

Hệ thống gợi ý phim sử dụng Machine Learning / Collaborative Filtering.

## Cấu trúc dự án
```text
.
├── app/                  # Ứng dụng Streamlit (pages, components)
├── configs/              # Cấu hình dự án (config.yaml)
├── data/                 # Dữ liệu thô (raw) và đã xử lý (processed)
├── models/               # Mô hình đã huấn luyện (.joblib, .pkl) - không commit
├── notebooks/            # Jupyter Notebooks cho EDA và thử nghiệm
├── reports/              # Báo cáo, biểu đồ (figures) và chỉ số đánh giá (metrics)
├── scripts/              # Các kịch bản chạy tự động
├── src/                  # Mã nguồn chính (data, models, evaluation, service)
├── tests/                # Unit tests
└── docs/                 # Tài liệu dự án
```

## Cài đặt
```bash
pip install -r requirements.txt
```

## Chạy ứng dụng
```bash
streamlit run app/Home.py
```

## Kiểm thử
```bash
pytest -q
ruff check .
```
