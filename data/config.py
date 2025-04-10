from environs import Env


env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = list(map(int, env.list("ADMINS")))
WEBHOOK_URL = env.str("WEBHOOK_URL")
WEBHOOK_PATH = env.str("WEBHOOK_PATH")

DB_NAME = env.str("DB_NAME")
DB_USER = env.str("DB_USER")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.str("DB_PORT")

REDIS_HOST = env.str("REDIS_HOST")
REDIS_PORT = env.str("REDIS_PORT")
REDIS_DB = env.str("REDIS_DB")

SECRET_KEY1 = env.str("SECRET_KEY1")
API_KEY = env.str("API_KEY")
MERCHANT_ID = env.str("MERCHANT_ID")

NICEPAY_MERCHANT_ID = env.str("NICEPAY_MERCHANT_ID")
NICEPAY_SECRET_KEY = env.str("NICEPAY_SECRET_KEY")

CRYSTALPAY_SECRET = env.str("CRYSTALPAY_SECRET")
CRYSTALPAY_LOGIN = env.str("CRYSTALPAY_LOGIN")
CRYSTALPAY_SALT = env.str("CRYSTALPAY_SALT")

# SUPPORT_ADMIN = env.str("SUPPORT_ADMIN")

FROM_LINK = {
    'yandex': 'Яндекс',
    'google': 'Google',
    'telegram': 'Телеграм',
    'whatsapp': 'WhatsApp',
    'vkontakte': 'Вконтакте',
    'friend': 'От друга',
}
