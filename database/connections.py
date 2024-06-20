from database.models import *
from playhouse.shortcuts import model_to_dict


async def add_user(user_id, full_name, from_link=None, username=None, user_balance=0, referals=0):
    with db:
        if not Users.select().where(Users.user_id == user_id).exists():
            Users.create(user_id=user_id, username=username, full_name=full_name, from_link=from_link,
                         user_balance=user_balance, referals=referals)


async def check_user(user_id: int):
    with db:
        user = Users.select().where(Users.user_id == user_id)
        user = [model_to_dict(item) for item in user]
        if not user:
            return False
        return True


async def get_user_info(user_id: int):
    with db:
        user = Users.select().where(Users.user_id == user_id)
        user = [model_to_dict(item) for item in user]

        return user


async def update_user_balance(user_id: int, value, incriment: bool = None, sett=False, referer: bool = None):
    with db:
        user = Users.select().where(Users.user_id == user_id)
        user = [model_to_dict(item) for item in user]
        balance = value
        if sett:
            Users.update(user_balance=balance).where(Users.user_id == user_id).execute()
            return
        if incriment:
            balance += user[0]['user_balance']
        elif incriment is False:
            balance -= user[0]['user_balance']
        if referer:
            Users.update(user_balance=balance, referals=user[0]['referals'] + 1).where(
                Users.user_id == user_id).execute()
        Users.update(user_balance=abs(balance)).where(Users.user_id == user_id).execute()


async def create_user_history(user_id, order_name, price):
    with db:
        history = UserHistory.create(user_id=user_id, order_name=order_name, price=price)
        return model_to_dict(history)


async def get_user_history(user_id: int):
    with db:
        history = UserHistory.select().where(UserHistory.user_id == user_id).order_by(UserHistory.date.desc())
        history = [model_to_dict(item) for item in history]

        return history


async def clear_user_history(user_id: int):
    with db:
        UserHistory.delete().where(UserHistory.user_id == user_id).execute()


async def get_all_channels():
    with db:
        channels = Channels.select()
        channels = [model_to_dict(item) for item in channels]
        return channels


async def get_all_admins():
    with db:
        admins = Admins.select()
        admins = [model_to_dict(item) for item in admins]
        return admins


async def get_bot_configs():
    with db:
        configs = BotConfigs.select()
        configs = [model_to_dict(item) for item in configs]
        return configs


async def get_all_services():
    with db:
        services = Services.select()
        services = [model_to_dict(item) for item in services]
        return services


async def get_single_service_by_id(service_id):
    with db:
        service = Services.select().where(Services.id == service_id)
        service = [model_to_dict(item) for item in service]
        return service


async def get_product_by_service(service_id):
    with db:
        products = Products.select().where(Products.service == service_id)
        products = [model_to_dict(item) for item in products]
        return products


async def get_product_by_id(product_id):
    with db:
        product = Products.select().where(Products.id == product_id)
        product = [model_to_dict(item) for item in product]
        return product


async def create_order(user_id, product, text: str = ""):
    with db:
        order = Orders.create(user_id=user_id, product=product, text=text)
        return model_to_dict(order)


async def create_photo(order, photo_id):
    with db:
        photo = Photos.create(order=order, photo_id=photo_id)
        return model_to_dict(photo)
