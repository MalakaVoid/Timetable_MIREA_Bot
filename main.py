from aiogram import Dispatcher, Bot, executor,types
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from globals import TOKEN_API, sampleGroup
from datetime import datetime, timedelta
from keyboards import get_inline_keyboard
import re

bot = Bot(TOKEN_API)
dp = Dispatcher(bot)

#Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message)->None:
    await bot.send_message(chat_id=message.from_user.id, text="Добро пожаловать!\n"
                                                         "Чтобы получить расписание, введите номер вашей группы.\n"
                                                         "Формат: БСБО-10-21.")
    await message.delete()
#Пока что обработчик ввода группы пользователем
@dp.message_handler()
async def all_message(message: types.Message):
    match= re.fullmatch(sampleGroup, message.text)
    if match != None:
        #функция проверки существования данной группы!!!!!!!!!!
        if is_group_availibale(message.text):
            #Добавление в базу данных id пользователя и номер группы!!!!!!!!!!!
            add_user_group_to_bd(message.from_user.id, message.text)
            await bot.send_message(message.from_user.id, text="Получить расписание на (выберите одно из указанных ниже)",
                                   reply_markup=get_inline_keyboard('main_menu'))


#Проверка существования группы
def is_group_availibale(group)->bool:
    return True
#Добавление группы и id пользователя в базу данных
def add_user_group_to_bd(id, group):
    print(id)

#Главное меню
async def main_menu_message(callback):
    await callback.message.edit_text(text="Получить расписание на (выберите одно из указанных ниже)",
                                     reply_markup=get_inline_keyboard('main_menu'))

# #Inline kb обработчик
@dp.callback_query_handler(lambda callback_querry: callback_querry.data.startswith('btn'))
async def ik_cb_handler(callback: types.CallbackQuery):
    #Выдача расписания на сегодня
    if callback.data=='today_btn':
        await callback.message.edit_text(text=current_day_timetable(datetime.today()),
                                   reply_markup=None)
    if callback.data=='tommorow_btn':
        one_day=timedelta(days=1)
        await callback.message.edit_text(text=current_day_timetable(datetime.today()+one_day),
                                         reply_markup=None)

#Получение расписания по дате!!!!!!!!!!!!!!!!!!
def current_day_timetable(date)->str:
    return f'Сегодня вот эта дата: {date}'

if __name__== '__main__':
    executor.start_polling(dp, skip_updates=True)