# Day 2 cross-review record

Reviewed on 07/11/2026 against `notes/task_day2_6_11.md`, covering PR #7 (model/service/tests), PR #8 (integration) and PR #10 (Linh Day 2).

## Model

- `ContentBasedRecommender` uses only `train_df` and `movies_df`; `test_df` is not read when fitting or building profiles.
- 18 known genres are used; `unknown` is excluded; genre vectors and user profiles are L2-normalized.
- Similarity is cosine over the genre matrix, clipped to `[0, 1]`; self is excluded from `similar_items`.
- Ties are deterministic by ascending `movie_id`.
- Cold-start users, zero-genre movies and short result lists fall back to Popularity with explicit method and reason.
- Invalid movie IDs raise `ValueError`.

## Service

- Popularity is initialized before Content-Based and passed as fallback.
- `content_based` is registered in `self.models`; `recommend` and `similar_items` route correctly.
- Invalid methods raise `ValueError` with the Day 3/4 message.
- Service does not import Streamlit; app does not import `src.models` directly.
- User profile statistics use train history.

## App

- Page 2 supports Popularity and Content-Based, K from 5 to 20 and `exclude_seen`.
- Page 3 uses Content-Based by default and displays the reason.
- Page 4 compares Popularity and Content-Based; Home and README describe the Day 2 state.
- Cards display method and reason.
- `st.cache_resource` caches the service; `st.cache_data` caches metrics.
- AppTest passed for Home, all five pages, three users and three movie searches.
- Streamlit started headless on port 8599; health endpoint and root page returned OK; screenshot saved at `reports/figures/day2_home.png`.

## Commands re-run

```text
pytest -q -p no:cacheprovider              -> 41 passed
ruff check .                               -> All checks passed
python scripts/smoke_content_based.py      -> pass
python scripts/smoke_surprise.py           -> RMSE 0.9540
grep -R "from src.models" app/             -> no matches
```

## CI and PR status

- GitHub Actions CI passed at commit `7804b97`.
- PR #5 closed as superseded; PR #7, #8 and #10 merged into `main`.

## Review limitation

The repository currently has one maintainer account. GitHub does not allow that account to approve its own pull requests, so formal APPROVED reviews cannot be created for #7, #8 or #10. This retrospective review records the checks that were performed instead.
