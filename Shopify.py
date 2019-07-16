import requests
import logging
import json


class Shopify():
    def __init__(self):
        self.connection_string = "https://587de113912bfa3dd33e5d05950b4ace:ca3bfda6ffd75cb48c05b24f3cd25905@inshout.myshopify.com/admin/api/2019-04/"

    def get_product(self, product_id):
        try:
            product = requests.get(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product_id))
            return product.json()['product']

        except Exception as e:
            logging.exception(e)
            logging.info("Product not found")

    def get_all_store_products(self):
        try:
            products = requests.get(
                "{connection_string}/products.json".format(connection_string=self.connection_string))
            return products.json()['products']

        except Exception as e:
            logging.exception(e)
            logging.info("Products not found")

    def get_product_all_variants(self, product_id):
        try:
            product = requests.get(
                "{connection_string}/products/{product_id}/variants.json".format(
                    connection_string=self.connection_string,
                    product_id=product_id))
            return product.json()['variants']

        except Exception as e:
            logging.exception(e)
            logging.info("Product not found")

    def get_variant(self, variant_id):
        try:
            product = requests.get(
                "{connection_string}/variants/{variant_id}.json".format(connection_string=self.connection_string,
                                                                        variant_id=variant_id))
            return product.json()['variant']

        except Exception as e:
            logging.exception(e)
            logging.info("Product not found")

    # def edit_variant(self, variants, updated_variants):
    #     i = 0
    #     for variant in variants:
    #         vari = {
    #             'id': updated_variants[i]['id'],
    #             'product_id': updated_variants[i]['product_id'],
    #             'title': updated_variants[i]['title'],
    #             'price': updated_variants[i]['price'],
    #             'sku': updated_variants[i]['sku'],
    #             'position': updated_variants[i]['position'],
    #             'compare_at_price': updated_variants[i]['compare_at_price'],
    #             'option1': updated_variants[i]['option1'],
    #             'option2': updated_variants[i]['option2'],
    #             'option3': updated_variants[i]['option3'],
    #             'taxable': updated_variants[i]['taxable'],
    #             'grams': updated_variants[i]['grams'],
    #             'inventory_quantity': 1 if updated_variants[i]['available'] else 0,
    #             'old_inventory_quantity': 0,
    #             'requires_shipping': updated_variants[i]['requires_shipping'],
    #         }
    #         try:
    #             res = requests.put(
    #                 "{connection_string}/variants/{variant_id}.json".format(connection_string=self.connection_string,
    #                                                                         variant_id=variant['id']),
    #                 data=json.dumps({"variant": vari}),
    #                 headers={'content-type': 'Application/json'}
    #             )
    #
    #         except Exception as e:
    #             logging.exception(e)
    #             logging.info("Variant not found")
    #         i = i + 1
    def edit_variant(self, product_to_be_updated, product):
        variants = []
        for variant in product['variants']:
            vari = {
                'product_id': variant['product_id'],
                'title': variant['title'],
                'price': str(float(variant['price']) * 1.7),
                'sku': variant['sku'],
                'position': variant['position'],
                'compare_at_price': None,
                'option1': variant['option1'],
                'option2': variant['option2'],
                'option3': variant['option3'],
                'taxable': variant['taxable'],
                'grams': variant['grams'],
                'inventory_quantity': 1 if variant['available'] else 0,
                'old_inventory_quantity': 0,
                'requires_shipping': variant['requires_shipping'],
            }
            variants.append(vari)
        options = []
        for option in product['options']:
            opt = {
                'name': option['name'],
                'values': option['values'],
                'position': option['position']
            }
            options.append(opt)
        data = {
            "id": product_to_be_updated['id'],
            "handle": product['handle'],
            "variants": variants,
            "options": options
        }
        try:
            res = requests.put(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product_to_be_updated['id']),
                data=json.dumps({"product": data}),
                headers={'content-type': 'Application/json'}
            )
            if res.status_code == 200 or 201:
                print(product_to_be_updated['title'])

        except Exception as e:
            logging.exception(e)
            logging.info("Variant not found")

    def edit_product(self, product):
        new_title = product['title'].replace("-", " ")
        data = {
            "id": product['id'],
            "title": new_title
        }
        try:
            res = requests.put(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product['id']),
                data=json.dumps({"product": data}),
                headers={'content-type': 'Application/json'}
            )
            if res.text:
                print(product['title'])

        except Exception as e:
            logging.exception(e)
            logging.info("Product not found")

    def create_variant(self, product, variants_to_be_created):
        for variant in variants_to_be_created:
            vari = {
                'title': variant['title'],
                'price': variant['price'],
                'sku': variant['sku'],
                'position': variant['position'],
                'compare_at_price': variant['compare_at_price'],
                'option1': variant['option1'],
                # 'option2': variant['option2'],
                # 'option3': variant['option3'],
                'taxable': variant['taxable'],
                'grams': variant['grams'],
                'inventory_quantity': 1 if variant['available'] else 0,
                'old_inventory_quantity': 0,
                'requires_shipping': variant['requires_shipping'],
            }
            # vari['option1'] = variant['option1'] if variant.get('option1') else print('None')
            try:
                res = requests.post(
                    "{connection_string}/products/{product_id}/variants.json".format(
                        connection_string=self.connection_string,
                        product_id=product['id']),
                    data=json.dumps({"variant": vari}),
                    headers={'content-type': 'Application/json'}
                )
                print('asd')
                # options = {}
                # options['id'] = res.json()['variant']['id']
                # if variant.get('option3'):
                #     options['option3'] = variant['option3']
                # if variant.get('option2'):
                #     options['option2'] = variant['option2']
                #
                # option_res = requests.put(
                #     "{connection_string}/variants/{variant_id}.json".format(
                #         connection_string=self.connection_string,
                #         variant_id=res.json()['variant']['id']),
                #     data=json.dumps({"variant": options}),
                #     headers={'content-type': 'Application/json'}
                # )
                # print('asd')

            except Exception as e:
                logging.exception(e)
                logging.info("Variant not found")

    def get_product_all_images(self, product_id):
        try:
            product = requests.get(
                "{connection_string}/products/{product_id}/images.json".format(connection_string=self.connection_string,
                                                                               product_id=product_id))
            return product.json()['images']

        except Exception as e:
            logging.exception(e)
            logging.info("Product not found")

    def delete_variant(self, product):
        for variant in product['variants']:
            try:
                response = requests.delete(
                    "{connection_string}/products/{product_id}/variants/{variant_id}.json".format(
                        connection_string=self.connection_string,
                        product_id=product['id'], variant_id=variant['id']))
            except Exception as e:
                logging.exception(e)
                logging.info("Product not found")


