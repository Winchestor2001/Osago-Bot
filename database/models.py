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
    date = TimestampField()

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
    min_sum = FloatField()

    class Meta:
        db_name = 'bot_configs'


class Admins(BaseModel):
    admin_id = BigIntegerField(primary_key=True, unique=True)
    admin_username = CharField(max_length=255)
    admin_fullname = CharField(max_length=300)

    class Meta:
        db_name = 'admins'


class UserHistory(BaseModel):
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    order_name = CharField(max_length=50, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'user_history'


class Payments(BaseModel):
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    bill_id = CharField(max_length=100)

    class Meta:
        db_name = 'payments'


class Services(BaseModel):
    name = CharField(max_length=300)
    text = TextField()
    date = TimestampField()


class Products(BaseModel):
    service = ForeignKeyField(Services, to_field="id", on_delete="CASCADE")
    name = CharField(max_length=255)
    template_text = TextField()
    template_photo = TextField()
    price = FloatField()


class Orders(BaseModel):
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    product = ForeignKeyField(Products, to_field='id', on_delete='CASCADE')
    text = TextField(null=True)
    date = TimestampField()


class Photos(BaseModel):
    order = ForeignKeyField(Orders, to_field='id', on_delete="CASCADE")
    photo_id = CharField(max_length=300)


models = [Users, Channels, Admins, BotConfigs, UserHistory, Payments, Services, Products, Orders, Photos]
