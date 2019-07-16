"""
This file scans the store and gives the products of a specific collection.
"""
import logging
import shopify
import ssl
import csv
import requests
import codecs
import json
import os
import pymongo
import sets
from save_products_in_db import get_source_products, get_own_store_products
from collections import defaultdict
from Shopify import Shopify
from requests.exceptions import ConnectionError
from copy import deepcopy
from read_shopify import extract_products

ssl._create_default_https_context = ssl._create_unverified_context
shop_url = "https://waseiim.myshopify.com/admin"
shopify.ShopifyResource.set_user("f3c44baad6a307255f78b24cd24b92ea")
shopify.ShopifyResource.set_password("472cb2503a0226df3f31751bc7720261")
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


if __name__ == '__main__':

    all_source_products = get_source_products()
    store_products = get_own_store_products()
    shop = Shopify()
    for source_products in all_source_products:
        for store_product in store_products:
            if store_product['handle'] == source_products['handle']:
                shop.edit_variant(store_product, source_products)

    # own_store_products = get_all_products(shopify.Product)
    # for own_product in own_store_products:
    #     for source_product in all_source_products:
    #         if own_product.handle == source_product['handle']:
    #             create_variants(source_product['variants'], own_product)
    #             break
