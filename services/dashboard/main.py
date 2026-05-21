import os
import boto3
import pandas as pd
import streamlit as st
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv
import altair as alt

load_dotenv()

TABLE_NAME = os.getenv("DYNAMO_TABLE_NAME")
REGION_NAME = os.getenv("AWS_REGION_NAME")


def get_dynamodb_table():
    """Connects to DynamoDB and returns the table object."""
    dynamodb = boto3.resource(
        "dynamodb",
        region_name=REGION_NAME,
    )

    return dynamodb.Table(TABLE_NAME)


def query_articles_by_target(target_name: str) -> pd.DataFrame:
    """Queries DynamoDB for articles about a specific target."""

    table = get_dynamodb_table()

    response = table.query(KeyConditionExpression=Key("target_name").eq(target_name))

    items = response.get("Items", [])

    return pd.DataFrame(items)


def create_sentiment_over_time_chart(df: pd.DataFrame, target_name: str):
    """Creates a continuous Altair line chart showing sentiment over time."""

    df["at"] = pd.to_datetime(df["at"])
    df["sentiment_score"] = pd.to_numeric(df["sentiment_score"])

    df = df.sort_values("at")

    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("at:T", title="Published At"),
            y=alt.Y("sentiment_score:Q", title="Sentiment Score"),
            tooltip=[
                "title",
                "source",
                "sentiment_label",
                "sentiment_score",
                "at",
            ],
        )
        .properties(title=f"Sentiment Trend for {target_name}")
    )

    st.altair_chart(chart, use_container_width=True)


def display_article_cards(df: pd.DataFrame):
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
            st.link_button(
                "Read Full Article",
                article["url"]
            )


def filter_dataframe_by_days(df: pd.DataFrame, days: int) -> pd.DataFrame:
    """Filters DataFrame to include only articles from the last N days.

    Args:
        df: DataFrame with articles data
        days: Number of days to look back

    Returns:
        Filtered DataFrame containing only recent articles
    """
    df = df.copy()
    df["at"] = pd.to_datetime(df["at"])
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
    return df[df["at"] >= cutoff_date]


def create_mention_frequency_chart(df: pd.DataFrame, target_name: str, days: int) -> None:
    """Creates a line chart showing mention frequency over time.

    Args:
        df: DataFrame with articles data filtered by time range
        target_name: Name of the target entity
        days: Number of days in the selected time range
    """
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

        # Time range selector for charts
        time_range = st.radio(
            "Select time range for analysis:",
            options=[7, 30],
            format_func=lambda x: f"{x} Days",
            horizontal=True
        )

        # Filter data by selected time range
        filtered_df = filter_dataframe_by_days(df, time_range)

        if not filtered_df.empty:
            # Display mention frequency chart
            create_mention_frequency_chart(
                filtered_df, target_name, time_range)
            
        else:
            st.warning(
                f"No articles found for {target_name} in the last {time_range} days.")
