from aiogram import types

from ... import config


async def about(msg: types.Message) -> None:
    if msg.from_user is None:
        return

    message = f"""Информация о магазине <a 
    href="{config.SHOP_NEWS_CHANNEL_URL}">{config.SHOP_NAME}</a>\n<a 
    href="{config.SHOP_USER_AGREEMENT_URL}">Пользовательское соглашение</a>\n\n
    По вопросам сотрудничества и работе магазина <a href="{config.SHOP_SUPPORT_URL}">обращаться в поддержку</a>"""

    await msg.answer(text=message, parse_mode="HTML")
