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
def test_handler_returns_event(mock_load):
    event = [{"article_id": "a1", "title": "Test"}]

    result = handler(event, {})

    assert result == event
    mock_load.assert_called_once_with(event)
