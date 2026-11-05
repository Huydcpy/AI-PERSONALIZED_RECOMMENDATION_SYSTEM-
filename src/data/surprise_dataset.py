from surprise import Dataset, Reader


def build_surprise_trainset(train_df):
    reader = Reader(rating_scale=(1, 5))
    data = Dataset.load_from_df(
        train_df[["user_id", "movie_id", "rating"]],
        reader,
    )
    return data.build_full_trainset()


def build_testset(test_df) -> list[tuple[int, int, float]]:
    return list(
        test_df[["user_id", "movie_id", "rating"]]
        .itertuples(index=False, name=None)
    )