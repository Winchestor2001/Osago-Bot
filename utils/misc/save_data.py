from playhouse.shortcuts import model_to_dict

from database.models import *


async def save_products_to_db():
    with open('products.txt', 'r', encoding='utf-8') as file:
        for product in file.read().split("\n"):
            product = product.split(":")
            with db:
                Products.create(product_id=product[0], product_slug=product[1], product_name=product[2], product_price=product[3])


async def save_users_to_db():
    with open('users_data.txt', 'r', encoding='utf-8') as file:
        for user in file.read().split("\n"):
            user = user.split(":")
            try:
                with db:
                    Users.create(user_id=user[0], user_balance=user[1], from_link=user[2])
            except:
                continue
