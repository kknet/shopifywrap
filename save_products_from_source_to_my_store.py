"""
This file scans the store and gives the products of a specific collection.
"""
import logging
import itertools
import csv
import shopify
import ssl
import csv
import requests
import pandas
import codecs
import json
import os
import pymongo
import sets
import save_products_in_db
from collections import defaultdict
from Shopify import Shopify
from requests.exceptions import ConnectionError
from copy import deepcopy
from read_shopify import extract_products

ssl._create_default_https_context = ssl._create_unverified_context
shop_url = "https://inshout.myshopify.com/admin"
shopify.ShopifyResource.set_user("587de113912bfa3dd33e5d05950b4ace")
shopify.ShopifyResource.set_password("ca3bfda6ffd75cb48c05b24f3cd25905")
shopify.ShopifyResource.set_site(shop_url)


def get_product(url):
    """
    This function request storefront api and get the json data and populate it accordingly

    :return: list of products
    """
    try:
        resp = requests.get("{}.json".format(url))
        if resp.text:
            product = resp.json()
            if product.get("product"):
                return product['product']
            return []

        print("Something went wrong, Response status code is '{}'".format(resp.status_code))
        return []

    except ConnectionError as e:
        logging.error(e)
        return []
    except Exception as e:
        logging.exception(e)


def edit_variants(variant, prod):
    import requests
    try:
        url = "https://587de113912bfa3dd33e5d05950b4ace:ca3bfda6ffd75cb48c05b24f3cd25905@inshout.myshopify.com/admin/api/2019-04/products/{}/variants/{}.json".format(
            prod.id, variant['id']
        )

        response = requests.request("POST", url, data=json.dumps({
            # "id":variant['id'],
            "title": variant['title'],
            "option1": variant['option1'],
            "option2": variant['option2'],
            "option3": variant['option3'],
            "sku": variant['sku'],
            "requires_shipping": variant['requires_shipping'],
            "taxable": variant['taxable'],
            "featured_image": variant['featured_image'],
            "available": variant['available'],
            "price": variant['price'],
            "grams": variant['grams'],
            "compare_at_price": variant['compare_at_price'],
            "position": variant['position'],
            "inventory_quantity": 1 if variant.get("available") else 0}))
        print(response.status_code)
        print(prod.title)
    except Exception as e:
        logging.exception(e)
        print("errir in delting variants")


def create_variants(variants, product):

    # variants = deepcopy(variants)
    product1 = shopify.Product.find(product.id)
    created_variants = []
    for variant in variants:
        # print(variant)
        # del variant['id']
        # vari = {
        #     "title": variant['title'],
        #     "option1": variant['option1'],
        #     "option2": variant['option2'],
        #     "option3": variant['option3'],
        #     "sku": variant['sku'],
        #     "requires_shipping": variant['requires_shipping'],
        #     "taxable": variant['taxable'],
        #     # "featured_image": variant['featured_image'],
        #     # "available": variant['available'],
        #     "price": variant['price'],
        #     "grams": variant['grams'],
        #     "compare_at_price": variant['compare_at_price'],
        #     "position": variant['position']
        # }
        # edit_variants(variant, product1)
        # for own_variant in product.variants:
        #     own_variant.attributes = vari
        # created_variants.append(shopify.Variant(vari))
        new_variant = shopify.Variant()
        new_variant.title = variant['title']
        new_variant.price = variant['price']
        new_variant.sku = variant['sku']
        new_variant.position = variant['position']
        new_variant.compare_at_price = variant['compare_at_price']
        new_variant.option1 = variant['option1']
        new_variant.option2 = variant['option2']
        new_variant.option3 = variant['option3']
        new_variant.taxable = variant['taxable']
        new_variant.grams = variant['grams']
        new_variant.requires_shipping = variant['requires_shipping']
        new_variant.inventory_policy = "continue"
        new_variant.inventory_quantity = 1
        new_variant.inventory_management = "shopify"
        new_variant.old_inventory_quantity = 1
        new_variant.fulfillment_service = "manual"
        created_variants.append(new_variant)
    product1.variants = []
    product1.variants = created_variants
    # product.variants = []
    save = product1.save()
    if save:
        print(product.title)
    else:
        print("Not Saved")


