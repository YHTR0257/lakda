from fastapi.testclient import TestClient
from lakda.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the lakda Backend API"}

def test_confirm_endpoint_missing_body_returns_422():
    # リクエストボディなしの場合はバリデーションエラー
    response = client.post("/ask/confirm")
    assert response.status_code == 422
