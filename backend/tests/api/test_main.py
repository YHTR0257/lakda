from fastapi.testclient import TestClient
from lakda.main import app

client = TestClient(app)

def test_read_main():
    # ルートパスにGETリクエストを送るテスト
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the lakda Backend API"}

def test_ask_endpoint():
    # askエンドポイントのテスト
    response = client.get("/ask/")
    assert response.status_code == 200

def test_confirm_endpoint():
    # ask/confirmエンドポイントのテスト
    response = client.post("/ask/confirm")
    assert response.status_code == 200