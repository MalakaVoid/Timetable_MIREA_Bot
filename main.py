from aiogram import Dispatcher, Bot, executor,types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from globals import TOKEN_API, sampleGroup, sampleDate
from datetime import datetime, timedelta
from keyboards import get_inline_keyboard
from aiogram_calendar import SimpleCalendar, simple_cal_callback
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from bd_operations import current_week_timetable, current_day_timetable, group_to_bd, is_group_aviable
import sqlite3
import re
#Начальная инициализация
bot = Bot(TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot,
                storage=storage)
#Состояния бота
class GroupStates(StatesGroup):
    group = State()
    group_first = State()

#Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message, state: FSMContext)->None:
    await bot.send_message(chat_id=message.from_user.id,
                           text="<b>Добро пожаловать!\n"
                                "Чтобы получить расписание, введите номер вашей группы.</b>\n"
                                "<em>Формат: БСБО-10-21.</em>",
                           parse_mode="HTML")
    await GroupStates.group.set()
    await message.delete()

#Удаление не нужных сообщений
@dp.message_handler(state=None)
async def del_messages(message: types.Message):
    await message.delete()

#Пока что обработчик ввода группы пользователем
@dp.message_handler(state=[GroupStates.group, GroupStates.group_first])
async def get_group(message: types.Message, state: FSMContext):
    match = re.fullmatch(sampleGroup, message.text)
    if match != None:
        #функция проверки существования данной группы!!!!!!!!!!
        if is_group_aviable(message.text):
            #Добавление в базу данных id пользователя и номер группы!!!!!!!!!!!
            group_to_bd(message.chat.id, message.text)
            await bot.send_message(message.from_user.id,
                                   text="<b>Получить расписание на (выберите одно из указанных ниже)</b>",
                                   parse_mode="HTML",
                                   reply_markup=get_inline_keyboard('main_menu'))
            await state.finish()
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Не смогли найти данную группу. Попробуйте еще раз.")
            await state.finish()
            await GroupStates.group.set()
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Не правильный формат группы, попробуйте еще раз.")
        await state.finish()
        await GroupStates.group.set()

#Главное меню
async def main_menu_message(callback):
    await callback.message.edit_text(text="<b>Получить расписание на (выберите одно из указанных ниже)</b>",
                                     parse_mode="HTML",
                                     reply_markup=get_inline_keyboard('main_menu'))

#Обработчик клавиатуры в главном меню
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.endswith('main_btn'), state='*')
async def ik_cb_main_handler(callback: types.CallbackQuery, state: FSMContext):
    #Выдача расписания на сегодня
    if callback.data=='today_main_btn':
        await callback.message.edit_text(text=current_day_timetable(callback.message.chat.id
                                                                    ,datetime.today()),
                                         reply_markup=get_inline_keyboard("timetable"),
                                         parse_mode="HTML")
    #Выдача расписания на завтра
    elif callback.data=='tommorow_main_btn':
        one_day=timedelta(days=1)
        await callback.message.edit_text(text=current_day_timetable(callback.message.chat.id
                                                                    ,datetime.today()+one_day),
                                         reply_markup=get_inline_keyboard("timetable"),
                                         parse_mode="HTML")
    #Выдача расписания на неделю
    elif callback.data == 'week_main_btn':
        await callback.message.edit_text(text = current_week_timetable(callback.message.chat.id),
                                         reply_markup=get_inline_keyboard('back_from_week_table'),
                                         parse_mode="HTML")
    #Смена номера группы
    elif callback.data == 'change_group_num_main_btn':
        await GroupStates.group_first.set()
        await callback.message.edit_text(text="<b>Введите номер группы.</b>\n"
                                              "<em>Формат БСБО-10-21</em>",
                                         parse_mode="HTML",
                                         reply_markup=get_inline_keyboard('back_from_enddate'))
    #Календарь
    elif callback.data == 'calendar_main_btn':
        await callback.message.edit_text(text='<b>Выберите дату:</b>',
                                         reply_markup=await SimpleCalendar().start_calendar())
#Handler календаря
@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.edit_text(text=current_day_timetable(callback_query.message.chat.id,
                                                                          date),
                                            reply_markup=get_inline_keyboard('timetable'),
                                            parse_mode="HTML"
        )

#Обработчик клавиатуры расписания
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.endswith('tmtb_btn'), state='*')
async def ik_cb_tmtb_handler(callback: types.CallbackQuery, state: FSMContext):
    # Обработка кнопки следующего дня в расписании
    one_day = timedelta(days=1)
    if callback.data == 'next_day_tmtb_btn':
        date = datetime.strptime(re.findall(sampleDate,
                                            callback.message.text)[0],
                                            "%d.%m.%Y")
        await callback.message.edit_text(text=current_day_timetable(callback.message.chat.id,
                                                                    date+one_day),
                                         reply_markup=get_inline_keyboard("timetable"),
                                         parse_mode="HTML")
    elif callback.data == 'prev_day_tmtb_btn':
        date = datetime.strptime(re.findall(sampleDate,
                                            callback.message.text)[0],
                                            "%d.%m.%Y")
        await callback.message.edit_text(text=current_day_timetable(callback.message.chat.id,
                                                                    date - one_day),
                                         reply_markup=get_inline_keyboard("timetable"),
                                         parse_mode="HTML")
    # Обработка кнопки назад в расписании
    elif callback.data == 'back_tmtb_btn':
        await main_menu_message(callback)

#обработчик клавиатуры Отмены
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.endswith('end_btn'), state='*')
async def ik_cb_end_handler(callback: types.CallbackQuery, state: FSMContext):
    #Обработка кнопки отменить при вводе даты пользователем и ввода группы
    cur_state = await state.get_state()
    if callback.data == 'back_end_btn' and cur_state is not None:
        if cur_state == 'GroupStates:group':
            await bot.send_message(chat_id=callback.message.chat.id,
                               text="<b>Получить расписание на (выберите одно из указанных ниже)</b>",
                                reply_markup=get_inline_keyboard('main_menu'),
                                   parse_mode="HTML")
            await callback.message.edit_reply_markup(reply_markup=None)
        else:
            await main_menu_message(callback)
        await state.finish()
    elif callback.data == 'back_end_btn':
        await callback.message.edit_reply_markup(reply_markup=None)

if __name__== '__main__':
    executor.start_polling(dp, skip_updates=True)