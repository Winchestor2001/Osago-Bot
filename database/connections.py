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


async def get_all_users():
    with db:
        users = Users.select()
        users = [model_to_dict(item) for item in users]
        return users


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


async def add_admin(admin_id, admin_fullname, admin_username):
    with db:
        admin = Admins.create(admin_id=admin_id, admin_username=admin_username, admin_fullname=admin_fullname)
        return model_to_dict(admin)


async def delete_admin(admin_id):
    with db:
        Admins.delete().where(Admins.admin_id == admin_id).execute()


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


async def count_users():
    with db:
        users = Users.select().count()
        yandex = Users.select().where(Users.from_link == 'yandex').count()
        google = Users.select().where(Users.from_link == 'google').count()
        telegram = Users.select().where(Users.from_link == 'telegram').count()
        whatsapp = Users.select().where(Users.from_link == 'whatsapp').count()
        vkontakte = Users.select().where(Users.from_link == 'vkontakte').count()
        friend = Users.select().where(Users.from_link == 'friend').count()
        return users, yandex, google, telegram, whatsapp, vkontakte, friend


async def admin_get_all_products():
    with db:
        products = Products.select()
        products = [model_to_dict(item) for item in products]
        return products
    

async def update_product_price(id: int, price: int):
    with db:
        Products.update(price=price).where(Products.id == id).execute()


async def update_config_price(sequence: int, price: int):
    with db:
        if sequence == 1:
            BotConfigs.update(ref_sum=price).where(BotConfigs.ref_sum == BotConfigs.ref_sum).execute()
        elif sequence == 2:
            BotConfigs.update(min_sum=price).where(BotConfigs.min_sum == BotConfigs.min_sum).execute()


async def add_user_invoice(user_id: int, bill_id: str):
    with db:
        Payments.create(user_id=user_id, bill_id=bill_id)


async def get_user_invoice(bill_id: str):
    with db:
        invoice = Payments.select().where(Payments.bill_id == bill_id)
        invoice = [model_to_dict(item) for item in invoice][0]
        return invoice


async def delete_user_invoice(user_id: int):
    with db:
        Payments.delete().where(Payments.user_id == user_id).execute()
