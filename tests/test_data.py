import json
import pymongo
import pytest
from aiohttp import web
from http.client import HTTPException


@pytest.fixture
async def client(aiohttp_client):
    app = web.Application()
    client = await aiohttp_client(app)
    return client


@pytest.fixture(scope="session")
def mongo_client():
    uri = "mongodb+srv://admin:admin@dastish.gf1hbe3.mongodb.net/?retryWrites=true&w=majority"
    client = pymongo.MongoClient(uri)
    yield client
    client.close()


@pytest.fixture()
def product_data():
    with open('data.json', encoding='utf-8') as f:
        data = json.load(f)
    return data[10]


def test_product_title(product_data):
    assert isinstance(product_data['title'], str)
    assert len(product_data['title']) > 0


def test_product_sku(product_data):
    assert isinstance(product_data['sku'], str)
    assert len(product_data['sku']) > 0


def test_product_price(product_data):
    assert isinstance(product_data['price'], int)
    assert product_data['price'] >= 0


def test_product_discount_price(product_data):
    assert isinstance(product_data['discount_price'], int)
    assert product_data['discount_price'] >= 0


def test_product_leftovers(product_data):
    assert isinstance(product_data['leftovers'], list)
    assert len(product_data['leftovers']) > 0


def test_create_collection(mongo_client):
    db = mongo_client.myDatabase
    collection_name = "test_collection"
    if collection_name not in db.list_collection_names():
        db.create_collection(collection_name)

    assert collection_name in db.list_collection_names()
