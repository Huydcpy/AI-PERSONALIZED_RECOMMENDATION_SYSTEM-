import os
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

DATA_FILES = [Path(f"data/processed/{name}.parquet") for name in ("train", "movies", "users")]


@pytest.mark.skipif(
    not all(path.exists() for path in DATA_FILES) and not os.environ.get("CI"),
    reason="Requires processed data",
)
def test_pages_and_content_based_interactions():
    assert all(path.exists() for path in DATA_FILES), "CI must prepare integration data"
    for page in [Path("app/Home.py"), *sorted(Path("app/pages").glob("*.py"))]:
        app = AppTest.from_file(str(page.resolve()), default_timeout=30).run()
        assert not app.exception
    app = AppTest.from_file(str(Path("app/pages/2_Recommendations.py").resolve()), default_timeout=30).run()
    app.selectbox[1].set_value("content_based")
    for uid in (1, 196, 405):
        app.selectbox[0].set_value(uid)
        app.button[0].click().run()
        assert not app.exception and not app.error
        assert len(app.metric) == 10
        assert any("content_based" in item.value for item in app.caption)
    app = AppTest.from_file(str(Path("app/pages/3_Similar_Movies.py").resolve()), default_timeout=30).run()
    for title in ("Toy Story", "Star Wars", "Pulp Fiction"):
        app.text_input[0].set_value(title).run()
        app.button[0].click().run()
        assert not app.exception and not app.error
        assert len(app.metric) == 10


@pytest.mark.skipif(not all(path.exists() for path in DATA_FILES), reason="Requires processed data")
def test_item_cf_interactions_and_ranking_page():
    app = AppTest.from_file(str(Path("app/pages/2_Recommendations.py").resolve()), default_timeout=30).run()
    app.selectbox[1].set_value("item_cf")
    for uid in (1, 196, 405):
        app.selectbox[0].set_value(uid)
        app.button[0].click().run()
        assert not app.exception and not app.error
        assert len(app.metric) == 10
        assert any("item_cf" in item.value for item in app.caption)
    app = AppTest.from_file(str(Path("app/pages/3_Similar_Movies.py").resolve()), default_timeout=30).run()
    for title in ("Toy Story", "Star Wars", "Pulp Fiction"):
        app.text_input[0].set_value(title).run()
        app.selectbox[1].set_value("item_cf")
        app.button[0].click().run()
        assert not app.exception and not app.error
        assert len(app.metric) == 10
        assert any("item_cf" in item.value for item in app.caption)
    app = AppTest.from_file(str(Path("app/pages/4_Compare_Methods.py").resolve()), default_timeout=30).run()
    assert not app.exception and not app.warning
    assert len(app.metric) == 50
    app = AppTest.from_file(str(Path("app/pages/5_Evaluation.py").resolve()), default_timeout=30).run()
    assert not app.exception and not app.error
    if Path("reports/metrics/ranking.json").exists():
        assert len(app.dataframe) == 2
