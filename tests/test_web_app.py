import pytest


@pytest.fixture
def client():
    from web.app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_returns_200(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_contains_resume_content(client):
    response = client.get("/")
    html = response.data.decode()
    assert "Resume" in html or "resume" in html


def test_download_returns_pdf(client):
    response = client.get("/download")
    assert response.status_code == 200
    assert response.content_type == "application/pdf"
    assert response.data[:4] == b"%PDF"
