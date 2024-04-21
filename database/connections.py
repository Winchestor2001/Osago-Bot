import datetime
import random

from playhouse.shortcuts import model_to_dict

from data.config import ADMINS
from .models import *
import loader
from aiogram.types import MediaGroup, InputFile


async def add_user(user_id: int, from_link: str, username):
    with db:
        Users.create(user_id=user_id, from_link=from_link, username=username)


async def check_user(user_id: int):
    with db:
        user = Users.select().where(Users.user_id == user_id)
        user = [model_to_dict(item) for item in user]
        if len(user) == 0:
            return True
        else:
            return False


async def get_user_info(user_id: int):
    with db:
        user = Users.select().where(Users.user_id == user_id)
        user = [model_to_dict(item) for item in user]

        return user


async def get_ref_sum():
    with db:
        ref_sum = BotConfigs.select()
        ref_sum = [model_to_dict(item) for item in ref_sum]
        return ref_sum[0]


async def update_ref_sum(ref_sum):
    with db:
        BotConfigs.update(ref_sum=ref_sum).execute()


async def save_unique_link(link, name):
    with db:
        UniqueReferalLinks.create(referal_id=link, referer=name)


async def get_unique_link(unique_id):
    with db:
        referer = UniqueReferalLinks.select().where(
            (UniqueReferalLinks.referal_id == unique_id) | (UniqueReferalLinks.referer == unique_id))
        referer = [model_to_dict(item) for item in referer]
        return referer


async def update_unique_referal(unique_id):
    with db:
        ref = UniqueReferalLinks.select().where(UniqueReferalLinks.referal_id == unique_id)
        ref = [model_to_dict(item) for item in ref]
        UniqueReferalLinks.update(referals=ref[0]['referals'] + 1).where(UniqueReferalLinks.referal_id == unique_id).execute()


async def update_user_balance(user_id: int, value, incriment: bool = None, sett=False):
    with db:
        user = Users.select().where(Users.user_id == user_id)
        user = [model_to_dict(item) for item in user]
        balance = value
        if sett:
            Users.update(user_balance=balance).where(Users.user_id == user_id).execute()
            return
        if incriment:
            balance += user[0]['user_balance']
        else:
            balance -= user[0]['user_balance']
        Users.update(user_balance=abs(balance)).where(Users.user_id == user_id).execute()


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


async def get_user_history(user_id: int):
    with db:
        history = UserHistory.select().where(UserHistory.user_id == user_id).order_by(UserHistory.date.desc())
        history = [model_to_dict(item) for item in history]

        return history


async def clear_user_history(user_id: int):
    with db:
        UserHistory.delete().where(UserHistory.user_id == user_id).execute()


async def get_products(product: str, **kwargs):
    with db:
        if kwargs:
            products = Products.select().where(
                (Products.product_id == product) & (Products.product_slug == kwargs['slug']))
        else:
            products = Products.select().where(Products.product_id == product)
        products = [model_to_dict(item) for item in products]

        return products


async def admin_get_all_products():
    with db:
        products = Products.select()
        products = [model_to_dict(item) for item in products]
        return products


async def edited_product_price(slug: str, price: int):
    with db:
        Products.update(product_price=price).where(Products.product_slug == slug).execute()


async def get_all_admins():
    admins = Admins.select()
    admins = [model_to_dict(item) for item in admins]
    all_admins = []
    for admin in admins:
        all_admins.append(admin['admin_id'])
    all_admins.extend(ADMINS)

    return all_admins


