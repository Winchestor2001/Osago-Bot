from peewee import *
from data.config import DB_NAME, DB_USER, DB_HOST, DB_PASSWORD, DB_PORT

db = PostgresqlDatabase(DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD, port=DB_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    user_id = BigIntegerField(primary_key=True, unique=True)
    username = CharField(max_length=50, null=True)
    full_name = CharField(max_length=155)
    user_balance = FloatField(default=0)
    from_link = CharField(max_length=50)
    referals = IntegerField(default=0)

    class Meta:
        db_name = 'users'


class Channels(BaseModel):
    channel_id = BigIntegerField(primary_key=True)
    channel_name = CharField(max_length=200, null=True)
    channel_url = CharField(max_length=200, null=True)

    class Meta:
        db_name = 'channels'


class BotConfigs(BaseModel):
    ref_sum = FloatField()

    class Meta:
        db_name = 'bot_configs'


class Admins(BaseModel):
    admin_id = BigIntegerField(primary_key=True, unique=True)
    admin_username = CharField(max_length=255)
    admin_fullname = CharField(max_length=300)

    class Meta:
        db_name = 'admins'


models = [Users, Channels, Admins, BotConfigs]
