import pytest
from aiohttp import web
from http.client import HTTPException


@pytest.fixture
async def client(aiohttp_client):
    app = web.Application()
    client = await aiohttp_client(app)
    return client


def test_valid_data_price_request():
    response = client.get("/data_price?min_price=2000&max_price=4000")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0


def test_invalid_data_price_request():
    response = client.get("/data_price?min_price=4000&max_price=2000")
    assert response.status_code == 302
    assert "Min price should be lower than or equal to max price" in response.text


def test_data_price_response_type():
    response = client.get("/data_price?min_price=2000&max_price=4000")
    assert isinstance(response.json(), dict)
    assert isinstance(response.json()["data"], list)


def test_data_price_limit():
    response = client.get("/data_price?min_price=2000&max_price=4000")
    assert len(response.json()["data"]) <= 100


def test_data_price_response_fields():
    response = client.get("/data_price?min_price=2000&max_price=4000")
    data = response.json()["data"][0]
    assert "title" in data
    assert "sku" in data
    assert "price" in data
    assert "discount_price" in data
    assert "leftovers" in data


def test_data_price_exception():
    with pytest.raises(HTTPException):
        client.get("/data_price?min_price=5000&max_price=4000")