async def save_user_product(user_id: int, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        ProductsPhotoQuestionnaire.create(order_id=order_id, user_id=user_id, product_name=data['product'],
                                          user_data_photo=data['photos'], product_price=data['price'])


async def save_osago_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        OsagoData.create(order_id=order_id, user_id=user_id, user_data=context, product_name=data['product'],
                         price=data['price'])


async def save_dogovor_kupli_prodazhi_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        DkbData.create(order_id=order_id, user_id=user_id, user_data=context, product_name=data['product'],
                       price=data['price'])


async def save_snyatie_ts_s_ucheta_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        SnyatieTSUchotaData.create(order_id=order_id, user_id=user_id, user_data=context, product_name=data['product'],
                                   price=data['price'])


async def save_vosstanovlenie_kbm_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        VosstanovlenieKBMData.create(order_id=order_id, user_id=user_id, user_data=context,
                                     product_name=data['product'],
                                     price=data['price'])


async def save_dk_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        DkData.create(order_id=order_id, user_id=user_id, user_data=context, product_name=data['product'],
                      price=data['price'], photos=data['photos'])


async def save_auto_med_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        AutoMedData.create(order_id=order_id, user_id=user_id, user_data=context, product_name=data['product'],
                           price=data['price'])


async def save_karta_gibdd_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        KartaGibddData.create(order_id=order_id, user_id=user_id, gos_nomer=context, product_name=data['product'],
                              price=data['price'])


async def save_search_solary_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        SearchSolaryData.create(order_id=order_id, user_id=user_id, user_data=context, product_name=data['product'],
                                price=data['price'])


async def save_kasko_bank_data(user_id: int, context: str, data: dict):
    order_id = random.randint(199, 9999)
    with db:
        KaskoBankData.create(order_id=order_id, user_id=user_id, user_data=context, product_name=data['product'],
                             price=data['price'])


async def save_user_orders(user_id, order_name, price):
    with db:
        history = UserHistory.select().where(UserHistory.user_id == user_id).order_by(UserHistory.date.desc())
        history = [model_to_dict(item) for item in history]
        counter = 0
        for item in history:
            if counter < 15:
                counter += 1
            else:
                UserHistory.delete().where(UserHistory.date == item['date']).execute()
        UserHistory.create(user_id=user_id, order_name=order_name, price=price)


async def send_orders_to_admins():
    with db:
        ordering_products = ProductsPhotoQuestionnaire.select()
        ordering_products = [model_to_dict(item) for item in ordering_products]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)
        for order in ordering_products:
            await save_user_orders(user_id=order['user_id']['user_id'], order_name=order['product_name'],
                                   price=order['product_price'])
            media = MediaGroup()
            photos = order['user_data_photo'].replace('[', '').replace(']', '').replace("'", "").replace(" ", "").split(
                ',')
            client_link = f"<a href='tg://user?id={order['user_id']['user_id']}'>Клиент ЛС</a>"
            if len(photos) != 1:
                media.attach_photo(photo=photos[0],
                                   caption=f"{client_link}\n\n<b>Услуга:</b> {order['product_name']} - {order['product_price']}руб.\n<b>Клиент:</b> <code>{order['user_id']['user_id']}</code>")
                for pic in photos[1:]:
                    media.attach_photo(photo=pic)

                try:
                    for admin in all_admins:
                        await loader.bot.send_media_group(chat_id=admin, media=media)
                except:
                    continue
                media.clean()
            else:
                for admin in all_admins:
                    try:
                        await loader.bot.send_photo(chat_id=admin, photo=photos[0],
                                                    caption=f"{client_link}\n\nУслуга: {order['product_name']} - {order['product_price']}руб.\nКлиент: <code>{order['user_id']['user_id']}</code>")
                    except:
                        continue

        ProductsPhotoQuestionnaire.delete().execute()


