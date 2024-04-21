from peewee import *
from data.config import DB_NAME, DB_USER, DB_HOST, DB_PASSWORD, DB_PORT

db = PostgresqlDatabase(DB_NAME, user=DB_USER, host=DB_HOST, password=DB_PASSWORD, port=DB_PORT)


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    user_id = BigIntegerField(primary_key=True, unique=True)
    username = CharField(max_length=50, null=True)
    user_balance = FloatField(default=0)
    from_link = CharField(max_length=50)
    referals = IntegerField(default=0)

    class Meta:
        db_name = 'users'


class BotConfigs(BaseModel):
    ref_sum = FloatField()

    class Meta:
        db_name = 'bot_configs'


class Payments(BaseModel):
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    bill_id = CharField(max_length=100)

    class Meta:
        db_name = 'payments'


class Admins(BaseModel):
    admin_id = BigIntegerField(primary_key=True, unique=True)

    class Meta:
        db_name = 'admins'


class UserHistory(BaseModel):
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    order_name = CharField(max_length=50, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'user_history'


class OsagoData(BaseModel):
    order_id = IntegerField(primary_key=True, unique=True)
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    user_data = TextField()
    product_name = CharField(max_length=150, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'osago_data'


class VosstanovlenieKBMData(BaseModel):
    order_id = IntegerField(primary_key=True, unique=True)
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    user_data = TextField()
    product_name = CharField(max_length=150, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'vosstanovlenie_kbm_data'


class DkbData(BaseModel):
    order_id = IntegerField(primary_key=True, unique=True)
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    user_data = TextField()
    product_name = CharField(max_length=150, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'dkb_data'


class SnyatieTSUchotaData(BaseModel):
    order_id = IntegerField(primary_key=True, unique=True)
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    user_data = TextField()
    product_name = CharField(max_length=150, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'snyatie_ts_uchota_data'


class DkData(BaseModel):
    order_id = IntegerField(primary_key=True, unique=True)
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    user_data = TextField()
    product_name = CharField(max_length=150, null=True)
    photos = TextField()
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'dk_data'


# class KartaGaiData(BaseModel):
#     order_id = IntegerField(primary_key=True, unique=True)
#     user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
#     prava_photo = CharField(max_length=100, null=True)
#     product_name = CharField(max_length=150, null=True)
#     price = IntegerField(default=0)
#     date = TimestampField()
#
#     class Meta:
#         db_name = 'karta_gai_data'


class KartaGibddData(BaseModel):
    order_id = IntegerField(primary_key=True, unique=True)
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    gos_nomer = CharField(max_length=100, null=True)
    product_name = CharField(max_length=150, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'karta_gibdd_data'


class KaskoBankData(BaseModel):
    order_id = IntegerField(primary_key=True, unique=True)
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    user_data = TextField()
    product_name = CharField(max_length=150, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'kasko_bank_data'


class AutoMedData(BaseModel):
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    user_data = TextField()
    product_name = CharField(max_length=150, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'auto_med_data'


class SearchSolaryData(BaseModel):
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE')
    user_data = TextField()
    product_name = CharField(max_length=150, null=True)
    price = IntegerField(default=0)
    date = TimestampField()

    class Meta:
        db_name = 'search_solary_data'


class Products(BaseModel):
    product_id = CharField(max_length=100, null=True)
    product_slug = CharField(max_length=150, null=True)
    product_name = CharField(max_length=150, null=True)
    product_price = IntegerField(default=500)

    class Meta:
        db_name = 'products'


class ProductsPhotoQuestionnaire(BaseModel):
    user_id = ForeignKeyField(Users, to_field='user_id', on_delete='CASCADE', unique=False)
    order_id = IntegerField(primary_key=True, unique=True)
    product_name = CharField(max_length=150, null=True)
    user_data_photo = TextField(null=True)
    product_price = IntegerField(default=0)

    class Meta:
        db_name = 'products_photo_questionnaire'


class UniqueReferalLinks(BaseModel):
    referer = CharField(max_length=100)
    referal_id = CharField(max_length=100, unique=True)
    referals = IntegerField(default=0)

    class Meta:
        db_name = 'unique_referal_links'