def create_images(images):
    images = deepcopy(images)
    created_images = []
    for image in images:
        new_image = shopify.Image()
        new_image.position = image['position']
        new_image.width = image['width']
        new_image.height = image['height']
        new_image.src = image['src']
        created_images.append(new_image)
    return created_images


def create_options(options):
    options = deepcopy(options)
    created_options = []
    for option in options:
        new_option = shopify.Option()
        new_option.name = option['name']
        new_option.position = option['position']
        new_option.values = option['values']
        created_options.append(new_option)
    return created_options


def create_product(product):
    try:
        new_product = shopify.Product()
        new_product.title = product['title']
        new_product.body_html = product['body_html']
        new_product.handle = product['handle']
        new_product.product_type = product['product_type']
        new_product.tags = product['tags']
        new_product.variants = create_variants(product['variants'])
        new_product.images = create_images(product['images'])
        new_product.options = create_options(product['options'])
        new_product.vendor = product['vendor']
        save = new_product.save()
        if save:
            print('Saved')
        else:
            print('Not Saved')
    except ConnectionError:
        logging.error("Connection error occurred")
        return False
    except Exception as e:
        logging.exception(e)


def delete_product(product_id):
    try:
        product = shopify.Product.find(product_id)
        if product:
            product.destroy()
            return True
        print("Something went wrong.")
        return False
    except ConnectionError:
        logging.error("Connection error occurred")
        return False
    except Exception as e:
        logging.exception(e)


