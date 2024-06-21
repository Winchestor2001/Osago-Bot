from environs import Env


env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMINS = env.list("ADMINS")
WEBHOOK_URL = env.str("WEBHOOK_URL")
WEBHOOK_PATH = env.str("WEBHOOK_PATH")
DB_NAME = env.str("DB_NAME")
DB_USER = env.str("DB_USER")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.str("DB_PORT")

# SUPPORT_ADMIN = env.str("SUPPORT_ADMIN")

FROM_LINK = {
    'yandex': 'Яндекс',
    'google': 'Google',
    'telegram': 'Телеграм',
    'whatsapp': 'WhatsApp',
    'vkontakte': 'Вконтакте',
    'friend': 'От друга',
}
