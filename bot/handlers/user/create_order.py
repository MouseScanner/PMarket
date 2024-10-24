from aiogram import types

from anypay import AnyPayAPI, AnyPayAPIError

from ...database.methods.users import get as user_get
from ...database.methods.users import create as user_create

from ...database.methods.categories import get as categories_get

from ...database.methods.goods import get as goods_get

from ...database.methods.orders import create as orders_create
from ...database.methods.orders import get as orders_get
from ...database.methods.orders import update as orders_update

from ...database.methods.partners import update as partners_update
from ...database.methods.partners import get as partners_get

from ...logs import logger
from ...config import get_bot, ORDERS_CHAT_ID

api = AnyPayAPI(
    '34F5E0FD201BAE1485', 'qEEAhEIgwJRv1LrmWSvEUIJRirDgox8ikWV3U9A', check=False,  # you can disable credentials check
)


async def anypay_create_order(order_id: int, amount_id: int):
    try:
        await api.get_balance()

    except AnyPayAPIError as exc:
        logger.error(exc)

    bill = await api.create_bill(  # easier way to create payment via SCI
        pay_id=order_id,
        amount=amount_id,
        project_id=11981,
        project_secret='SHwmVER23M3XKEh3C7',
    )

    return bill.id, bill.url


async def anypay_check_order(pay_id: int) -> bool:
    payments = await api.get_payments(project_id=11981, pay_id=pay_id)

    is_paid = False

    for payment in payments:
        if payment.status == 'paid':
            is_paid = True
            break

    return is_paid


async def create_order(clb: types.CallbackQuery) -> None:
    if clb.from_user is None:
        return

    method1, method2, user_id, good_id = clb.data.split('_')
    user_id = int(user_id)
    good_id = int(good_id)
    if user_id != clb.from_user.id:
        return

    partner_id = (await user_get.get(clb.from_user.id))[7]
    order_info = await orders_create.create(user_id, partner_id, good_id)

    if order_info is None:
        logger.error(
            f"Произошла ошибка при создании заказа (пустой заказ). TG_ID: {clb.from_user.id}. Содержание order_info: {order_info}")
        return

    logger.debug(f"order_info: {order_info}")

    good_info = await goods_get.get(int(order_info[6]))

    # pay_id, order_url = await anypay_create_order(order_info[0], int(good_info[3] * (1 - (await partners_get.get_by_promo((await user_get.get(clb.from_user.id))[7]))[5] / 100)))
    # Временно убран партнерский бонус

    pay_id, order_url = await anypay_create_order(order_info[0], int(good_info[3] - good_info[6]))

    keyboard = types.InlineKeyboardMarkup(resize_keyboard=True)
    buttons = [
        types.InlineKeyboardButton(text=f"Оплатить", url=f"{order_url}"),
        types.InlineKeyboardButton(text=f"Проверить оплату", callback_data=f"checkpaygood_{order_info[0]}_{pay_id}")

    ]
    keyboard.add(*buttons)

    await clb.message.edit_caption('Нажмите еще раз на кнопку "Оплатить", чтобы перейти к оплате.')
    await clb.message.edit_reply_markup(keyboard)


async def checkpaygood(clb: types.CallbackQuery) -> None:
    if clb.from_user is None:
        return

    try:
        order_info = await orders_get.get(clb.from_user.id)
    except IndexError:
        return

    try:
        check_order_id, pay_id = map(int, clb.data.replace('checkpaygood_', '').split('_'))
    except ValueError:
        await clb.answer("Нажмите кнопку Оплатить")
        return

    if order_info[2] == 1:
        await clb.answer('Платеж оплачен, товар в процессе выдачи', show_alert=True)
        return

    order_is_paid = await anypay_check_order(pay_id)

    if not order_is_paid:
        await clb.answer('Платеж еще не поступил', show_alert=True)
        return

    await orders_update.update(check_order_id, 'status', 1)

    try:
        await partners_update.update((await user_get.get(clb.from_user.id))[7], "total_sales",
                                     (await partners_get.get_by_promo((await user_get.get(clb.from_user.id))[7]))[
                                         6] + 1)
        await partners_update.update((await user_get.get(clb.from_user.id))[7], "all_income",
                                     (await partners_get.get_by_promo((await user_get.get(clb.from_user.id))[7]))[
                                         8] + (await goods_get.get(order_info[6]))[11] // 2)

        await partners_update.update((await user_get.get(clb.from_user.id))[7], "income_left",
                                     (await partners_get.get_by_promo((await user_get.get(clb.from_user.id))[7]))[
                                         9] + (await goods_get.get(order_info[6]))[11] // 2)
    except Exception as ERROR:
        logger.error(f"Ошибка при обновлении данных партнера: {ERROR}")

    await clb.message.answer(
        f'✅ Вы успешно оплатили заказ (№{check_order_id}).\n\nЗаказ поступил в обработку. Совсем скоро Вы получите свой товар, а также пришлем инструкцию по активации, ожидайте.\n❓ По любым вопросам задержки (больше 3 часов с момента покупки) обращайтесь в службу поддержки: @pmarket_support')
    logger.success(f'Оплачен новый заказ №{check_order_id}')

    await get_bot().send_message(protect_content=True, parse_mode="HTML", chat_id=ORDERS_CHAT_ID,
                                 text=f"Оплачен новый заказ №{check_order_id}\n\nПокупатель: @{clb.from_user.username}, №{(await user_get.get(clb.from_user.id))[0]}\nСумма заказа: {(await goods_get.get(order_info[6]))[3]}₽")
