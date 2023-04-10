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
                           text="Добро пожаловать!\n"
                                "Чтобы получить расписание, введите номер вашей группы.\n"
                                "Формат: БСБО-10-21.")
    await GroupStates.group.set()
    await message.delete()

#Удаление не нужных сообщений
@dp.message_handler(state=None)
async def del_messages(message: types.Message):
    await message.delete()

#Пока что обработчик ввода группы пользователем
@dp.message_handler(state=[GroupStates.group, GroupStates.group_first])
async def get_group(message: types.Message, state: FSMContext):
    match= re.fullmatch(sampleGroup, message.text)
    if match != None:
        #функция проверки существования данной группы!!!!!!!!!!
        if is_group_availibale(message.text):
            #Добавление в базу данных id пользователя и номер группы!!!!!!!!!!!
            add_user_group_to_bd(message.from_user.id, message.text)
            await bot.send_message(message.from_user.id,
                                   text="Получить расписание на (выберите одно из указанных ниже)",
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

#Проверка существования группы
def is_group_availibale(group)->bool:
    return True
#Добавление группы и id пользователя в базу данных
def add_user_group_to_bd(id, group):
    print(id, group)

#Главное меню
async def main_menu_message(callback):
    await callback.message.edit_text(text="Получить расписание на (выберите одно из указанных ниже)",
                                     reply_markup=get_inline_keyboard('main_menu'))

#Обработчик клавиатуры в главном меню
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.endswith('main_btn'), state='*')
async def ik_cb_main_handler(callback: types.CallbackQuery, state: FSMContext):
    #Выдача расписания на сегодня
    if callback.data=='today_main_btn':
        await callback.message.edit_text(text=current_day_timetable(datetime.today()),
                                   reply_markup=get_inline_keyboard("timetable"))
    #Выдача расписания на завтра
    elif callback.data=='tommorow_main_btn':
        one_day=timedelta(days=1)
        await callback.message.edit_text(text=current_day_timetable(datetime.today()+one_day),
                                         reply_markup=get_inline_keyboard("timetable"))
    #Выдача расписания на неделю
    elif callback.data == 'week_main_btn':
        a=1
    #Смена номера группы
    elif callback.data == 'change_group_num_main_btn':
        await GroupStates.group_first.set()
        await callback.message.edit_text(text="Введите номер группы.\n"
                                              "Формат БСБО-10-21",
                                         reply_markup=get_inline_keyboard('back_from_enddate'))
    #Календарь
    elif callback.data == 'calendar_main_btn':
        await callback.message.edit_text(text='Выберите дату:',
                                         reply_markup=await SimpleCalendar().start_calendar())
#Handler календаря
@dp.callback_query_handler(simple_cal_callback.filter())
async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        await callback_query.message.edit_text(text=current_day_timetable(date),
                                            reply_markup=get_inline_keyboard('timetable')
        )

#Обработчик клавиатуры расписания
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.endswith('tmtb_btn'), state='*')
async def ik_cb_tmtb_handler(callback: types.CallbackQuery, state: FSMContext):
    # Обработка кнопки следующего дня в расписании
    if callback.data == 'next_day_tmtb_btn':
        a = 1
    elif callback.data == 'prev_day_tmtb_btn':
        a=1
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
                               text="Получить расписание на (выберите одно из указанных ниже)",
                                reply_markup=get_inline_keyboard('main_menu'))
            await callback.message.edit_reply_markup(reply_markup=None)
        else:
            await main_menu_message(callback)
        await state.finish()
    elif callback.data == 'back_end_btn':
        await callback.message.edit_reply_markup(reply_markup=None)


#Получение расписания по дате!!!!!!!!!!!!!!!!!!
def current_day_timetable(date)->str:
    return f'Расписание на {date.strftime("%d.%m.%Y")}'



if __name__== '__main__':
    executor.start_polling(dp, skip_updates=True)