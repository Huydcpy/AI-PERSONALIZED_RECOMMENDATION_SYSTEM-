"""Contract chung cho tất cả các recommender trong dự án."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Recommendation:
    """Một gợi ý phim trả về cho người dùng.

    Attributes:
        movie_id: ID phim trong MovieLens.
        title: Tiêu đề phim.
        score: Điểm dự đoán/phù hợp do model tính.
        method: Tên phương pháp sinh ra gợi ý (ví dụ: ``popularity``).
        reason: Giải thích ngắn vì sao phim được gợi ý.
    """

    movie_id: int
    title: str
    score: float
    method: str
    reason: str | None = None


class Recommender(Protocol):
    """Interface mà mọi recommender phải implement."""

    name: str

    def recommend(
        self, user_id: int, k: int = 10, exclude_seen: bool = True
    ) -> list[Recommendation]:
        """Trả về tối đa ``k`` phim gợi ý cho ``user_id``.

        Args:
            user_id: ID người dùng.
            k: Số lượng gợi ý tối đa.
            exclude_seen: Nếu True, loại các phim người dùng đã rating
                trong tập train.

        Returns:
            Danh sách ``Recommendation`` đã sắp xếp theo độ phù hợp giảm dần.
        """
        ...

    def similar_items(
        self, movie_id: int, k: int = 10
    ) -> list[Recommendation]:
        """Trả về tối đa ``k`` phim tương tự với ``movie_id``.

        Args:
            movie_id: ID phim gốc.
            k: Số lượng phim tương tự tối đa.

        Returns:
            Danh sách ``Recommendation`` đã sắp xếp theo độ tương đồng giảm dần.
        """
        ...