if __name__ == '__main__':
    shop = Shopify()
    all_products = shop.get_all_store_products()
    print(all_products)
    # product = shop.get_product("3659372068944")
    # updated_variant = {
    #     'id': 28695680514206,
    #     'product_id': 3659372068944,
    #     'title': 'S / Cream',
    #     'price': '799.00',
    #     'sku': '8946 L-946.1018-00040',
    #     'position': 2,
    #     'inventory_policy': 'deny',
    #     'compare_at_price': None,
    #     'fulfillment_service': 'manual',
    #     'inventory_management': 'shopify',
    #     'option1': 'S',
    #     'option2': 'Cream',
    #     'option3': None,
    #     'created_at': '2019-07-09T21:07:00+05:00',
    #     'updated_at': '2019-07-09T21:07:00+05:00',
    #     'taxable': False,
    #     'barcode': '',
    #     'grams': 275,
    #     'image_id': None,
    #     'weight': 275.0,
    #     'weight_unit': 'g',
    #     'inventory_item_id': 29642944413776,
    #     'inventory_quantity': 1,
    #     'old_inventory_quantity': 0,
    #     'requires_shipping': True,
    #     'admin_graphql_api_id': 'gid://shopify/ProductVariant/28695680516176'
    # }
    # print(shop.edit_variant("28695680514206", updated_variant))
    # print(shop.get_product_all_variants("3659372068944"))
    # print(shop.get_product_all_images("3659372068944"))
