from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram_calendar import SimpleCalendar


def get_inline_keyboard(id) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup()
    if (id == 'main_menu'):
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Сегодня',
                                  callback_data='today_main_btn'),
             InlineKeyboardButton('Завтра',
                                  callback_data='tommorow_main_btn')],
            [InlineKeyboardButton('Выбор даты через календарь',
                                  callback_data='calendar_main_btn')],
            [InlineKeyboardButton('Эта неделя',
                                  callback_data='week_main_btn')],
            [InlineKeyboardButton('Изменить группу',
                                  callback_data='change_group_num_main_btn'),
             InlineKeyboardButton('Написать в тех поддержку',
                                  callback_data='get_support_main_btn')]
        ])
    if id == 'without_event_timetable':
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Предыдуший день',
                                  callback_data='prev_day_tmtb_btn'),
             InlineKeyboardButton('Следующий день',
                                  callback_data='next_day_tmtb_btn')],
            [InlineKeyboardButton('Добавить событие',
                                  callback_data='add_event_tmtb_btn')],
            [InlineKeyboardButton('Назад',
                                  callback_data='back_tmtb_btn')]
        ])
    if id == 'with_event_timetable':
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton('Предыдуший день',
                                  callback_data='prev_day_tmtb_btn'),
             InlineKeyboardButton('Следующий день',
                                  callback_data='next_day_tmtb_btn')],
            [InlineKeyboardButton('Добавить событие',
                                  callback_data='add_event_tmtb_btn')],
            [InlineKeyboardButton('Изменить событие',
                                  callback_data='change_event_tmtb_btn'),
             InlineKeyboardButton('Удалить событие',
                                  callback_data='delete_event_tmtb_btn')],
            [InlineKeyboardButton('Назад',
                                  callback_data='back_tmtb_btn')]
        ])
    if id == 'back_from_enddate':
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Отменить",
                                  callback_data='back_end_btn')]
        ])
    if id == 'back_from_week_table':
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Назад",
                                  callback_data='back_tmtb_btn')]
        ])
    if id == 'time_or_name_tmtb_btn':
        ikb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton("Изменить время",
                                  callback_data='edit_time_event_btn'),
             InlineKeyboardButton("Изменить событие",
                                  callback_data='edit_name_event_btn')]
        ])
    return ikb