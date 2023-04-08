from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_inline_keyboard()->InlineKeyboardMarkup:
    ik_for_main_menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton('Сегодня', callback_data='today_btn'),InlineKeyboardButton('Завтра', callback_data='tommorow_btn')],
        [InlineKeyboardButton('Ввести дату', callback_data='current_date_btn')],
        [InlineKeyboardButton('Эта неделя', callback_data='week_btn')],
        [InlineKeyboardButton('Изменить номер группы', callback_data='change_group_num_btn')]
    ])
    return ik_for_main_menu

