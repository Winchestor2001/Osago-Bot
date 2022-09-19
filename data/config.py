from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")  # Забираем значение типа str
ADMINS = list(map(int, env.list("ADMINS")))  # Тут у нас будет список из админов
DB_NAME = env.str("DB_NAME")
DB_USER = env.str("DB_USER")
DB_PASSWORD = env.str("DB_PASSWORD")
DB_HOST = env.str("DB_HOST")
DB_PORT = env.str("DB_PORT")
BOT_CHANNEL_ID = -1001671141710
BOT_CHANNEL_LINK = 'https://t.me/+n5K3rRkrX1tjZDgy'

FROM_LINK = {
    'yandex': 'Яндекс',
    'google': 'Google',
    'telegram': 'Телеграм',
    'whatsapp': 'WhatsApp',
    'vkontakte': 'Вконтакте',
    'friend': 'От друга',
}