def get_all_products(resource, **kwargs):
    resource_count = resource.count(**kwargs)
    resources = []
    if resource_count > 0:
        for page in range(1, ((resource_count-1) // 250) + 2):
            kwargs.update({"limit": 250, "page": page})
            resources.extend(resource.find(**kwargs))
    return resources


def check_changes(store_product, source_product):
    if len(store_product['variants']) == len(source_product['variants']):
        for store, source in zip(store_product['variants'], source_product['variants']):
            if (
                    store['taxable'] == source['taxable'] and
                    store['grams'] == source['grams'] and store['requires_shipping'] == source['requires_shipping'] and
                    ((store['inventory_quantity'] <= 0 and source['available'] is False) or
                        (store['inventory_quantity'] >= 1 and source['available'] is True))
            ):
                pass
            else:
                return True
        return False
    else:
        print(store_product['title'], store_product['handle'], store_product['src_name'])
        return False


def update_stock():
    store_products = get_all_products(shopify.Product)
    all_source_products = save_products_in_db.get_source_products()
    shop = Shopify()
    for store_product in store_products:
        for source_products in all_source_products:
            if source_products['handle'] == store_product.handle and check_changes(store_product, source_products):
                shop.update_variant(store_product, source_products)


def update_title():
    shop = Shopify()
    store_products = get_all_products(shopify.Product)
    with open('products_export.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        for line in csv_reader:
            if line[1] != '' and line[0] != 'Handle':
                for product in store_products:
                    if product.handle == line[0]:
                        shop.edit_product_title(product, line[1])


def save_store_products_in_db():
    client = pymongo.MongoClient()
    db = client["inshout_products"]
    store_products = get_all_products(shopify.Product)
    men_fashion_products = []
    women_fashion_products = []
    kids_fashion_products = []
    handles = []
    deeds = save_products_in_db.get_deeds_products()
    blueshoppy = save_products_in_db.get_blueshoppy_products()
    brandsxpress = save_products_in_db.get_brandsxpress_products()
    brandspopper = save_products_in_db.get_brandspopper_products()
    with open('men_fashion.csv') as read_file:
        csv_reader = csv.reader(read_file, delimiter=',')
        prev = ''
        count = 0
        for line in csv_reader:
            if count == 0:
                count += 1
            elif prev != line[7]:
                prev = line[7]
                handle = line[7].split("/products/")
                handles.append(handle[1])
        col1 = db["men-fashion-products"]
        for handle in handles:
            for product in store_products:
                if product.handle == handle:
                    variants = []
                    options = []
                    images = []
                    for variant in product.variants:
                        var = {
                            'id': variant.id,
                            'title': variant.title,
                            'price': variant.price,
                            'sku': variant.sku,
                            'position': variant.position,
                            'compare_at_price': variant.compare_at_price,
                            'option1': variant.option1,
                            'option2': variant.option2,
                            'option3': variant.option3,
                            'taxable': variant.taxable,
                            'grams': variant.grams,
                            'inventory_quantity': variant.inventory_quantity,
                            'old_inventory_quantity': variant.old_inventory_quantity,
                            'requires_shipping': variant.requires_shipping,
                        }
                        variants.append(var)
                    for image in product.images:
                        img = {
                            'id': image.id,
                            'position': image.position,
                            'variant_ids': image.variant_ids,
                            'src': image.src,
                            'width': image.width,
                            'height': image.height
                        }
                        images.append(img)
                    for option in product.options:
                        opt = {
                            'name': option.name,
                            'position': option.position,
                            'values': option.values
                        }
                        options.append(opt)
                    prod = {
                        'id': product.id,
                        'title': product.title,
                        'handle': product.handle,
                        'body_html': product.body_html,
                        'vendor': product.vendor,
                        'product_type': product.product_type,
                        'tags': product.tags,
                        'variants': variants,
                        'images': images,
                        'options': options,
                        'src_name': 'Not Found',
                        'src_handle': 'Not Found',
                        'src_title': 'Not Found'
                    }
                    men_fashion_products.append(prod)
        for product in men_fashion_products:
            for temp in deeds:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'deeds.pk'
                    product['src_title'] = temp['title']
            for temp in blueshoppy:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'blueshoppy.com'
                    product['src_title'] = temp['title']
            for temp in brandsxpress:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'brandsxpress.com'
                    product['src_title'] = temp['title']
            for temp in brandspopper:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'brandspopper.com'
                    product['src_title'] = temp['title']
        for product in men_fashion_products:
            col1.insert_one(product)

    handles.clear()

    with open('women_fashion.csv') as read_file:
        csv_reader = csv.reader(read_file, delimiter=',')
        prev = ''
        count = 0
        for line in csv_reader:
            if count == 0:
                count += 1
            elif prev != line[7]:
                prev = line[7]
                handle = line[7].split("/products/")
                handles.append(handle[1])
        col2 = db["women-fashion-products"]
        for handle in handles:
            for product in store_products:
                if product.handle == handle:
                    variants = []
                    options = []
                    images = []
                    for variant in product.variants:
                        var = {
                            'id': variant.id,
                            'title': variant.title,
                            'price': variant.price,
                            'sku': variant.sku,
                            'position': variant.position,
                            'compare_at_price': variant.compare_at_price,
                            'option1': variant.option1,
                            'option2': variant.option2,
                            'option3': variant.option3,
                            'taxable': variant.taxable,
                            'grams': variant.grams,
                            'inventory_quantity': variant.inventory_quantity,
                            'old_inventory_quantity': variant.old_inventory_quantity,
                            'requires_shipping': variant.requires_shipping,
                        }
                        variants.append(var)
                    for image in product.images:
                        img = {
                            'id': image.id,
                            'position': image.position,
                            'variant_ids': image.variant_ids,
                            'src': image.src,
                            'width': image.width,
                            'height': image.height
                        }
                        images.append(img)
                    for option in product.options:
                        opt = {
                            'name': option.name,
                            'position': option.position,
                            'values': option.values
                        }
                        options.append(opt)
                    prod = {
                        'id': product.id,
                        'title': product.title,
                        'handle': product.handle,
                        'body_html': product.body_html,
                        'vendor': product.vendor,
                        'product_type': product.product_type,
                        'tags': product.tags,
                        'variants': variants,
                        'images': images,
                        'options': options,
                        'src_name': 'Not Found',
                        'src_handle': 'Not Found',
                        'src_title': 'Not Found'
                    }
                    women_fashion_products.append(prod)
        for product in women_fashion_products:
            for temp in deeds:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'deeds.pk'
                    product['src_title'] = temp['title']
            for temp in blueshoppy:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'blueshoppy.com'
                    product['src_title'] = temp['title']
            for temp in brandsxpress:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'brandsxpress.com'
                    product['src_title'] = temp['title']
            for temp in brandspopper:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'brandspopper.com'
                    product['src_title'] = temp['title']
        for product in women_fashion_products:
            col2.insert_one(product)

    handles.clear()

    with open('kids_fashion.csv') as read_file:
        csv_reader = csv.reader(read_file, delimiter=',')
        prev = ''
        count = 0
        for line in csv_reader:
            if count == 0:
                count += 1
            elif prev != line[7]:
                prev = line[7]
                handle = line[7].split("/products/")
                handles.append(handle[1])
        col3 = db["kids-fashion-products"]
        for handle in handles:
            for product in store_products:
                if product.handle == handle:
                    variants = []
                    options = []
                    images = []
                    for variant in product.variants:
                        var = {
                            'id': variant.id,
                            'title': variant.title,
                            'price': variant.price,
                            'sku': variant.sku,
                            'position': variant.position,
                            'compare_at_price': variant.compare_at_price,
                            'option1': variant.option1,
                            'option2': variant.option2,
                            'option3': variant.option3,
                            'taxable': variant.taxable,
                            'grams': variant.grams,
                            'inventory_quantity': variant.inventory_quantity,
                            'old_inventory_quantity': variant.old_inventory_quantity,
                            'requires_shipping': variant.requires_shipping,
                        }
                        variants.append(var)
                    for image in product.images:
                        img = {
                            'id': image.id,
                            'position': image.position,
                            'variant_ids': image.variant_ids,
                            'src': image.src,
                            'width': image.width,
                            'height': image.height
                        }
                        images.append(img)
                    for option in product.options:
                        opt = {
                            'name': option.name,
                            'position': option.position,
                            'values': option.values
                        }
                        options.append(opt)
                    prod = {
                        'id': product.id,
                        'title': product.title,
                        'handle': product.handle,
                        'body_html': product.body_html,
                        'vendor': product.vendor,
                        'product_type': product.product_type,
                        'tags': product.tags,
                        'variants': variants,
                        'images': images,
                        'options': options,
                        'src_name': 'Not Found',
                        'src_handle': 'Not Found',
                        'src_title': 'Not Found'
                    }
                    kids_fashion_products.append(prod)
        for product in kids_fashion_products:
            for temp in deeds:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'deeds.pk'
                    product['src_title'] = temp['title']
            for temp in blueshoppy:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'blueshoppy.com'
                    product['src_title'] = temp['title']
            for temp in brandsxpress:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'brandsxpress.com'
                    product['src_title'] = temp['title']
            for temp in brandspopper:
                if product['handle'] == temp['handle']:
                    product['src_handle'] = temp['handle']
                    product['src_name'] = 'brandspopper.com'
                    product['src_title'] = temp['title']
        for product in kids_fashion_products:
            col3.insert_one(product)


def get_store_products_from_db_by_collection(collection_name):
    client = pymongo.MongoClient()
    db = client["inshout_products"]
    col = db[collection_name]
    store_products = []
    for product in col.find({}, {"_id": 0}):
        store_products.append(product)
    return store_products


def get_store_products_from_db():
    client = pymongo.MongoClient()
    db = client["inshout_products"]
    men = db["men-fashion-products"]
    women = db["women-fashion-products"]
    kids = db["kids-fashion-products"]
    store_products = []
    for product in men.find({}, {"_id": 0}):
        store_products.append(product)
    for product in women.find({}, {"_id": 0}):
        store_products.append(product)
    for product in kids.find({}, {"_id": 0}):
        store_products.append(product)
    return store_products


def export_linked_products():
    men_products = get_store_products_from_db("men-fashion-products")
    women_products = get_store_products_from_db("women-fashion-products")
    kid_products = get_store_products_from_db("kids-fashion-products")
    with open('new-men-fashion.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Source Title', 'Store Title', 'Source URL', 'Store URL', 'Vendor',
                         'Store Price', 'Product Type'])
        for product in men_products:
            writer.writerow([product['src_title'], product['title'],
                            "https://"+product['src_name']+"/products/"+product['src_handle']
                            if product['src_handle'] != 'Not Found'
                            else product['src_handle'],
                            "https://inshout.com/products/"+product['handle'],
                            product['vendor'], product['variants'][0]['price'], product['product_type']])
    with open('new-women-fashion.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Source Title', 'Store Title', 'Source URL', 'Store URL', 'Vendor',
                         'Store Price', 'Product Type'])
        for product in women_products:
            writer.writerow([product['src_title'], product['title'],
                            "https://" + product['src_name'] + "/products/" + product['src_handle']
                            if product['src_handle'] != 'Not Found'
                            else product['src_handle'],
                            "https://inshout.com/products/" + product['handle'],
                            product['vendor'], product['variants'][0]['price'], product['product_type']])
    with open('new-kids-fashion.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Source Title', 'Store Title', 'Source URL', 'Store URL', 'Vendor',
                         'Store Price', 'Product Type'])
        for product in kid_products:
            writer.writerow([product['src_title'], product['title'],
                            "https://" + product['src_name'] + "/products/" + product['src_handle']
                            if product['src_handle'] != 'Not Found'
                            else product['src_handle'],
                            "https://inshout.com/products/" + product['handle'],
                            product['vendor'], product['variants'][0]['price'], product['product_type']])


