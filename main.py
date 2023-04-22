from aiogram import Dispatcher, Bot, executor,types
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from globals import TOKEN_API, sampleGroup, sampleDate, sampleTime
from datetime import datetime, timedelta
from keyboards import get_inline_keyboard
from aiogram_calendar import SimpleCalendar, simple_cal_callback
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from bd_operations import current_week_timetable, current_day_timetable, group_to_bd, is_group_aviable, event_existense, enter_event, event_id_arr, delete_event, current_day_events
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
class AddEventSates(StatesGroup):
    time = State()
    event_name = State()
class DelEvent(StatesGroup):
    event_num = State()
class ChangeEvent(StatesGroup):
    event_num = State
    time = State()
    event_name = State()

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

#Для получения данных о ивенте
@dp.message_handler(state=AddEventSates.time)
async def get_event_time(message: types.Message, state: FSMContext):
    match = re.fullmatch(sampleTime, message.text)
    if match != None:
        arr_time = message.text.split(":")
        if int(arr_time[0]) < 24 and int(arr_time[1]) < 60:
            await bot.send_message(message.chat.id,
                                   text='<b>Введите событие</b>',
                                   parse_mode='HTML')
            async with state.proxy() as data:
                data['time'] = message.text
                await AddEventSates.next()
        else:
            await bot.send_message(chat_id=message.from_user.id,
                                   text="Не правильное время, попробуйте еще раз.")
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text="Не правильный формат времени, попробуйте еще раз.")

@dp.message_handler(state=AddEventSates.event_name)
async def get_event_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        date=data['date_event']
        enter_event(message.chat.id, data['date_event'], data['time'], message.text)
    if event_existense(date,
                       message.chat.id):
        str_result = current_day_timetable(message.chat.id,
                                           date)
        await bot.send_message(message.chat.id,
                               text=str_result,
                               reply_markup=get_inline_keyboard('with_event_timetable'),
                               parse_mode="HTML")
    else:
        str_result = current_day_timetable(message.chat.id,
                                           date)
        await bot.send_message(message.chat.id,
                               text=str_result,
                               reply_markup=get_inline_keyboard('without_event_timetable'),
                               parse_mode="HTML")
    await state.finish()

#Удаление ивента, получение id ивента
@dp.message_handler(state=DelEvent.event_num)
async def get_del_event_id(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        arr_of_event_id = event_id_arr(data['date'], message.chat.id)
        flag = False
        date = data['date']
        for each in arr_of_event_id:
            if each[0] == message.text:
                flag = True
        if flag:
            delete_event(message.text, message.chat.id, data['date'])
            await state.finish()
            if event_existense(date,
                               message.chat.id):
                str_result = current_day_timetable(message.chat.id,
                                                   date)
                await bot.send_message(message.chat.id,
                                       text=str_result,
                                       reply_markup=get_inline_keyboard('with_event_timetable'),
                                       parse_mode="HTML")
            else:
                str_result = current_day_timetable(message.chat.id,
                                                   date)
                await bot.send_message(message.chat.id,
                                       text=str_result,
                                       reply_markup=get_inline_keyboard('without_event_timetable'),
                                       parse_mode="HTML")
        else:
            await bot.send_message(message.chat.id,
                                   text="<b>Неверный номер события, попробуйте еще раз</b>",
                                   parse_mode='HTML',
                                   reply_markup=get_inline_keyboard('back_from_enddate'))

@dp.message_handler(state = ChangeEvent.event_num)
async def get_edditing_event_num(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        arr_of_event_id = event_id_arr(data['date'], message.chat.id)
        flag = False
        date = data['date']
        for each in arr_of_event_id:
            if each[0] == message.text:
                flag = True
        if flag:
            data['event_num'] = message.text
            await bot.send_message(message.chat.id,
                                   text='<b>Выберите опцию</b>',
                                   parse_mode='HTML',
                                   reply_markup=get_inline_keyboard('time_or_name_tmtb_btn'))
        else:
            await bot.send_message(message.chat.id,
                                   text="<b>Неверный номер события, попробуйте еще раз</b>",
                                   parse_mode='HTML',
                                   reply_markup=get_inline_keyboard('back_from_enddate'))
#Главное меню
async def main_menu_message(callback):
    await callback.message.edit_text(text="<b>Получить расписание на (выберите одно из указанных ниже)</b>",
                                     parse_mode="HTML",
                                     reply_markup=get_inline_keyboard('main_menu'))

#Обработчик клавиатуры в главном меню
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.endswith('main_btn'), state='*')
async def ik_cb_main_handler(callback: types.CallbackQuery, state: FSMContext):
    #Выдача расписания на сегодня
    if callback.data == 'today_main_btn':
        if event_existense(datetime.today(),
                           callback.message.chat.id):
            str_result = current_day_timetable(callback.message.chat.id,
                                               datetime.today())
            await callback.message.edit_text(text=str_result,
                                             reply_markup=get_inline_keyboard('with_event_timetable'),
                                             parse_mode="HTML")
        else:
            str_result = current_day_timetable(callback.message.chat.id,
                                               datetime.today())
            await callback.message.edit_text(text=str_result,
                                             reply_markup=get_inline_keyboard('without_event_timetable'),
                                             parse_mode="HTML")
    #Выдача расписания на завтра
    elif callback.data == 'tommorow_main_btn':
        one_day = timedelta(days=1)
        if event_existense(datetime.today() + one_day,
                           callback.message.chat.id):
            str_result = current_day_timetable(callback.message.chat.id,
                                               datetime.today() + one_day)
            await callback.message.edit_text(text=str_result,
                                             reply_markup=get_inline_keyboard('with_event_timetable'),
                                             parse_mode="HTML")
        else:
            str_result = current_day_timetable(callback.message.chat.id,
                                               datetime.today() + one_day)
            await callback.message.edit_text(text=str_result,
                                             reply_markup=get_inline_keyboard('without_event_timetable'),
                                             parse_mode="HTML")
    #Выдача расписания на неделю
    elif callback.data == 'week_main_btn':
        str_result = current_week_timetable(callback.message.chat.id)
        await callback.message.edit_text(text=str_result,
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
                                         reply_markup=await SimpleCalendar().start_calendar(),
                                         parse_mode='HTML')
#Handler календаря
@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query,
                                                              callback_data)
    if selected:
        if event_existense(date,
                           callback_query.message.chat.id):
            str_result = current_day_timetable(callback_query.message.chat.id,
                                               date)
            await callback_query.message.edit_text(text=str_result,
                                                   reply_markup=get_inline_keyboard('with_event_timetable'),
                                                   parse_mode="HTML")
        else:
            str_result = current_day_timetable(callback_query.message.chat.id,
                                               date)
            await callback_query.message.edit_text(text=str_result,
                                                   reply_markup=get_inline_keyboard('without_event_timetable'),
                                                   parse_mode="HTML")