async def send_osago_data_to_admins():
    with db:
        data = OsagoData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    await loader.bot.send_message(chat_id=admin,
                                                  text=f"{client_link}\n\n<b>Данные:</b>\n{item['user_data']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                except:
                    continue

        OsagoData.delete().execute()


async def send_dogovor_kupli_prodazhi_data_to_admins():
    with db:
        data = DkbData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    await loader.bot.send_message(chat_id=admin,
                                                  text=f"{client_link}\n\n<b>Данные:</b>\n{item['user_data']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                except:
                    continue

        DkbData.delete().execute()


async def send_snyatie_ts_s_ucheta_data_to_admins():
    with db:
        data = SnyatieTSUchotaData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    await loader.bot.send_message(chat_id=admin,
                                                  text=f"{client_link}\n\n<b>Данные:</b>\n{item['user_data']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                except:
                    continue

        SnyatieTSUchotaData.delete().execute()


async def send_vosstanovlenie_kbm_data_to_admins():
    with db:
        data = VosstanovlenieKBMData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    await loader.bot.send_message(chat_id=admin,
                                                  text=f"{client_link}\n\n<b>Данные:</b>\n{item['user_data']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                except:
                    continue

        VosstanovlenieKBMData.delete().execute()


async def send_dk_data_to_admins():
    with db:
        data = DkData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    media = MediaGroup()
                    photos = item['photos'].replace('[', '').replace(']', '').replace("'", "").replace(" ",
                                                                                                                "").split(
                        ',')
                    media.attach_photo(photo=photos[0],
                                       caption=f"{client_link}\n\n<b>Данные:</b>\n{item['user_data']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                    for pic in photos[1:]:
                        media.attach_photo(photo=pic)

                    await loader.bot.send_media_group(chat_id=admin, media=media)
                    media.clean()
                except:
                    continue

        DkData.delete().execute()


async def send_auto_med_data_to_admins():
    with db:
        data = AutoMedData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    await loader.bot.send_message(chat_id=admin,
                                                  text=f"{client_link}\n\n<b>Данные:</b>\n{item['user_data']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                except:
                    continue

        AutoMedData.delete().execute()


async def send_karta_gibdd_data_to_admins():
    with db:
        data = KartaGibddData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    await loader.bot.send_message(chat_id=admin,
                                                  text=f"{client_link}\n\n<b>Данные:</b>\n{item['gos_nomer']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                except:
                    continue

        KartaGibddData.delete().execute()


async def send_search_solary_data_to_admins():
    with db:
        data = SearchSolaryData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    await loader.bot.send_message(chat_id=admin,
                                                  text=f"{client_link}\n\n<b>Данные:</b>\n{item['user_data']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                except:
                    continue

        SearchSolaryData.delete().execute()


async def send_kasko_bank_data_to_admins():
    with db:
        data = KaskoBankData.select()
        data = [model_to_dict(item) for item in data]
        admins = Admins.select()
        all_admins = []
        for admin in admins:
            all_admins.append(admin)
        all_admins.extend(ADMINS)

        for item in data:
            await save_user_orders(user_id=item['user_id']['user_id'], order_name=item['product_name'],
                                   price=item['price'])
            client_link = f"<a href='tg://user?id={item['user_id']['user_id']}'>Клиент ЛС</a>"
            for admin in all_admins:
                try:
                    await loader.bot.send_message(chat_id=admin,
                                                  text=f"{client_link}\n\n<b>Данные:</b>\n{item['user_data']}\n\n<b>Услуга:</b> {item['product_name']} - {item['price']}руб.\n<b>Клиент:</b> <code>{item['user_id']['user_id']}</code>")
                except:
                    continue

        KaskoBankData.delete().execute()


async def save_user_invoice(user_id: int, bill: str):
    with db:
        if Payments.select().where(Payments.user_id == user_id).exists():
            Payments.delete().where(Payments.user_id == user_id).execute()
        Payments.create(user_id=user_id, bill_id=bill)


async def get_all_bot_configs():
    with db:
        qiwi = QiwiConfig.select()
        qiwi = [model_to_dict(item) for item in qiwi]

        return qiwi


async def get_all_users_payments():
    with db:
        payments = Payments.select()
        payments = [model_to_dict(item) for item in payments]

        return payments


async def delete_user_payment_bill(bill_id):
    with db:
        Payments.delete().where(Payments.bill_id == bill_id).execute()


async def delete_user_payment_by_id(user_id):
    with db:
        Payments.delete().where(Payments.user_id == user_id).execute()


async def update_qiwi_token(qiwi_token: str):
    with db:
        QiwiConfig.update(qiwi_token=qiwi_token).execute()


async def get_all_users_for_mailing():
    with db:
        users = Users.select()
        users = [model_to_dict(item) for item in users]

        return users


async def add_admin(admin_id: int):
    try:
        with db:
            Admins.create(admin_id=admin_id)
    except:
        pass


async def del_admin(admin_id: int):
    with db:
        Admins.delete().where(Admins.admin_id == admin_id).execute()
