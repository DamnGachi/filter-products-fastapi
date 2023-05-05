import json
from fastapi import FastAPI, File, HTTPException, UploadFile
from database import my_collection

app = FastAPI()


@app.put("/set_price")
async def set_price():

    items = my_collection.find()

    for item in items:
        if item.get("discount_price", 0) > 0:
            item["price"] = item["discount_price"]
        else:
            item["discount_price"] = 0

        if item["discount_price"] > item["price"] or item["price"] == item["discount_price"]:
            item["price"] = item["discount_price"]
            item["discount_price"] = 0

        my_collection.update_one({"_id": item["_id"]}, {"$set": item})

    return {"message": "Цены на все товары успешно присвоены"}


@app.post("/upload")
async def upload_data(data: UploadFile = File(...)):
    contents = await data.read()
    data_dict = json.loads(contents)
    my_collection.insert_many(data_dict)
    return {"status": "Data uploaded successfully!"}


@app.get("/data_item")
async def get_data(title: str,):
    query = {"title": title}
    projection = {"_id": 0}

    results = my_collection.find(query, projection).limit(20)

    data = []
    for result in results:
        data.append(result)
        print(result)

    return {"data": data}


@app.get("/data_price")
async def get_data_price(min_price: int, max_price: int):
    if min_price >= max_price:
        raise HTTPException(
            status_code=302, detail="Min price should be lower than or equal to max price")

    query = {"leftovers": {"$elemMatch": {
        "price": {"$gte": min_price, "$lte": max_price}}}}
    projection = {"_id": 0}

    results = my_collection.find(query, projection).limit(20)

    data = []
    for result in results:
        data.append(result)
    return {"data": data}


@app.get("/data_brand")
async def get_brands(brand: str | None = None):
    if brand is not None:
        query = {"brand": brand}
    else:
        query = {}
    projection = {"_id": 0}
    results = my_collection.find(query, projection).sort("brand", 1).limit(120)
    brands = []
    for result in results:
        if result["brand"] == "":
            continue
        brands.append(result)
    return {"brands": brands}


@app.get("/data_size")
async def get_data_size(size: str | None = None):
    if size is not None:
        query = {"leftovers": {"size": size}}
    else:
        query = {}
    projection = {"_id": 0}
    results = my_collection.find(query, projection).sort("size", 1).limit(20)
    sizes = []
    for result in results:
        sizes.append(result["size"])
    return {"size": sizes}
