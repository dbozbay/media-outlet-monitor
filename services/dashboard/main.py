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
        st.dataframe(df)
        create_sentiment_over_time_chart(df, target_name)
