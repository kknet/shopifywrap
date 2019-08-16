from read_shopify import extract_products
import pymongo


def get_deeds_products():
    # client = pymongo.MongoClient()
    # db = client["deeds_products"]
    # col = db["products"]
    deeds = []
    whole_products = extract_products('deeds.pk')
    for product in whole_products:
        deeds.append(whole_products.get(product))
    # for product in whole_products:
    #     col.insert_one(whole_products.get(product))
    # source_products = []
    # for product in col.find({}, {"_id": 0}):
    #     print("Deeds              "+product['title'], product['id'])
    #     source_products.append(product)
    return deeds


def get_blueshoppy_products():
    # client = pymongo.MongoClient()
    # db = client["blueshoppy_products"]
    # col = db["products"]
    blueshoppy = []
    whole_products = extract_products('blueshoppy.com')
    for product in whole_products:
        blueshoppy.append(whole_products.get(product))
    # for product in whole_products:
    #     col.insert_one(whole_products.get(product))
    # source_products = []
    # for product in col.find({}, {"_id": 0}):
        # print("Blue Shoppy         "+product['title'], product['id'])
        # source_products.append(product)
    return blueshoppy


def get_brandsxpress_products():
    # client = pymongo.MongoClient()
    # db = client["brandsxpress_products"]
    # col = db["products"]
    brandsxpress = []
    whole_products = extract_products('brandsxpress.com')
    for product in whole_products:
        brandsxpress.append(whole_products.get(product))
    # source_products = []
    # for product in col.find({}, {"_id": 0}):
        # print("Brands Xpress         "+product['title'], product['id'])
        # source_products.append(product)
    return brandsxpress


def get_brandspopper_products():
    # client = pymongo.MongoClient()
    # db = client["brandspopper_products"]
    # col = db["products"]
    brandspopper = []
    whole_products = extract_products('brandspopper.com')
    for product in whole_products:
        brandspopper.append(whole_products.get(product))
    # source_products = []
    # for product in col.find({}, {"_id": 0}):
        # print("Brands Popper         "+product['title'], product['id'])
        # source_products.append(product)
    return brandspopper


def get_source_products():
    source_products = []
    deeds_products = extract_products('deeds.pk')
    for deeds_product in deeds_products:
        source_products.append(deeds_products.get(deeds_product))
    blueshoppy_products = extract_products('blueshoppy.com')
    for blueshoppy_product in blueshoppy_products:
        source_products.append(blueshoppy_products.get(blueshoppy_product))
    brandsxpress_products = extract_products('brandsxpress.com')
    for brandsxpress_product in brandsxpress_products:
        source_products.append(brandsxpress_products.get(brandsxpress_product))
    brandspopper_products = extract_products('brandspopper.com')
    for brandspopper_product in brandspopper_products:
        source_products.append(brandspopper_products.get(brandspopper_product))
    return source_products


if __name__ == '__main__':
    get_source_products()
