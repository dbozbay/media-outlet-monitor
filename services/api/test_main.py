from unittest.mock import MagicMock, patch

from main import get_articles, get_articles_by_target, handler


@patch("main.boto3")
def test_get_articles_scans_table(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {
        "Items": [
            {"article_id": "a1", "target_name": "BBC", "title": "First"},
            {"article_id": "a2", "target_name": "CNN", "title": "Second"},
        ]
    }
    mock_boto3.resource.return_value.Table.return_value = mock_table

    result = get_articles()

    mock_table.scan.assert_called_once()
    assert len(result) == 2
    assert result[0]["article_id"] == "a1"
    assert result[1]["target_name"] == "CNN"


@patch("main.boto3")
def test_get_articles_returns_empty_list_when_no_items(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": []}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    result = get_articles()

    assert result == []


@patch("main.get_articles")
def test_handler_returns_200_with_articles(mock_get_articles):
    mock_get_articles.return_value = [
        {"article_id": "a1", "title": "Test"}
    ]

    response = handler({"routeKey": "GET /articles"}, {})

    assert response["statusCode"] == 200
    assert '"article_id": "a1"' in response["body"]


@patch("main.get_articles")
def test_handler_returns_500_on_error(mock_get_articles):
    mock_get_articles.side_effect = Exception("DynamoDB error")

    response = handler({"routeKey": "GET /articles"}, {})

    assert response["statusCode"] == 500
    assert "error" in response["body"]


@patch("main.boto3")
def test_get_articles_by_target_queries_partition_key(mock_boto3):
    mock_table = MagicMock()
    mock_table.query.return_value = {
        "Items": [
            {"article_id": "a1", "target_name": "BBC", "title": "BBC News"},
            {"article_id": "a2", "target_name": "BBC", "title": "BBC Sport"},
        ]
    }
    mock_boto3.resource.return_value.Table.return_value = mock_table

    result = get_articles_by_target("BBC")

    mock_table.query.assert_called_once()
    assert len(result) == 2
    assert all(item["target_name"] == "BBC" for item in result)


@patch("main.boto3")
def test_get_articles_by_target_returns_empty_list_when_no_match(mock_boto3):
    mock_table = MagicMock()
    mock_table.query.return_value = {"Items": []}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    result = get_articles_by_target("NonExistent")

    assert result == []


@patch("main.get_articles_by_target")
def test_handler_get_articles_by_target_returns_200(mock_get_by_target):
    mock_get_by_target.return_value = [
        {"article_id": "a1", "target_name": "BBC", "title": "Test"}
    ]

    response = handler(
        {
            "routeKey": "GET /articles/{target_name}",
            "pathParameters": {"target_name": "BBC"},
        },
        {},
    )

    assert response["statusCode"] == 200
    assert '"target_name": "BBC"' in response["body"]
    mock_get_by_target.assert_called_once_with("BBC")