def old_get_linked_products():
    store_products = get_all_products(shopify.Product)
    handles = []
    with open('women_fashion.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        prev = ''
        count = 0
        for line in csv_reader:
            if count == 0:
                count += 1
            elif prev != line[7]:
                prev = line[7]
                handle = line[7].split("/products/")
                handles.append(handle[1])
    men_fashion = []

    deeds = save_products_in_db.get_deeds_products()
    blueshoppy = save_products_in_db.get_blueshoppy_products()
    brandspopper = save_products_in_db.get_brandspopper_products()
    brandsxpress = save_products_in_db.get_brandsxpress_products()
    with open('new-women-fashion.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Source Title', 'Store Title', 'Source URL', 'Store URL', 'Vendor', 'Source Price',
                         'Store Price', 'Product Type'])
        for handle in handles:
            for store_product in store_products:
                if store_product.handle == handle:
                    var = {
                        'source_title': 'Not Found',
                        'store_title': store_product.title,
                        'source_url': 'Not Found',
                        'store_url': "https://inshout.com/products/"+store_product.handle,
                        'vendor': store_product.vendor,
                        'source_price': 'Not Found',
                        'store_price': store_product.variants[0].price,
                        'product_type': store_product.product_type
                    }
                    men_fashion.append(var)
        for product in men_fashion:
            for deed in deeds:
                store_handle = product['store_url'].split("/products/")
                _handle = store_handle[1]
                if _handle == deed['handle']:
                    product['source_title'] = deed['title']
                    product['source_url'] = "https://deeds.pk/products/"+deed['handle']
                    product['source_price'] = deed['variants'][0]['price']
        for product in men_fashion:
            for blue in blueshoppy:
                store_handle = product['store_url'].split("/products/")
                _handle = store_handle[1]
                if _handle == blue['handle']:
                    product['source_title'] = blue['title']
                    product['source_url'] = "https://blueshoppy.com/products/"+blue['handle']
                    product['source_price'] = blue['variants'][0]['price']
        for product in men_fashion:
            for popper in brandspopper:
                store_handle = product['store_url'].split("/products/")
                _handle = store_handle[1]
                if _handle == popper['handle']:
                    product['source_title'] = popper['title']
                    product['source_url'] = "https://brandspopper.com/products/"+popper['handle']
                    product['source_price'] = popper['variants'][0]['price']
        for product in men_fashion:
            for xpress in brandsxpress:
                store_handle = product['store_url'].split("/products/")
                _handle = store_handle[1]
                if _handle == xpress['handle']:
                    product['source_title'] = xpress['title']
                    product['source_url'] = "https://brandsxpress.com/products/"+xpress['handle']
                    product['source_price'] = xpress['variants'][0]['price']
        for product in men_fashion:
            writer.writerow([product['source_title'], product['store_title'], product['source_url'],
                            product['store_url'], product['vendor'], product['source_price'],
                            product['store_price'], product['product_type']])


