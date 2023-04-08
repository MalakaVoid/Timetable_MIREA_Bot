from aiogram import Dispatcher, Bot, executor,types
from aiogram.types import ReplyKeyboardMarkup,ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.callback_data import CallbackData
from globals import TOKEN_API, sampleGroup
from keyboards import get_inline_keyboard
import re
bot = Bot(TOKEN_API)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message)->None:
    await bot.send_message(chat_id=message.from_user.id, text="Добро пожаловать!\n"
                                                         "Чтобы получить расписание, введите номер вашей группы.\n"
                                                         "Формат: БСБО-10-21.")
    await message.delete()

@dp.message_handler()
async def all_message(message: types.Message):
    match= re.fullmatch(sampleGroup, message.text)
    if match != None:
        #функция проверки существования данной группы!!!!!!!!!!
        #Добавление в базу данных id пользователя и номер группы!!!!!!!!!!!
        await bot.send_message(message.from_user.id, text="Получить расписание на (выберите одно из указанных ниже)",
                               reply_markup=get_inline_keyboard())

async def main_menu_message(callback):
    await callback.message.edit_text(text="Получить расписание на (выберите одно из указанных ниже)",
                                     reply_markup=get_inline_keyboard())

@dp.callback_query_handler(lambda callback_querry: callback_querry.data.startswith('btn'))
async def ik_cb_handler(callback: types.CallbackQuery):

if __name__== '__main__':
    executor.start_polling(dp, skip_updates=True)