from aiogram import Bot
import os

# Если истина, то бот будет запущен, иначе нет
IS_ENABLED = True

# Если истина, то партнерская система работает, команда "пстата"
IS_PARTNERS_SYSTEM_ENABLED = False

# Токен бота для его работоспособности
bot = Bot(token=os.environ["TOKEN"])

# Название магазина
SHOP_NAME = "PMarket"
# Телеграм ссылка на бота магазина
SHOP_BOT_URL = ""
# Телеграм ссылка на новостной канал магазина
SHOP_NEWS_CHANNEL_URL = ""
# Телеграм ссылка на техническую поддержку
SHOP_SUPPORT_URL = ""
# Телеграм ссылка на техническую поддержку
SHOP_REVIEWS_URL = ""
# Ссылка на пользовательское соглашение
SHOP_USER_AGREEMENT_URL = ""

# Айди канала, куда приходит информация о заказах
ORDERS_CHAT_ID = -1


def get_bot():
    return bot
