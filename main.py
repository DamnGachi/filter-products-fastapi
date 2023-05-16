import json
import re
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
    sku: Union[str, None] = None,
    min_price: Union[int, None] = None,
    max_price: Union[int, None] = None
):
    query = {"leftovers": {"$elemMatch": {
        "count": {"$gt": 0}, "count": {"$ne": 0}}}}

    if title:
        query["title"] = title

    if sku:
        regex_pattern = re.escape(sku) + ".*$"
        query["sku"] = {"$regex": regex_pattern}

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
    data_dict = {}
    sku_set = set()
    color = []
    danger = ["-1", "-2", "-3", "-4", "-5", "-6",
              "-7", "-8", "-9", "-R", "-P", "-R-R"]
    for result in results:
        filtered_leftovers = [
            item for item in result["leftovers"] if item.get("count", 0) > 0]
        result["leftovers"] = filtered_leftovers
        if result["sku"][-4:] in danger:
            result["sku"] = result["sku"][:-4]
        elif result["sku"][-2:] in danger:
            result["sku"] = result["sku"][:-2]
        try:
            col = result["color"].split("/")[0]
            unique_key = (result["sku"], col)
            if unique_key in data_dict:
                # Если комбинация sku и color уже существует в словаре, суммируем значения count
                existing_leftovers = data_dict[unique_key]
                for item in result["leftovers"]:
                    size = item["size"]
                    count = item["count"]
                    price = item["price"]
                    existing_item = next(
                        (x for x in existing_leftovers if x["size"] == size and x["price"] == price), None)
                    if existing_item:
                        existing_item["count"] += count
                    else:
                        existing_leftovers.append(item)
            else:
                # Если комбинация sku и color еще не существует в словаре, добавляем ее
                data_dict[unique_key] = result["leftovers"]
                sku_set.add(result["sku"])
                color.append(col)

                result["leftovers"] = result["leftovers"]
                data.append(result)
        except KeyError:
            continue
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
    for result in results:
        sizes.append(result)
    return {"size": sizes}
