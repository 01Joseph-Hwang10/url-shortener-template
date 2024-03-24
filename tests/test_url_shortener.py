import pytest
from fastapi.testclient import TestClient
from app import app


@pytest.fixture(scope="module")
def shared():
    return {
        "test_create_short_url": {
            "original_url": "https://www.google.com",
        }
    }


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.mark.order(1)
def test_health_check(client: TestClient):
    """`GET /` 라우트가 200 상태 코드를 반환하는지 확인합니다."""
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.order(2)
def test_create_short_url(client: TestClient, shared: dict):
    """애플리케이션이 주어진 URL에 대한 shortened URL을 생성하는지 확인합니다."""
    # Execute the request
    original_url = shared.get("test_create_short_url").get("original_url")
    response = client.post("/", json={"url": original_url})

    # Response should be 201 Created
    assert response.status_code == 201

    # Response body should contain original URL, short slug and short URL
    response_body = response.json()
    assert response_body["original_url"] == original_url
    assert response_body["short_slug"] is not None
    assert response_body["short_url"] is not None

    # Save the short slug and short URL for future tests
    shared["test_create_short_url"]["short_slug"] = response_body["short_slug"]
    shared["test_create_short_url"]["short_url"] = response_body["short_url"]


@pytest.mark.order(3)
def test_create_short_url_again(client: TestClient, shared: dict):
    """애플리케이션은 이미 생성된 shortened URL이 있다면 해당 URL을 반환해야 합니다."""
    # Execute the request
    original_url = shared.get("test_create_short_url").get("original_url")
    response = client.post("/", json={"url": original_url})

    # Response should be 200 OK
    assert response.status_code == 200

    # Response body should contain original URL, short slug and short URL
    response_body = response.json()
    assert response_body["original_url"] == original_url
    assert response_body["short_slug"] == shared["test_create_short_url"]["short_slug"]
    assert response_body["short_url"] is not None


@pytest.mark.order(4)
def test_create_invalid_short_url(client: TestClient):
    """애플리케이션은 유효하지 않은 URL을 입력받았을 때 400 상태 코드를 반환해야 합니다."""
    # Execute the request
    response = client.post("/", json={"url": "invalid-url"})

    # Response should be 400 Bad Request
    assert response.status_code == 400


@pytest.mark.order(5)
def test_get_short_url(client: TestClient, shared: dict):
    """애플리케이션은 shortened URL을 입력받아 원래 URL로 리디렉션해야 합니다."""
    # Execute the request
    short_slug = shared.get("test_create_short_url").get("short_slug")
    response = client.get(f"/{short_slug}", follow_redirects=True)

    # Seems like the status shown to the user is 200 OK
    assert response.status_code == 200

    # Response url should be the original URL
    assert response.url == shared.get("test_create_short_url").get("original_url")


@pytest.mark.order(6)
def test_get_invalid_short_url(client: TestClient):
    """애플리케이션은 존재하지 않는 shortened URL을 입력받았을 때 404 상태 코드를 반환해야 합니다."""
    # Execute the request
    response = client.get("/invalid-short-slug")

    # Response should be 404 Not Found
    assert response.status_code == 404
