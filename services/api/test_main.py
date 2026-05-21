from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from main import app, get_articles, get_articles_by_target

client = TestClient(app)

ARTICLE_BBC = {
    "article_id": "a1",
    "target_name": "BBC",
    "title": "BBC News",
    "url": "https://bbc.com/news/1",
    "source": "BBC News",
    "description": "A test article",
    "at": "2026-05-20T10:00:00",
    "keywords": ["test"],
    "sentiment_label": "positive",
    "sentiment_score": "0.8",
}

ARTICLE_CNN = {
    "article_id": "a2",
    "target_name": "CNN",
    "title": "CNN News",
    "url": "https://cnn.com/news/1",
    "source": "CNN",
    "description": "Another test article",
    "at": "2026-05-20T11:00:00",
    "keywords": ["test"],
    "sentiment_label": "negative",
    "sentiment_score": "-0.5",
}


@patch("main.boto3")
def test_get_articles_scans_table(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [ARTICLE_BBC, ARTICLE_CNN]}
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


@patch("main.boto3")
def test_get_articles_endpoint_returns_200(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [ARTICLE_BBC]}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    response = client.get("/articles")

    assert response.status_code == 200
    assert response.json()[0]["article_id"] == "a1"


@patch("main.boto3")
def test_get_articles_endpoint_returns_404_when_empty(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": []}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    response = client.get("/articles")

    assert response.status_code == 404


@patch("main.boto3")
def test_get_articles_by_target_filters_by_name(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [ARTICLE_BBC, ARTICLE_CNN]}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    result = get_articles_by_target("BBC")

    mock_table.scan.assert_called_once()
    assert len(result) == 1
    assert result[0]["target_name"] == "BBC"


@patch("main.boto3")
def test_get_articles_by_target_is_case_insensitive(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [ARTICLE_BBC]}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    result = get_articles_by_target("bbc")

    assert len(result) == 1


@patch("main.boto3")
def test_get_articles_by_target_filters_by_sentiment(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [ARTICLE_BBC]}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    result = get_articles_by_target("BBC", sentiment="negative")

    assert result == []


@patch("main.boto3")
def test_get_articles_by_target_returns_empty_list_when_no_match(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [ARTICLE_BBC]}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    result = get_articles_by_target("NonExistent")

    assert result == []


@patch("main.boto3")
def test_get_articles_by_target_endpoint_returns_200(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [ARTICLE_BBC]}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    response = client.get("/articles/BBC")

    assert response.status_code == 200
    assert response.json()[0]["target_name"] == "BBC"


@patch("main.boto3")
def test_get_articles_by_target_endpoint_with_sentiment_param(mock_boto3):
    mock_table = MagicMock()
    mock_table.scan.return_value = {"Items": [ARTICLE_BBC]}
    mock_boto3.resource.return_value.Table.return_value = mock_table

    response = client.get("/articles/BBC?sentiment=positive")

    assert response.status_code == 200
    assert response.json()[0]["sentiment_label"] == "positive"
