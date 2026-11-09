from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest


@pytest.mark.skipif(not Path("data/processed/train.parquet").exists(), reason="Requires processed data")
def test_day4_methods_and_evaluation_tables():
    for method in ("svd", "hybrid"):
        app = AppTest.from_file(str(Path("app/pages/2_Recommendations.py").resolve()), default_timeout=30).run()
        app.selectbox[1].set_value(method)
        for uid in (1, 196, 405):
            app.selectbox[0].set_value(uid)
            app.button[0].click().run()
            assert not app.exception and not app.error
            assert len(app.metric) == 10
            assert any(method in item.value for item in app.caption)
        app = AppTest.from_file(str(Path("app/pages/3_Similar_Movies.py").resolve()), default_timeout=30).run()
        for title in ("Toy Story", "Star Wars", "Pulp Fiction"):
            app.text_input[0].set_value(title).run()
            app.selectbox[1].set_value(method)
            app.button[0].click().run()
            assert not app.exception and not app.error
            assert len(app.metric) == 10
            assert any(method in item.value for item in app.caption)
    app = AppTest.from_file(str(Path("app/pages/4_Compare_Methods.py").resolve()), default_timeout=30).run()
    assert not app.exception and not app.error
    assert len(app.tabs) == 5 and len(app.metric) == 50
    app = AppTest.from_file(str(Path("app/pages/5_Evaluation.py").resolve()), default_timeout=30).run()
    assert not app.exception and not app.error
    assert len(app.dataframe) == 2
    assert len(app.dataframe[0].value) == 2
    assert len(app.dataframe[1].value) == 5

