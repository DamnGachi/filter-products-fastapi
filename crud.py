import re
from slugify import slugify
from pymongo import UpdateOne


def update_sku(my_collection):

    my_collection.update_many(
        {"category": {"$in": ["одежда", "обувь", "сумки"]}},
        [
            {
                "$set": {
                    "sku": {
                        "$regexFind": {
                            "input": "$sku",
                            "regex": "\\d+"
                        }
                    }
                },
                "$set": {
                    "leftovers": [{"size": "U", "count": {"$sum": "$leftovers.count"}, "price": "$price"}]
                }
            }

        ]
    )

    return {"message": "Цены и артиклы на все товары успешно присвоены"}


def remove_color_from_category(my_collection):
    my_collection.update_many(
        {"size_table_type": {
            "$in": ["парфюм", "парфюмерия", "Парфюм", "Парфюмерия"]}},
        [{"$set": {
            "color": {
                "$regexFind": {
                    "input": "$color",
                    "regex": "/([^\s\/]+)$/",
                    "options": "i"
                }
            }
        }}]
    )
    my_collection.update_many({}, {"$unset": {"fashion_season": 1,"fashion_collection": 1,"fashion_collection_inner": 1,"manufacture_country": 1}})
    return {"message": "Удалены все цвета из парфюмерии"}


def crud_update_brand(my_collection):
    products = my_collection.find({
        "brand": {"$exists": True},
        "color": {"$exists": True},
        # "size_table_type": {"$ne": "Парфюмерия"},
        # "root_category": {"$ne": "Косметика"},
    }).limit(100)

    for product in products:
        if "slug" not in product["brand"]:
            name = product["brand"]
            if product["color"]:
                color_code, color_name = product["color"].split("/") if "/" in product["color"] else (product["color"], "")
                sku = product["sku"]

                slug = slugify(f"{name} {color_code} {color_name} {sku}")

                my_collection.update_one(
                    {"_id": product["_id"]},
                    {"$set": {"brand": {"name": name, "slug": slug, "color_name": color_name}}}
                )
        else:
            continue
    return {"message": "Бренды успешно обновлены"}



def set_data_price(my_collection):

    items = my_collection.find().limit(100)

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


def get_category_slug(category_name):
    return slugify(category_name)


def update_categories(my_collection):

    categories = my_collection.distinct("root_category")

    for category in categories:
        slug = slugify(category)
        category_entity = {"name": category, "slug": slug}
        my_collection.update_many({"root_category": category}, {
                                  "$set": {"category_entity": category_entity}})

    return {"message": "Categories updated successfully"}
