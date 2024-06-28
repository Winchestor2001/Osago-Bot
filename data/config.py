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

# SUPPORT_ADMIN = env.str("SUPPORT_ADMIN")

FROM_LINK = {
    'yandex': 'Яндекс',
    'google': 'Google',
    'telegram': 'Телеграм',
    'whatsapp': 'WhatsApp',
    'vkontakte': 'Вконтакте',
    'friend': 'От друга',
}
