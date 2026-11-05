import pandas as pd
import numpy as np

class RecommenderService:
    def __init__(self, ratings_path: str | None = None, items_path: str | None = None):
        self.ratings_df = None
        self.items_df = None
        if ratings_path:
            self.load_data(ratings_path, items_path)

    def load_data(self, ratings_path: str | None, items_path: str | None = None):
        """Tải dữ liệu đánh giá và danh mục sản phẩm/phim."""
        if ratings_path:
            self.ratings_df = pd.read_csv(ratings_path)
        if items_path:
            self.items_df = pd.read_csv(items_path)

    def get_popular_recommendations(self, top_n: int = 5) -> list:
        """Gợi ý danh sách phổ biến nhất (Fallback baseline)."""
        if self.ratings_df is None or self.ratings_df.empty:
            return ["Movie A", "Movie B", "Movie C"] # Mock data nếu chưa có file dữ liệu
        
        top_items = self.ratings_df.groupby('item_id')['rating'].mean().reset_index()
        top_items = top_items.sort_values(by='rating', ascending=False).head(top_n)
        return top_items['item_id'].tolist()