def delete_bad_products():
    store_products = get_all_products(shopify.Product)
    shop = Shopify()
    with open('delete_products.csv') as file:
        csv_reader = csv.reader(file, delimiter=',')
        prev = ''
        handles = []
        for line in csv_reader:
            if prev != line[8] and line[7].lower() == 'no':
                handle = line[8].split("/products/")
                handles.append(handle[1])
                prev = line[8]
    for store_product in store_products:
        if store_product.handle in handles:
            shop.delete_product(store_product)


def check_size(option):
    if option and "EXTRA SMALL" in option:
        return "XS"
    elif option and "SMALL" in option:
        return "S"
    elif option and "MEDIUM" in option:
        return "M"
    elif option and "DOUBLE EXTRA LARGE" in option:
        return "2XL"
    elif option and "TRIPLE EXTRA LARGE" in option:
        return "3XL"
    elif option and "FOUR EXTRA LARGE" in option:
        return "4XL"
    elif option and "EXTRA LARGE" in option:
        return "XL"
    elif option and "LARGE" in option:
        return "L"
    elif option and "XXXXL" in option:
        return "4XL"
    elif option and "XXXL" in option:
        return "3XL"
    elif option and "XXL" in option:
        return "2XL"
    elif option and "XXS" in option:
        return "2XS"
    elif option and "MONTHS" in option:
        return option.replace("MONTHS", "M")
    elif option and "YEARS" in option:
        return option.replace("YEARS", "Y")
    elif option and "Months" in option:
        return option.replace("Months", "M")
    elif option and "Years" in option:
        return option.replace("Years", "Y")
    elif option and "MONTH" in option:
        return option.replace("MONTH", "M")
    elif option and "YEAR" in option:
        return option.replace("YEAR", "Y")
    elif option and "Month" in option:
        return option.replace("Month", "M")
    elif option and "Year" in option:
        return option.replace("Year", "Y")
    else:
        return option


