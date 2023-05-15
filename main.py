import json
from typing import Union
from fastapi import FastAPI, File, HTTPException, UploadFile
from crud import (
    change_color_product,
    remove_color_from_category,
    crud_update_brand,
    update_categories,
    update_size_cloth,
    update_sku,
    set_data_price
)
from database import my_collection


app = FastAPI()


@app.post("/upload")
async def upload_data(data: UploadFile = File(...)):
    contents = await data.read()
    data_dict = json.loads(contents)
    my_collection.insert_many(data_dict)
    return {"status": "Data uploaded successfully!"}


@app.put('/filter')
async def product_filter():
    set_data_price(my_collection)
    change_color_product(my_collection)
    update_size_cloth(my_collection)
    update_sku(my_collection)
    remove_color_from_category(my_collection)
    update_categories(my_collection)
    crud_update_brand(my_collection)
    return {"message": "All functions finished successfully"}


@app.get("/data")
async def find_all_data(
    title: Union[str, None] = None,
    size: Union[str, None] = None,
    brand: Union[str, None] = None,
    min_price: Union[int, None] = None,
    max_price: Union[int, None] = None
):
    query = {"leftovers": {"$elemMatch": {
        "count": {"$gt": 0}, "count": {"$ne": 0}}}}

    if title:
        query["title"] = title

    if brand:
        query["brand"] = brand

    if size:
        query["leftovers"]["$elemMatch"]["size"] = size

    if min_price and max_price:
        if min_price >= max_price:
            raise HTTPException(
                status_code=302, detail="Min price should be lower than or equal to max price")

        query["leftovers"]["$elemMatch"]["price"] = {
            "$gte": min_price, "$lte": max_price}

    projection = {"_id": 0}
    results = my_collection.find(query, projection).limit(500)

    data = []
    sku = []
    color = []
    danger = ["-1", "-2", "-3", "-4", "-5", "-6", "-7", "-8", "-9", "-R", "-P"]
    for result in results:
        if result["sku"][-2:] in danger:
            result["sku"] = result["sku"][:-2]
        if result["color"] in color and result["sku"] in sku:
            leftovers_sum = sum([sum([item["count"] for item in result["leftovers"]]) for result in data])
            max_price = max([result["price"] for result in data])

        else:
            sku.append(result["sku"])
            color.append(result["color"])
        filtered_leftovers = [
            item for item in result["leftovers"] if item.get("count", 0) > 0]
        result["leftovers"] = filtered_leftovers
        data.append(result)

    return data


@app.get("/data_item")
async def get_data(title: str):
    query = {"title": title}
    projection = {"_id": 0}

    results = my_collection.find(query, projection).limit(500)

    data = []
    for result in results:
        data.append(result)

    return data


@app.get("/data_price")
async def get_data_price(min_price: int, max_price: int):
    if min_price >= max_price:
        raise HTTPException(
            status_code=302, detail="Min price should be lower than or equal to max price")

    query = {"leftovers": {"$elemMatch": {
        "price": {"$gte": min_price, "$lte": max_price}}}
    }
    projection = {"_id": 0}

    results = my_collection.find(query, projection).limit(500)

    data = []
    for result in results:
        data.append(result)
    return data


@app.get("/data_brand")
async def get_brands(brand: Union[str, None] = None):
    if brand is not None:
        query = {"brand": brand}
    else:
        query = {}
    projection = {"_id": 0}
    results = my_collection.find(query, projection).sort("brand", 1).limit(500)
    brands = []
    for result in results:
        if result["brand"] == "":
            continue
        brands.append(result)
    return {"brands": brands}


@app.get("/data_size")
async def get_data_size(size: Union[str, None] = None):
    query = {"leftovers": {"$elemMatch": {"count": {"$gt": 0}}}}
    if size is not None:
        query["leftovers"]["$elemMatch"]["size"] = size
    else:
        query = {}
    projection = {"_id": 0}
    results = my_collection.find(query, projection).limit(100)
    sizes = []
    print(results)
    for result in results:
        sizes.append(result)
    return {"size": sizes}
