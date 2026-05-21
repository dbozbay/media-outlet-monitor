import pandas as pd
import pytest

from main import filter_dataframe_by_days


@pytest.fixture
def sample_articles_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "title": ["Recent Article", "Old Article", "Very Old Article"],
            "at": [
                pd.Timestamp.now() - pd.Timedelta(days=1),
                pd.Timestamp.now() - pd.Timedelta(days=10),
                pd.Timestamp.now() - pd.Timedelta(days=60),
            ],
            "source": ["Source A", "Source B", "Source C"],
        }
    )


class TestFilterDataFrameByDays:
    def test_filter_by_7_days_returns_only_recent(
        self, sample_articles_df: pd.DataFrame
    ) -> None:
        result = filter_dataframe_by_days(sample_articles_df, days=7)

        assert len(result) == 1
        assert result.iloc[0]["title"] == "Recent Article"

    def test_filter_by_30_days_excludes_old_articles(
        self, sample_articles_df: pd.DataFrame
    ) -> None:
        result = filter_dataframe_by_days(sample_articles_df, days=30)

        assert len(result) == 2
        assert "Very Old Article" not in result["title"].values

    def test_filter_by_90_days_returns_all(
        self, sample_articles_df: pd.DataFrame
    ) -> None:
        result = filter_dataframe_by_days(sample_articles_df, days=90)

        assert len(result) == 3

    def test_filter_empty_dataframe_returns_empty(self) -> None:
        df = pd.DataFrame(columns=["title", "at", "source"])

        result = filter_dataframe_by_days(df, days=7)

        assert result.empty

    def test_filter_does_not_mutate_original(
        self, sample_articles_df: pd.DataFrame
    ) -> None:
        original_len = len(sample_articles_df)

        filter_dataframe_by_days(sample_articles_df, days=7)

        assert len(sample_articles_df) == original_len
