import boto3

from extract.main import handler as extract_handler
from enrich.main import prepare_articles_for_dynamodb


TABLE_NAME = "c23-mesopelagic-article-db"
REGION_NAME = "eu-west-2"


def load_articles_to_dynamodb(articles: list[dict]) -> None:
    """Loads transformed article dictionaries into DynamoDB."""

    dynamodb = boto3.resource("dynamodb", region_name=REGION_NAME)
    table = dynamodb.Table(TABLE_NAME)

    for article in articles:
        table.put_item(Item=article)


if __name__ == "__main__":
    extracted_articles = extract_handler({}, {})

    transformed_articles = prepare_articles_for_dynamodb(
        extracted_articles
    )

    load_articles_to_dynamodb(transformed_articles)

    print(f"Loaded {len(transformed_articles)} articles")
