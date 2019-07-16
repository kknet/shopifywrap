from read_shopify import extract_products
import pymongo


def get_deeds_products():
    client = pymongo.MongoClient()
    db = client["deeds_products"]
    col = db["products"]
    # whole_products = extract_products('deeds.pk')
    # for product in whole_products:
    #     col.insert_one(whole_products.get(product))
    source_products = []
    for product in col.find({}, {"_id": 0}):
        # print("Deeds              "+product['title'], product['id'])
        source_products.append(product)
    return source_products


def get_blueshoppy_products():
    client = pymongo.MongoClient()
    db = client["blueshoppy_products"]
    col = db["products"]
    # whole_products = extract_products('blueshoppy.com')
    # for product in whole_products:
    #     col.insert_one(whole_products.get(product))
    source_products = []
    for product in col.find({}, {"_id": 0}):
        # print("Blue Shoppy         "+product['title'], product['id'])
        source_products.append(product)
    return source_products


def get_brandsxpress_products():
    client = pymongo.MongoClient()
    db = client["brandsxpress_products"]
    col = db["products"]
    # whole_products = extract_products('brandsxpress.com')
    # for product in whole_products:
    #     col.insert_one(whole_products.get(product))
    source_products = []
    for product in col.find({}, {"_id": 0}):
        # print("Brands Xpress         "+product['title'], product['id'])
        source_products.append(product)
    return source_products


def get_brandspopper_products():
    client = pymongo.MongoClient()
    db = client["brandspopper_products"]
    col = db["products"]
    # whole_products = extract_products('brandspopper.com')
    # for product in whole_products:
    #     col.insert_one(whole_products.get(product))
    source_products = []
    for product in col.find({}, {"_id": 0}):
        # print("Brands Popper         "+product['title'], product['id'])
        source_products.append(product)
    return source_products


def get_source_products():
    # client = pymongo.MongoClient()
    # db = client["all_source_products"]
    # col = db["products"]
    source_products = []
    # for product in col.find({}, {"_id": 0}):
    #     source_products.append(product)
    for product in get_brandspopper_products():
        source_products.append(product)
    for product in get_brandsxpress_products():
        source_products.append(product)
    for product in get_blueshoppy_products():
        source_products.append(product)
    for product in get_deeds_products():
        source_products.append(product)
    # for product in source_products:
    #     print(product['title'])
    #     col.insert_one(product)
    return source_products


def get_own_store_products():
    client = pymongo.MongoClient()
    db = client["own_store_products_list"]
    col = db["inshout-products"]
    inshout_products = []
    for product in col.find({}, {"_id": 0}):
        inshout_products.append(product)
    return inshout_products
    # whole_products = extract_products('inshout.com')
    # for product in whole_products:
    #     col.insert_one(whole_products.get(product))


if __name__ == '__main__':

    get_own_store_products()
    # sources = get_source_products()
    # for product in sources:
    #     print(product['title'])
    # for product in sources:
    #     print(product['title'])
    # count = 0
    # for product in sources:
    #     for product1 in sources:
    #         if product['title'] == product1['title'] and product['id'] != product1['id']:
    #             count = count + 1
    #             print(product['title'])
    # print(count)
    # get_own_store_products()