def make_tags(mylist, values):
    for value in values:
        if value not in mylist:
            mylist.append(value.lower())
    return mylist


def update_options():
    shop = Shopify()
    store_products = get_all_products(shopify.Product)
    for product in store_products:
        temp = 0
        for variant in product.variants:
            x = check_size(variant.option1)
            y = check_size(variant.option2)
            z = check_size(variant.option3)
            if x != variant.option1 or y != variant.option2 or z != variant.option3:
                variant.option1 = x
                variant.option2 = y
                variant.option3 = z
                temp += 1
        if temp > 0:
            shop.update_variant_titles(product)


def update_tags_with_sizes():
    shop = Shopify()
    store_products = get_all_products(shopify.Product)
    for product in store_products:
        mylist = []
        if type(product.tags) is list:
            for tag in product.tags:
                mylist.append(tag)
        elif ',' in product.tags:
            for tag in product.tags.split(','):
                mylist.append(tag)
        else:
            mylist.append(product.tags)
        product.tags = mylist
        count = 0
        for option in product.options:
            if option.name == "Length":
                if product.tags != make_tags(product.tags, option.values):
                    product.tags = make_tags(product.tags, option.values)
                    count += 1
        if count > 0:
            shop.update_tags(product)


def update_tags():
    shop = Shopify()
    store_products = get_all_products(shopify.Product)
    for product in store_products:
        mylist = []
        if type(product.tags) is list:
            for tag in product.tags:
                tag = tag.replace(' ', '')
                mylist.append(tag.lower())
        elif ',' in product.tags:
            for tag in product.tags.split(','):
                tag = tag.replace(' ', '')
                mylist.append(tag.lower())
        else:
            tags = tags.replace(' ', '')
            mylist.append(product.tags.lower())
        i = 0
        count = 0
        for tag in mylist:
            if 'MONTH' in tag:
                mylist[i] = tag.replace('MONTH', 'm')
                count += 1
            elif 'month' in tag:
                mylist[i] = tag.replace('month', 'm')
                count += 1
            i += 1
        if count > 0:
            product.tags = mylist
            shop.update_tags(product)

        # if product.vendor.lower() not in mylist and product.vendor not in mylist:
        #     mylist.append(product.vendor.lower().replace(' ', '-'))
        # else:
        #     i = 0
        #     for tag in mylist:
        #         if tag == product.vendor.lower() or tag == product.vendor:
        #             mylist[i] = product.vendor.lower().replace(' ', '-')
        #             break
        #         i += 1


