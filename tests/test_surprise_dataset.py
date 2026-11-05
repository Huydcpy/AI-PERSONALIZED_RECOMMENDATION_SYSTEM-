import pandas as pd

from src.data.surprise_dataset import build_surprise_trainset, build_testset


def test_build_surprise_dataset():
    train = pd.DataFrame(
        {
            "user_id": [1, 1, 2],
            "movie_id": [1, 2, 1],
            "rating": [5.0, 4.0, 3.0],
        }
    )
    test = pd.DataFrame(
        {
            "user_id": [2],
            "movie_id": [2],
            "rating": [4.0],
        }
    )

    trainset = build_surprise_trainset(train)
    assert trainset.n_ratings == len(train)
    assert build_testset(test) == [(2, 2, 4.0)]