import logging
import re
from urllib.parse import urlparse

import spacy
from nltk.corpus import stopwords
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize

nlp = spacy.load("en_core_web_sm")
sia = SentimentIntensityAnalyzer()
logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure root logging. Call once from the entrypoint."""
    logging.basicConfig(
        level=logging.INFO,
        format="{asctime} - {levelname} - {name} - {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M",
    )


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

    return [
        name
        for name in target_names
        if name
    ]


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


def handler(event: list[dict], context: dict) -> list[dict]:
    """AWS Lambda handler that transforms serialized articles into DynamoDB-ready dicts."""
    configure_logging()
    logger.info("Enrich handler received %d articles", len(event))
    ready_articles = prepare_articles_for_dynamodb(event)
    logger.info("Prepared %d articles for DynamoDB", len(ready_articles))
    return ready_articles
