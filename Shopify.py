import requests
import logging
import json


class Shopify():
    def __init__(self):
        self.connection_string = \
            "https://587de113912bfa3dd33e5d05950b4ace:ca3bfda6ffd75cb48c05b24f3cd25905@inshout.myshopify.com/admin/api/2019-07/"

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
            # image_id = variant['image_id']
            # for image in product['images']:
            #     if image['id'] == image_id:
            #         img = {
            #             'width': image['width'],
            #             'height': image['height'],
            #             'src': image['src']
            #         }
            #         image_res = requests.post(
            #             "{connection_string}/products/{product_id}/images.json".format(
            #                 connection_string=self.connection_string,
            #                 product_id=product_to_be_updated['id']),
            #             data=json.dumps({"image": img}),
            #             headers={'content-type': 'Application/json'}
            #         )
            #         if image_res == 200 or 201:
            #             print(product_to_be_updated['title'])
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
            "id": product_to_be_updated.id,
            "variants": variants,
            "options": options
        }
        try:
            res = requests.put(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product_to_be_updated.id),
                data=json.dumps({"product": data}),
                headers={'content-type': 'Application/json'}
            )
            if res.status_code == 200 or 201:
                print(product_to_be_updated.title)

        except Exception as e:
            logging.exception(e)
            logging.info("Variant not found")

    def update_variant(self, product_to_be_updated, product):
        i = 0
        for variant in product['variants']:
            to_be_updated = product_to_be_updated['variants'][i]
            invent_qt = 0
            if variant['available']:
                if to_be_updated['inventory_quantity'] > 0:
                    pass
                else:
                    invent_qt += 1
            else:
                if to_be_updated['inventory_quantity'] > 0:
                    invent_qt -= 1
            vari = {
                'price': str(float(variant['price']) * 1.7),
                'compare_at_price': None,
                'taxable': variant['taxable'],
                'grams': variant['grams'],
                'inventory_quantity': invent_qt,
                'old_inventory_quantity': 0,
                'requires_shipping': variant['requires_shipping'],
            }
            try:
                res = requests.put(
                    "{connection_string}/variants/{variant_id}.json".format(connection_string=self.connection_string,
                                                                            variant_id=to_be_updated['id']),
                    data=json.dumps({"variant": vari}),
                    headers={'content-type': 'Application/json'}
                )
            except Exception as e:
                logging.exception(e)
                logging.info("Variant not found")
            i = i + 1

    def edit_product_title(self, product, title):
        data = {
            "id": product.id,
            "title": title
        }
        try:
            res = requests.put(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product.id),
                data=json.dumps({"product": data}),
                headers={'content-type': 'Application/json'}
            )
            if res.status_code == 200 or 201:
                print(product.title+"             "+product.handle)

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

    def create_order_webhook(self):
        data = {
            'topic': 'orders/create',
            'address': 'https://order-details.free.beeceptor.com',
            'format': 'json'
        }
        try:
            res = requests.post(
                "{connection_string}/webhooks.json".format(connection_string=self.connection_string),
                data=json.dumps({"webhook": data}),
                headers={'content-type': 'Application/json'}
            )
            if res.status_code == 201:
                print("Webhook created")
            else:
                print("Webhook not created")
        except Exception as e:
            logging.exception(e)
            logging.info("Something went wrong")

    def get_all_webhooks(self):
        try:
            res = requests.get(
                "{connection_string}/webhooks.json".format(connection_string=self.connection_string),
                headers={'content-type': 'Application/json'}
            )
            if res.status_code == 200:
                json_data = res.json()
                print(json_data)
        except Exception as e:
            logging.exception(e)
            logging.info("Something went wrong")

    def delete_product(self, product):
        try:
            res = requests.delete(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product.id))
            if res.status_code == 200:
                print(product.title)

        except Exception as e:
            logging.exception(e)
            logging.info("Product not found")

    def update_variant_titles(self, product):
        print(product.title)
        for variant in product.variants:
            vari = {
                'id': variant.id,
                'option1': variant.option1,
                'option2': variant.option2,
                'option3': variant.option3
            }
            try:
                res = requests.put(
                    "{connection_string}/variants/{variant_id}.json".format(
                        connection_string=self.connection_string,
                        variant_id=variant.id),
                    data=json.dumps({"variant": vari}),
                    headers={'content-type': 'Application/json'}
                )
            except Exception as e:
                logging.exception(e)
                logging.info("Variant not found")

    def update_tags(self, product):
        data = {
            'tags': product.tags
        }
        try:
            res = requests.put(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product.id),
                data=json.dumps({"product": data}),
                headers={'content-type': 'Application/json'}
            )
            print(product.title)
        except Exception as e:
            logging.exception(e)
            logging.info("Not Updated")

    def edit_product_vendor_and_title(self, product):
        data = {
            "id": product.id,
            "title": product.title
        }
        try:
            res = requests.put(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product.id),
                data=json.dumps({"product": data}),
                headers={'content-type': 'Application/json'}
            )
            if res.status_code == 200 or 201:
                print(product.title)

        except Exception as e:
            logging.exception(e)
            logging.info("Product not found")

    def create_image_of_variants(self, source_product, store_product):
        if len(source_product['variants']) == len(store_product.variants):
            for image in source_product['images']:
                if image['variant_ids']:
                    source_url = image['src']
                    store_ids = []
                    for _id in image['variant_ids']:
                        for source, store in zip(source_product['variants'], store_product.variants):
                            if _id == source['id'] and store.image_id is None:
                                store_ids.append(store.id)
                    if store_ids:
                        data = {
                            'variant_ids': store_ids,
                            'src': source_url
                        }
                        res = requests.post(
                            "{connection_string}/products/{product_id}/images.json".format(
                                connection_string=self.connection_string,
                                product_id=store_product.id),
                            data=json.dumps({"image": data}),
                            headers={'content-type': 'Application/json'}
                        )
                        if res == 200 or 201:
                            print(store_product.title)

    def update_handle(self, product, handle):
        data = {
            'handle': handle
        }
        try:
            res = requests.put(
                "{connection_string}/products/{product_id}.json".format(connection_string=self.connection_string,
                                                                        product_id=product['id']),
                data=json.dumps({"product": data}),
                headers={'content-type': 'Application/json'}
            )
            print(product['title'])
        except Exception as e:
            logging.exception(e)
            logging.info("Not Updated")


if __name__ == '__main__':
    shop = Shopify()
    all_products = shop.get_all_store_products()
    print(all_products)
