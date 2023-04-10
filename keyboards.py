from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_calendar import SimpleCalendar

def get_inline_keyboard(id)->InlineKeyboardMarkup:
    ikb=InlineKeyboardMarkup()
    if (id=='main_menu'):
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Сегодня', callback_data='today_main_btn'),InlineKeyboardButton('Завтра', callback_data='tommorow_main_btn')],
            [InlineKeyboardButton('Выбор даты через календарь', callback_data='calendar_main_btn')],
            [InlineKeyboardButton('Эта неделя', callback_data='week_main_btn')],
            [InlineKeyboardButton('Изменить номер группы', callback_data='change_group_num_main_btn')]
        ])
    if id == 'timetable':
        ikb=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Предыдуший день', callback_data='prev_day_tmtb_btn'),
             InlineKeyboardButton('Следующий день', callback_data='next_day_tmtb_btn')],
            [InlineKeyboardButton('Назад', callback_data='back_tmtb_btn')]
        ])
    if id == 'back_from_enddate':
        ikb=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Отменить",
                                  callback_data='back_end_btn')]
        ])
    return ikb

