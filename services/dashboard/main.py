import os
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st
from boto3 import resource
from dotenv import load_dotenv

load_dotenv()


def get_dynamodb_table() -> Any:
    """Connects to DynamoDB and returns the table object."""
    db = resource(
        "dynamodb",
        region_name=os.getenv("AWS_REGION_NAME"),
    )
    return db.Table(os.getenv("DYNAMO_TABLE_NAME"))


def query_articles_by_target(target_name: str) -> pd.DataFrame:
    """Scans DynamoDB for articles about a specific target."""

    table = get_dynamodb_table()

    response = table.scan()

    items = response.get("Items", [])

    matching_items = []

    for item in items:
        if item["target_name"].lower() == target_name.strip().lower():
            matching_items.append(item)

    return pd.DataFrame(matching_items)


def filter_dataframe_by_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Filters DataFrame to include only articles from the last N days."""
    df = df.copy()
    df["at"] = pd.to_datetime(df["at"])
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
    return df[df["at"] >= cutoff_date]


def create_mention_frequency_chart(
    df: pd.DataFrame, target_name: str, days: int
) -> None:
    """Creates a line chart showing mention frequency over time."""
    df = df.copy()
    df["at"] = pd.to_datetime(df["at"])
    df["date"] = df["at"].dt.date

    # Group by date and count mentions
    frequency_df = df.groupby("date").size().reset_index(name="mention_count")
    frequency_df = frequency_df.sort_values("date")

    chart = (
        alt.Chart(frequency_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("mention_count:Q", title="Number of Mentions"),
            tooltip=["date:T", "mention_count:Q"],
        )
        .properties(title=f"Mention Frequency for {target_name} (Last {days} Days)")
    )

    st.altair_chart(chart, use_container_width=True)


def create_sentiment_over_time_chart(df: pd.DataFrame, target_name: str) -> None:
    """Creates a daily average sentiment trend chart."""

    df = df.copy()
    df["at"] = pd.to_datetime(df["at"])
    df["sentiment_score"] = pd.to_numeric(df["sentiment_score"])
    df["date"] = df["at"].dt.date

    daily_sentiment_df = df.groupby("date")["sentiment_score"].mean().reset_index()

    chart = (
        alt.Chart(daily_sentiment_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("sentiment_score:Q", title="Average Sentiment Score"),
            tooltip=["date:T", "sentiment_score:Q"],
        )
        .properties(title=f"Average Daily Sentiment for {target_name}")
    )

    st.altair_chart(chart, use_container_width=True)


def display_article_cards(df: pd.DataFrame) -> None:
    """Displays articles as styled Streamlit cards."""

    sorted_df = df.sort_values(by="at", ascending=False)

    for _, article in sorted_df.iterrows():
        sentiment = article["sentiment_label"]

        if sentiment == "positive":
            sentiment_emoji = "🟢"

        elif sentiment == "negative":
            sentiment_emoji = "🔴"

        else:
            sentiment_emoji = "🟡"

        keywords = ", ".join(article["keywords"])

        with st.container(border=True):
            st.subheader(article["title"])
            st.markdown(
                f"""
                    **Source:** {article["source"]}

                    **Published:** {article["at"]}

                    **Sentiment:** {sentiment_emoji} {article["sentiment_score"]} ({sentiment})

                    **Keywords:** {keywords}
                    """
            )
            st.link_button("Read Full Article", article["url"])


def create_sentiment_distribution_chart(df: pd.DataFrame, target_name: str) -> None:
    """Creates a bar chart showing positive, neutral and negative article counts."""
    sentiment_df = df["sentiment_label"].value_counts().reset_index()
    sentiment_df.columns = ["sentiment_label", "count"]

    chart = (
        alt.Chart(sentiment_df)
        .mark_bar()
        .encode(
            x=alt.X("sentiment_label:N", title="Sentiment"),
            y=alt.Y("count:Q", title="Number of Articles"),
            tooltip=["sentiment_label", "count"],
        )
        .properties(title=f"Sentiment Breakdown for {target_name}")
    )

    st.altair_chart(chart, use_container_width=True)


def create_top_keywords_chart(df: pd.DataFrame, target_name: str) -> None:
    """Creates a bar chart showing the most common keywords."""
    all_keywords = []

    for keywords in df["keywords"]:
        if isinstance(keywords, list):
            all_keywords.extend(keywords)

    keyword_df = pd.Series(all_keywords).value_counts().head(10).reset_index()
    keyword_df.columns = ["keyword", "count"]

    chart = (
        alt.Chart(keyword_df)
        .mark_bar()
        .encode(
            x=alt.X("count:Q", title="Mentions"),
            y=alt.Y("keyword:N", sort="-x", title="Keyword"),
            tooltip=["keyword", "count"],
        )
        .properties(title=f"Top Keywords for {target_name}")
    )

    st.altair_chart(chart, use_container_width=True)


def create_source_distribution_chart(df: pd.DataFrame, target_name: str) -> None:
    """Creates a bar chart showing article count by source."""
    source_df = df["source"].value_counts().reset_index()
    source_df.columns = ["source", "count"]

    chart = (
        alt.Chart(source_df)
        .mark_bar()
        .encode(
            x=alt.X("source:N", title="Source"),
            y=alt.Y("count:Q", title="Number of Articles"),
            tooltip=["source", "count"],
        )
        .properties(title=f"Coverage by Source for {target_name}")
    )

    st.altair_chart(chart, use_container_width=True)


def main() -> None:
    """Main function to run the Streamlit dashboard."""
    st.title("Media Reputation Monitor")

    st.write(
        "Search for a celebrity, public figure, or brand to view their media coverage."
    )

    target_name = st.text_input(
        "Enter celebrity or brand name", placeholder="Example: Taylor Swift"
    )

    if target_name:
        df = query_articles_by_target(target_name)

        if df.empty:
            st.warning(f"No articles found for {target_name}.")
        else:
            st.success(f"Found {len(df)} articles for {target_name}.")
            display_article_cards(df)
            create_sentiment_over_time_chart(df, target_name)
            create_sentiment_distribution_chart(df, target_name)
            create_top_keywords_chart(df, target_name)
            create_source_distribution_chart(df, target_name)

            # Time range selector for charts
            time_range = st.radio(
                "Select time range for analysis:",
                options=[7, 30],
                format_func=lambda x: f"{x} Days",
                horizontal=True,
            )

            # Filter data by selected time range
            filtered_df = filter_dataframe_by_days(df, time_range)

            if not filtered_df.empty:
                # Display mention frequency chart
                create_mention_frequency_chart(filtered_df, target_name, time_range)

            else:
                st.warning(
                    f"No articles found for {target_name} in the last {time_range} days."
                )


if __name__ == "__main__":
    main()
