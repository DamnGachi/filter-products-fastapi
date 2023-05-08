import json
from typing import Union
from fastapi import FastAPI, File, HTTPException, UploadFile
from crud import remove_color_from_category, crud_update_brand, update_categories, update_sku, set_data_price
from database import my_collection

app = FastAPI(contact=dict(
    name="Developer Telegram",
    url="https://t.me/Holucrap",
    email="maijor18@mail.ru",))


@app.post("/upload")
async def upload_data(data: UploadFile = File(...)):
    contents = await data.read()
    data_dict = json.loads(contents)
    my_collection.insert_many(data_dict)
    return {"status": "Data uploaded successfully!"}

@app.put('/filter')
async def product_filter():
    update_sku(my_collection)
    remove_color_from_category(my_collection)
    update_categories(my_collection)
    crud_update_brand(my_collection)
    set_data_price(my_collection)
    return {"message": "All functions finished successfully"}


@app.get("/data_item")
async def get_data(title: str,):
    query = {"title": title}
    projection = {"_id": 0}

    results = my_collection.find(query, projection).limit(100)

    data = []
    for result in results:
        data.append(result)

    return {"data": data}


@app.get("/data_price")
async def get_data_price(min_price: int, max_price: int):
    if min_price >= max_price:
        raise HTTPException(
            status_code=302, detail="Min price should be lower than or equal to max price")

    query = {"leftovers": {"$elemMatch": {
        "price": {"$gte": min_price, "$lte": max_price}}}
    }
    projection = {"_id": 0}

    results = my_collection.find(query, projection).limit(100)

    data = []
    for result in results:
        data.append(result)
    return {"data": data}


@app.get("/data_brand")
async def get_brands(brand: Union[str, None] = None):
    if brand is not None:
        query = {"brand": brand}
    else:
        query = {}
    projection = {"_id": 0}
    results = my_collection.find(query, projection).sort("brand", 1).limit(100)
    brands = []
    for result in results:
        if result["brand"] == "":
            continue
        brands.append(result)
    return {"brands": brands}


@app.get("/data_size")
async def get_data_size(size: Union[str, None] = None):
    if size is not None:
        query = {"leftovers": {"$elemMatch": {"size": size}}}
    else:
        query = {}
    projection = {"_id": 0}
    results = my_collection.find(query, projection).sort("size", 1).limit(100)
    sizes = []
    for result in results:
        sizes.append(result)
    return {"size": sizes}