def update_vendors_and_titles():
    shop = Shopify()
    store_products = get_all_products(shopify.Product)
    for store in store_products:
        if "' " in store.title:
            store.title = store.title.replace("' ", ' ')
            shop.edit_product_vendor_and_title(store)
    # file = pandas.read_excel('new-kids-fashion.xlsx')
    # store_urls = file['Store URL']
    # titles = file['Store Title']
    # colors = file['Color']
    # for store_url, title, color in zip(store_urls, titles, colors):
    #     for store_product in store_products:
    #         if store_product.handle == store_url.split("/products/")[1]:
    #             if color in store_product.title and store_product.product_type != 'shoes':
    #                 new_title = store_product.title.replace(color, '')
    #                 store_product.title = new_title.replace('  ', ' ')
    #                 shop.edit_product_vendor_and_title(store_product)


def update_variant_images():
    shop = Shopify()
    store_products = get_all_products(shopify.Product)
    source_products = save_products_in_db.get_source_products()
    for store in store_products:
        for source in source_products:
            if store.handle == source['handle'] and store.handle == 'american-eagle-long-sleeves-pique-polo-shirt':
                shop.create_image_of_variants(source, store)


def update_handles():
    shop = Shopify()
    for product in get_store_products_from_db():
        handle = product['title'].lower()
        for option in product['options']:
            if option['name'] == 'Color':
                for value in option['values']:
                    handle = handle + "-{}".format(value.lower())
        handle = handle.replace('   ', '-').replace('  ', '-').replace(' ', '-').replace('/', '-').replace("'", '-')
        handle = handle.replace(',', '-').replace('.', '-').replace('--', '-').replace('+', '')
        # shop.update_handle(product, handle)


def update_variant_by_handle():
    shop = Shopify()
    store_products = get_all_products(shopify.Product)
    source_products = save_products_in_db.get_source_products()
    for product in store_products:
        if product.handle == 'mustang-cotton-stretch-ankle-socks':
            for source in source_products:
                if source['handle'] == 'mustang-cotton-stretch-ankle-socks':
                    shop.create_image_of_variants(source, product)


