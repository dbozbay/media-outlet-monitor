import os
import boto3
import pandas as pd
import streamlit as st
from boto3.dynamodb.conditions import Key
from dotenv import load_dotenv


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

    response = table.query(
        KeyConditionExpression=Key("target_name").eq(target_name)
    )

    items = response.get("Items", [])

    return pd.DataFrame(items)


st.title("Media Reputation Monitor")

st.write(
    "Search for a celebrity, public figure, or brand to view their media coverage."
)

target_name = st.text_input(
    "Enter celebrity or brand name",
    placeholder="Example: Taylor Swift"
)

if target_name:
    df = query_articles_by_target(target_name)

    if df.empty:
        st.warning(f"No articles found for {target_name}.")
    else:
        st.success(f"Found {len(df)} articles for {target_name}.")
        st.dataframe(df)