#Обработчик клавиатуры расписания
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.endswith('tmtb_btn'), state='*')
async def ik_cb_tmtb_handler(callback: types.CallbackQuery, state: FSMContext):
    # Обработка кнопки следующего дня в расписании
    one_day = timedelta(days=1)
    if callback.data == 'next_day_tmtb_btn':
        date = datetime.strptime(re.findall(sampleDate,
                                            callback.message.text)[0],
                                 "%d.%m.%Y")
        if event_existense(date+one_day,
                           callback.message.chat.id):
            str_result = current_day_timetable(callback.message.chat.id,
                                               date + one_day)
            await callback.message.edit_text(text=str_result,
                                             reply_markup=get_inline_keyboard('with_event_timetable'),
                                             parse_mode="HTML")
        else:
            str_result = current_day_timetable(callback.message.chat.id,
                                               date + one_day)
            await callback.message.edit_text(text=str_result,
                                             reply_markup=get_inline_keyboard('without_event_timetable'),
                                             parse_mode="HTML")
    elif callback.data == 'prev_day_tmtb_btn':
        date = datetime.strptime(re.findall(sampleDate,
                                            callback.message.text)[0],
                                 "%d.%m.%Y")
        if event_existense(date-one_day,
                           callback.message.chat.id):
            str_result = current_day_timetable(callback.message.chat.id,
                                               date - one_day)
            await callback.message.edit_text(text=str_result,
                                             reply_markup=get_inline_keyboard('with_event_timetable'),
                                             parse_mode="HTML")
        else:
            str_result = current_day_timetable(callback.message.chat.id,
                                               date - one_day)
            await callback.message.edit_text(text=str_result,
                                             reply_markup=get_inline_keyboard('without_event_timetable'),
                                             parse_mode="HTML")
    elif callback.data == 'add_event_tmtb_btn':
        await callback.message.edit_text('<b>Введите время события</b>\n'
                                         '<em>Формат: 00:00</em>',
                                         parse_mode='HTML',
                                         reply_markup=get_inline_keyboard('back_from_enddate'))
        await AddEventSates.time.set()
        date = datetime.strptime(re.findall(sampleDate,
                                            callback.message.text)[0],
                                 "%d.%m.%Y")
        async with state.proxy() as data:
            data['date_event'] = date
    elif callback.data == 'delete_event_tmtb_btn':
        date = datetime.strptime(re.findall(sampleDate,
                                            callback.message.text)[0],
                                 "%d.%m.%Y")
        str_output = '<b>Введите номер события для удаления: '
        for each in event_id_arr(date ,callback.message.chat.id):
          str_output+=  each[0] + ' '
        str_output += '</b>\n\n'
        str_output += current_day_events(callback.message.chat.id, date)
        await callback.message.edit_text(text=str_output,
                               parse_mode='HTML',
                               reply_markup=get_inline_keyboard('back_from_enddate'))
        await DelEvent.event_num.set()
        async with state.proxy() as data:
            data['date']=date
    elif callback.data == 'change_event_tmtb_btn':
        date = datetime.strptime(re.findall(sampleDate,
                                            callback.message.text)[0],
                                 "%d.%m.%Y")
        str_output = '<b>Введите номер события для изменения: '
        for each in event_id_arr(date, callback.message.chat.id):
            str_output += each[0] + ' '
        str_output += '</b>\n\n'
        str_output += current_day_events(callback.message.chat.id, date)
        await ChangeEvent.event_num.set()
        async with state.proxy() as data:
            data['event_date'] = date
    # Обработка кнопки назад в расписании
    elif callback.data == 'back_tmtb_btn':
        await main_menu_message(callback)

#обработчик клавиатуры Отмены
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.endswith('end_btn'), state='*')
async def ik_cb_end_handler(callback: types.CallbackQuery, state: FSMContext):
    #Обработка кнопки отменить при вводе даты пользователем и ввода группы
    cur_state = await state.get_state()
    if callback.data == 'back_end_btn' and cur_state is not None:
        if cur_state in ['GroupStates:group', 'AddEventSates:time', 'AddEventSates:event_name', 'DelEvent:event_num', 'ChangeEvent.event_num',
                         'ChangeEvent.event_name', 'ChangeEvent.time']:
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

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)