def create_db_of_all_products():
    client = pymongo.MongoClient()
    db = client["all_inshout_products"]
    col = db["all_products"]
    all_products = []
    store_products = get_all_products(shopify.Product)
    deeds = save_products_in_db.get_deeds_products()
    blueshoppy = save_products_in_db.get_blueshoppy_products()
    brandsxpress = save_products_in_db.get_brandsxpress_products()
    brandspopper = save_products_in_db.get_brandspopper_products()
    for product in store_products:
        variants = []
        images = []
        options = []
        for variant in product.variants:
            var = {
                'id': variant.id,
                'title': variant.title,
                'price': variant.price,
                'sku': variant.sku,
                'position': variant.position,
                'compare_at_price': variant.compare_at_price,
                'option1': variant.option1,
                'option2': variant.option2,
                'option3': variant.option3,
                'taxable': variant.taxable,
                'grams': variant.grams,
                'inventory_quantity': variant.inventory_quantity,
                'old_inventory_quantity': variant.old_inventory_quantity,
                'requires_shipping': variant.requires_shipping,
            }
            variants.append(var)
        for image in product.images:
            img = {
                'id': image.id,
                'position': image.position,
                'variant_ids': image.variant_ids,
                'src': image.src,
                'width': image.width,
                'height': image.height
            }
            images.append(img)
        for option in product.options:
            opt = {
                'name': option.name,
                'position': option.position,
                'values': option.values
            }
            options.append(opt)
        prod = {
            'id': product.id,
            'title': product.title,
            'handle': product.handle,
            'body_html': product.body_html,
            'vendor': product.vendor,
            'product_type': product.product_type,
            'tags': product.tags,
            'variants': variants,
            'images': images,
            'options': options,
            'src_name': 'Not Found',
            'src_handle': 'Not Found',
            'src_title': 'Not Found',
            'src_id': 'Not Found'
        }
        all_products.append(prod)
    for linked_product in all_products:
        for deeds_product in deeds:
            if deeds_product['handle'] == linked_product['handle']:
                linked_product['src_name'] = 'deeds.pk'
                linked_product['src_handle'] = deeds_product['handle']
                linked_product['src_title'] = deeds_product['title']
                linked_product['src_id'] = deeds_product['id']
        for blueshoppy_product in blueshoppy:
            if blueshoppy_product['handle'] == linked_product['handle']:
                linked_product['src_name'] = 'blueshoppy.com'
                linked_product['src_handle'] = blueshoppy_product['handle']
                linked_product['src_title'] = blueshoppy_product['title']
                linked_product['src_id'] = blueshoppy_product['id']
        for brandspopper_product in brandspopper:
            if brandspopper_product['handle'] == linked_product['handle']:
                linked_product['src_name'] = 'brandspopper.com'
                linked_product['src_handle'] = brandspopper_product['handle']
                linked_product['src_title'] = brandspopper_product['title']
                linked_product['src_id'] = brandspopper_product['id']
        for brandsxpress_product in brandsxpress:
            if brandsxpress_product['handle'] == linked_product['handle']:
                linked_product['src_name'] = 'brandsxpress.com'
                linked_product['src_handle'] = brandsxpress_product['handle']
                linked_product['src_title'] = brandsxpress_product['title']
                linked_product['src_id'] = brandsxpress_product['id']
    for product in all_products:
        col.insert_one(product)


def get_all_linked_products():
    client = pymongo.MongoClient()
    db = client["all_inshout_products"]
    col = db["all_products"]
    linked_products = []
    for product in col.find():
        linked_products.append(product)
    return linked_products


if __name__ == '__main__':
    update_tags_with_sizes()
    # for product in get_all_linked_products():
    #     if product['product_type'] != 'shoes'\
    #             and product['product_type'] != 'Shoes' and product['src_id'] == 'Not Found':
    #         print("Title:        " + product['title'])
    #         print("Handle:       " + product['handle'])
