from database.models import *
from playhouse.shortcuts import model_to_dict


async def add_user(user_id, full_name, from_link, username=None, user_balance=0, referals=0):
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
        elif incriment is False:
            balance -= user[0]['user_balance']
        Users.update(user_balance=abs(balance)).where(Users.user_id == user_id).execute()


async def get_all_channels():
    with db:
        channels = Channels.select()
        channels = [model_to_dict(item) for item in channels]
        return channels


async def get_bot_configs():
    with db:
        configs = BotConfigs.select()
        configs = [model_to_dict(item) for item in configs]
        return configs
