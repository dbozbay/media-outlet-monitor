from io import BytesIO
from unittest.mock import MagicMock, patch

from main import handler, load_articles_to_dynamodb


@patch("main.boto3")
def test_load_articles_to_dynamodb_puts_each_article(mock_boto3):
    mock_table = MagicMock()
    mock_boto3.resource.return_value.Table.return_value = mock_table
    articles = [
        {"article_id": "a1", "title": "First"},
        {"article_id": "a2", "title": "Second"},
    ]

    load_articles_to_dynamodb(articles)

    assert mock_table.put_item.call_count == 2
    mock_table.put_item.assert_any_call(Item=articles[0])
    mock_table.put_item.assert_any_call(Item=articles[1])


@patch("main.load_articles_to_dynamodb")
@patch("main.boto3.client")
def test_handler_loads_from_s3_and_calls_load(mock_client_factory, mock_load):
    articles = [{"article_id": "a1", "title": "Test"}]
    raw_json = '[{"article_id": "a1", "title": "Test"}]'
    mock_s3_client = mock_client_factory.return_value
    mock_s3_client.get_object.return_value = {"Body": BytesIO(raw_json.encode("utf-8"))}

    result = handler(
        {"s3_bucket": "bucket", "s3_key": "enriched_articles/articles.json"}, {}
    )

    mock_s3_client.get_object.assert_called_once_with(
        Bucket="bucket", Key="enriched_articles/articles.json"
    )
    mock_load.assert_called_once_with(articles)
    assert result == {"loaded": 1}
