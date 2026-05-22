import json
import logging
import re
from datetime import datetime
from urllib.parse import urlparse

import boto3
import spacy
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()

logger = logging.getLogger(__name__)


def extract_source_article_id(url: str) -> str:
    """Extracts a unique article ID from the URL based on known patterns for each source."""
    bbc_match = re.search(r"/articles/([a-zA-Z0-9]+)", url)
    if bbc_match:
        return bbc_match.group(1)

    ok_match = re.search(r"-(\d+)$", url)
    if ok_match:
        return ok_match.group(1)

    path = urlparse(url).path
    return path.rstrip("/").split("/")[-1]


def clean_source(source: str) -> str:
    """Cleans the source name to create a consistent source ID."""
    return source.lower().replace("!", "").replace(" ", "_")


def generate_article_id(source: str, url: str) -> str:
    """Generates a unique article ID based on the source and URL."""
    source_id = clean_source(source)
    article_id = extract_source_article_id(url)

    return f"{source_id}#{article_id}"


def get_text_for_analysis(article: dict) -> str:
    """Combines title, summary, and body for NLP analysis."""
    return f"{article['title']} {article['summary']} {article['body']}"


def clean_target_name(name: str) -> str:
    """Cleans extracted entity names."""
    return name.strip(""" '"’“”""")


def extract_target_names(text: str) -> list[str]:
    """Extracts and cleans people and organisations using spaCy."""
    doc = nlp(text)

    target_names = {
        clean_target_name(ent.text)
        for ent in doc.ents
        if ent.label_ in ["PERSON", "ORG"]
    }

    return [name for name in target_names if name]


def get_sentiment(text: str) -> tuple[float, str]:
    """Gets sentiment score and label using NLTK VADER."""
    score = sia.polarity_scores(text)["compound"]

    if score >= 0.05:
        label = "positive"
    elif score <= -0.05:
        label = "negative"
    else:
        label = "neutral"

    return score, label


def extract_keywords(text: str) -> list[str]:
    """Extracts the top 10 keywords from text."""

    stop_words = set(stopwords.words("english"))
    tokens = word_tokenize(text.lower())

    keyword_counts = {}

    for token in tokens:
        if token.isalpha() and token not in stop_words and len(token) > 2:
            if token not in keyword_counts:
                keyword_counts[token] = 1
            else:
                keyword_counts[token] += 1

    sorted_keywords = sorted(
        keyword_counts.items(), key=lambda item: item[1], reverse=True
    )

    return [keyword for keyword, count in sorted_keywords[:10]]


def prepare_article_for_dynamodb(article: dict) -> list[dict]:
    """Transforms one article into one or more DynamoDB-ready records."""
    text = get_text_for_analysis(article)
    target_names = extract_target_names(text)
    sentiment_score, sentiment_label = get_sentiment(text)
    keywords = extract_keywords(text)

    if not target_names:
        logger.info("Skipping article with no target names: %s", article["title"])
        return []

    return [
        {
            "article_id": generate_article_id(article["source"], article["link"]),
            "target_name": target_name,
            "at": article["pub_date"],
            "title": article["title"],
            "source": article["source"],
            "url": article["link"],
            "sentiment_score": str(sentiment_score),
            "sentiment_label": sentiment_label,
            "keywords": keywords,
            "description": article["summary"],
        }
        for target_name in target_names
    ]


def prepare_articles_for_dynamodb(articles: list[dict]) -> list[dict]:
    """Transforms a list of articles into DynamoDB-ready dictionaries."""
    prepared_articles = []
    for article in articles:
        prepared_articles.extend(prepare_article_for_dynamodb(article))
    return prepared_articles


def load_articles_from_s3(s3_bucket: str, s3_key: str) -> list[dict]:
    """Loads serialized articles from S3 using the provided bucket and key."""
    s3_client = boto3.client("s3")
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    body = response["Body"].read().decode("utf-8")
    return json.loads(body)


def upload_articles_to_s3(articles: list[dict], bucket: str, key: str) -> None:
    """Uploads enriched articles to S3 as a JSON file."""
    s3_client = boto3.client("s3")
    s3_client.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(articles),
        ContentType="application/json",
    )
    logger.info("Uploaded enriched articles to s3://%s/%s", bucket, key)


def handler(event: dict, context: dict) -> dict:
    """AWS Lambda handler that enriches articles and uploads results to S3."""
    s3_bucket = event.get("s3_bucket", "")
    s3_key = event.get("s3_key", "")

    articles = load_articles_from_s3(s3_bucket, s3_key)
    logger.info("Enrich handler received %d articles", len(articles))
    ready_articles = prepare_articles_for_dynamodb(articles)
    logger.info("Prepared %d articles for DynamoDB", len(ready_articles))

    at = datetime.now().strftime("%Y-%m-%dT%H:%M")
    key = f"enriched_articles/{at}.json"
    upload_articles_to_s3(ready_articles, s3_bucket, key)

    return {"s3_bucket": s3_bucket, "s3_key": key}
