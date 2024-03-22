#сделай отмену, если пользователь случайно нажал кнопку
import asyncio
import sqlite3 as sql
import io
import datetime
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN_API #из файла config импортируем токен бота
from database import check_user_bd, get_reservation_data, get_users_with_access_0, delete_user,add_moderator, add_client,check_reservation_on_bd, check_client_bd, check_reservation_on_bd_2
from keyboards import entrance_ikb, moder_ikb, admin_ikb,reservation_ikb,default_kb, default_ikb
import pandas as pd
import os
entrance_username = ""  # Глобальная переменная для хранения логина при входе
entrance_password = ""
bot = Bot(token=TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

async def on_startup(dp):
    print('ok')

async def send_birthday_greeting(dp):
    current_date = datetime.datetime.now().date()
   # print(current_date)
    target_date = current_date + datetime.timedelta(days=7)
   # print(target_date)

    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()
    target_date_str = target_date.strftime("%d.%m")
   # print(target_date_str)
    current_date_str = current_date.strftime("%d.%m")
   # print(current_date_str)

    query = f"SELECT userName, chatId, firstName, dateOfBirth FROM clients " \
            f"WHERE SUBSTR(dateOfBirth, 1, 5) = '{target_date_str}' " \
            f"OR SUBSTR(dateOfBirth, 1, 5) = '{current_date_str}'"

    cur.execute(query)
    result = cur.fetchall()
   # print(result)
    cur.close()
    con.close()

    for row in result:
        username = row[0]
        chat_id = row[1]
        first_name = row[2]
        date_of_birth = row[3]

        if chat_id is None:
            continue

        if date_of_birth[:5] == current_date_str:
            # День рождения сегодня
            message_text = f"Дорогой гость, {first_name}! На связи Gaudí Bar 🦎. " \
                           f"От всей нашей команды передаем Вам тёплые поздравления с днём рождения! 🥳 " \
                           f"Желаем вам крепкого здоровья, удачи и счастья! " \
                           f"Сегодня у нас Вас ждёт второй кальян 🎁 и десерт в подарок, а также тройные бонусы."
            reply_markup = None
        else:
            message_text = f"Дорогой гость, {first_name}! На связи Gaudí Bar 🦎. " \
                           f"В ваш день рождения 🥳 при заказе кальяна для вас в подарок второй кальян 🎁 " \
                           f"и десерт для именинника! " \
                           f"А также в день рождения, за три дня до него и три дня после него " \
                           f"при визите к нам начислим вам тройные бонусы! " \
                           f"Забронировать столик для вас?"
            reply_markup = reservation_ikb

        await dp.bot.send_message(chat_id=chat_id, text=message_text, reply_markup=reply_markup)

async def schedule_birthday_greetings(dp):
    while True:
        await send_birthday_greeting(dp)
        # Pause for one day (24 hours)
        await asyncio.sleep(24 * 60 * 60)

class EntranceStates(StatesGroup): # Обработчики для входа
    WAITING_FOR_USERNAME = State()
    WAITING_FOR_PASSWORD = State()

class AddModerStates(StatesGroup): # Обработчики для входа
    WAITING_FOR_MODER_USERNAME = State()
    WAITING_FOR_MODER_PASSWORD = State()

class DeleteStates(StatesGroup):
    WAITING_FOR_DELETE_USERNAME=State()

class AddClientStates(StatesGroup):
    WAITING_FOR_CLIENT_NAME=State()
    WAITING_FOR_CLIENT_DOB = State()
    WAITING_FOR_CLIENT_USERNAME = State()
    WAITING_FOR_CLIENT_PHONE_NUMBER = State()

class AddReservationStates(StatesGroup):
    WAITING_FOR_INFO=State()
    WAITING_FOR_INFO_NEW=State()


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.answer(text="Добро пожаловать в наш телеграм-бот", reply_markup=default_kb)
    await message.delete()

    # Получение chat_id пользователя из сообщения
    chat_id = message.chat.id

    # Запрос номера телефона у пользователя
    request = types.KeyboardButton(text="Поделиться номером телефона", request_contact=True)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(request)
    await message.answer("Пожалуйста, предоставьте ваш номер телефона, по кнопке в меню", reply_markup=keyboard)

@dp.message_handler(content_types=types.ContentType.CONTACT)
async def handle_contact(message: types.Message):
    # Получение номера телефона из сообщения
    phone_number = message.contact.phone_number

    # Проверка наличия номера телефона в таблице "clients"
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()
    query = f"SELECT userName FROM clients WHERE phone_number = '{phone_number}'"
    cur.execute(query)
    result = cur.fetchone()

    if result:
        # Если номер телефона найден в таблице "clients", добавляем логин пользователя
        telegram_username = message.from_user.username
        chat_id = message.chat.id
        update_query = f"UPDATE clients SET userName = '{telegram_username}', chatId = {chat_id} WHERE phone_number = '{phone_number}'"
        cur.execute(update_query)
        con.commit()

        await message.answer("Логин успешно добавлен.", reply_markup=default_kb)
    else:
        # Если логин пользователя не найден в базе данных
        chat_id = message.chat.id
        telegram_username = message.from_user.username
        # Проверка наличия chat_id в таблице clients_default
        check_query = f"SELECT chatId FROM clients_default WHERE chatId = {chat_id}"
        cur.execute(check_query)
        result = cur.fetchone()
        # print(result)

        if result:
            # Если chat_id уже существует в таблице clients_default, не добавляем его
            await message.answer("Ваш логин, уже добавлен.", reply_markup=default_kb)
        else:
            # Добавляем новую запись в clients_default
            insert_query = f"INSERT INTO clients_default (userName, chatId, phone_number) VALUES ('{telegram_username}', {chat_id}, '{phone_number}')"
            cur.execute(insert_query)
            con.commit()
            await message.answer("Логин успешно добавлен.", reply_markup=default_kb)

    con.close()

@dp.message_handler(commands=['menu'])
async def moder_command(message:types.Message):
    await message.answer(text="В нашем телеграм боте вы можете: ", reply_markup=default_ikb)
    await message.delete()


@dp.message_handler(commands=['moder'])
async def moder_command(message:types.Message):
    await message.answer(text="Здравствуйте, подтвердите вход", reply_markup=entrance_ikb)
    await message.delete()

@dp.callback_query_handler()
async def callback_authentication(callback: types.CallbackQuery, state: FSMContext):
    if callback.data=='entrance':  # колбек для входа
        await callback.message.answer('Введите логин')
        await EntranceStates.WAITING_FOR_USERNAME.set()
    elif callback.data=='opening_hours':
        current_file_path = os.path.abspath(__file__)
        project_directory = os.path.dirname(current_file_path)
        # Построение пути к PDF файлу относительно директории проекта
        image_path = os.path.join(project_directory, 'opening_hours.png')
        chat_id = callback.message.chat.id  # Получение chat_id из callback
        with open(image_path, 'rb') as photo:
            await bot.send_photo(chat_id=chat_id, photo=photo)

    elif callback.data=='websity':
        await callback.message.answer(' Наш сайт: https://gaudibar.ru/')
    elif callback.data=='info_promotion':
        await callback.message.answer('Подготавливаем файл с специальными предложениями для вас')
        current_file_path = os.path.abspath(__file__)
        project_directory = os.path.dirname(current_file_path)
        # Построение пути к PDF файлу относительно директории проекта
        pdf_file_path = os.path.join(project_directory, '2.pdf')
        chat_id = callback.message.chat.id  # Получение chat_id из callback
        with open(pdf_file_path, 'rb') as f:
            await bot.send_document(chat_id=chat_id, document=f)
    elif callback.data=='number_phone':
        await callback.message.answer(' Вы можете связаться с нами по номеру: +7 343 201 11 17')
    elif callback.data == 'menu_pdf':
        await callback.message.answer('Подготавливаем файл с меню для вас')
        current_file_path = os.path.abspath(__file__)
        project_directory = os.path.dirname(current_file_path)
        # Построение пути к PDF файлу относительно директории проекта
        pdf_file_path = os.path.join(project_directory, '1.pdf')
        chat_id = callback.message.chat.id  # Получение chat_id из callback
        with open(pdf_file_path, 'rb') as f:
            await bot.send_document(chat_id=chat_id, document=f)

    elif callback.data == 'reservation':
        await callback.message.answer('Список забронированных столиков')
        # Получите данные из базы данных SQLite и создайте DataFrame
        table_data = get_reservation_data()  # Функция для получения данных из базы данных
        df = pd.DataFrame(table_data)
        # Создайте объект BytesIO для хранения данных в памяти
        excel_data = io.BytesIO()
        # Запишите данные DataFrame в BytesIO объект
        with pd.ExcelWriter(excel_data, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        # Переместите указатель BytesIO в начало
        excel_data.seek(0)
        # Отправьте табличку с помощью метода send_document
        excel_data.name = 'reservation_table.xlsx'  # Устанавливаем имя файла для объекта BytesIO
        await bot.send_document(callback.from_user.id, excel_data)

    elif callback.data == 'deleteModer':
        await callback.message.answer('Список менеджеров')
        user_logins = get_users_with_access_0()
        users_text = '\n'.join(user_logins)
        await callback.message.answer(f'Логины пользователей :\n{users_text}')
        await callback.message.answer('Введите логин пользователя, которого нужно удалить')
        await DeleteStates.WAITING_FOR_DELETE_USERNAME.set()

    elif callback.data == 'addModer':
        await callback.message.answer('Введите логин модератора')
        await AddModerStates.WAITING_FOR_MODER_USERNAME.set()

    elif callback.data == 'addClient':
        await callback.message.answer('Введите ФИО клиента (через пробел)')
        await AddClientStates.WAITING_FOR_CLIENT_NAME.set()
    elif callback.data == 'addReservation':
        chat_id = callback.message.chat.id
        if check_client_bd(chat_id):
            await callback.message.answer(" \n 🦎 Перед бронированием, пожалуйста, ознакомьтесь с режимом работы. Стол закрепляется за вами на 3 часа. \n 🦎 Напишите дату, время и количество гостей для бронирования. \n🦎 Если количество гостей больше 8, пожалуйста, забронируйте 2 стола. \n🦎 Пожалуйста, введите все ключевые слова для корректной обработки данных. \n🦎 Напишите слово <b>«отмена»</b> ,если хотите прервать бронирование. \n🦎 Для удобства скопируйте пример ниже, и введите свои данные.", parse_mode='HTML')
            await callback.message.answer(" <b>Дата:</b> 1970.20.02 \n<b>Время:</b> 16:00 \n<b>Количество гостей:</b> 6 ", parse_mode='HTML')
            await AddReservationStates.WAITING_FOR_INFO.set()
        else:
            await callback.message.answer("\n 🦎 Перед бронированием, пожалуйста, ознакомьтесь с режимом работы. Стол закрепляется за вами на 3 часа.\n 🦎 Напишите свое имя, дату, время и количество гостей для бронирования. \n🦎 Если количество гостей больше 8, пожалуйста, забронируйте 2 стола. \n🦎 Пожалуйста, введите все ключевые слова для корректной обработки данных. \n🦎 Напишите слово <b>«отмена»</b> ,если хотите прервать бронирование. \n🦎 Для удобства скопируйте пример ниже, и введите свои данные.", parse_mode='HTML')
            await callback.message.answer(
                "<b>Имя:</b> Анастасия \n<b>Дата:</b> 1970.20.02 \n<b>Время:</b> 16:00 \n<b>Количество гостей:</b> 6 ",parse_mode='HTML')
            await AddReservationStates.WAITING_FOR_INFO_NEW.set()


@dp.message_handler(state=AddReservationStates.WAITING_FOR_INFO)
async def info_reservation(message: types.Message, state: FSMContext):
    info = message.text.lower()
    if info == "отмена":
        # If the user input is "отмена", finish the state
        await state.finish()
        await message.answer("Вы отменили операцию бронирования.")
        return

    try:
        chat_id = message.chat.id
        telegram_username = message.from_user.username
        # Извлечение даты
        date_start = info.find("дата: ") + len("дата: ")
        date_end = info.find("\n", date_start)
        date = info[date_start:date_end].strip()  # Удаляем лишние пробелы

        # Извлечение времени
        time_start = info.find("время: ") + len("время: ")
        time_end = info.find("\n", time_start)
        time = info[time_start:time_end].strip()  # Удаляем лишние пробелы

        # Извлечение количества гостей
        guests_start = info.find("количество гостей: ") + len("количество гостей: ")
        guests = int(info[guests_start:].strip())  # Удаляем лишние пробелы и преобразуем в целое число


        # Проверка наличия ключевых слов
        if not (date and time and guests):
            raise ValueError("Отсутствуют ключевые слова")

        if check_reservation_on_bd(date,time,guests, chat_id, telegram_username):
            await message.answer(text="Стол зарезервирован")
            await message.answer(
                f'Ваше бронирование :\nДата: {date} \nВремя: {time} \nКоличество гостей: {guests} ')
        else:
            await message.answer(text="Извините, нет мест на выбранный день")

        # Сброс состояния FSMContext
        await state.finish()

    except Exception as e:
        # Обработка некорректного ввода
       # print("Некорректный ввод:", e)
        await message.answer("Некорректный ввод. Пожалуйста, убедитесь, что вы ввели данные в правильном формате.")

@dp.message_handler(state=AddReservationStates.WAITING_FOR_INFO_NEW)
async def infooh_reservation(message: types.Message, state: FSMContext):
    info = message.text.lower()
    if info == "отмена":
        # If the user input is "отмена", finish the state
        await state.finish()
        await message.answer("Вы отменили операцию бронирования.")
        return

    try:
        chat_id = message.chat.id
        telegram_username = message.from_user.username

        # Извлечение имени
        name_start = info.find("имя: ") + len("имя: ")
        name_end = info.find("\n", name_start)
        name = info[name_start:name_end].strip()  # Удаляем лишние пробелы

        # Извлечение даты
        date_start = info.find("дата: ") + len("дата: ")
        date_end = info.find("\n", date_start)
        date = info[date_start:date_end].strip()  # Удаляем лишние пробелы

        # Извлечение времени
        time_start = info.find("время: ") + len("время: ")
        time_end = info.find("\n", time_start)
        time = info[time_start:time_end].strip()  # Удаляем лишние пробелы

        # Извлечение количества гостей
        guests_start = info.find("количество гостей: ") + len("количество гостей: ")
        guests = int(info[guests_start:].strip())  # Удаляем лишние пробелы и преобразуем в целое число

        # Проверка наличия ключевых слов
        if not (name and date and time and guests):
            raise ValueError("Отсутствуют ключевые слова")

        if check_reservation_on_bd_2(name, date, time, guests, chat_id, telegram_username):
            await message.answer(text="Стол зарезервирован")
            await message.answer(
                f'Ваше бронирование :\nДата: {date} \nВремя: {time} \nКоличество гостей: {guests} ')
        else:
            await message.answer(text="Извините, нет мест на выбранный день")

        # Сброс состояния FSMContexts
        await state.finish()

    except Exception as e:
        # Обработка некорректного ввода
        #print("Некорректный ввод:", e)
        await message.answer("Некорректный ввод. Пожалуйста, убедитесь, что вы ввели данные в правильном формате.")


@dp.message_handler(state=AddClientStates.WAITING_FOR_CLIENT_NAME)
async def entrance_client_name(message: types.Message, state: FSMContext):
    entrance_client_name = message.text.split()
    await state.update_data(client_name=entrance_client_name)
    await message.answer('Введите дату рождения клиента (в формате ДД.ММ.ГГГГ).')
    await AddClientStates.WAITING_FOR_CLIENT_DOB.set()

@dp.message_handler(state=AddClientStates.WAITING_FOR_CLIENT_DOB)
async def entrance_dob(message: types.Message, state: FSMContext):
    entrance_dob = message.text
    await state.update_data(client_dob=entrance_dob)
    await message.answer('Введите логин клиента в Telegram')
    await AddClientStates.WAITING_FOR_CLIENT_USERNAME.set()

@dp.message_handler(state=AddClientStates.WAITING_FOR_CLIENT_USERNAME)
async def entrance_client_username(message: types.Message, state: FSMContext):
    entrance_client_username = message.text
    data = await state.get_data()
    client_name = data['client_name']
    client_dob = data['client_dob']
    await state.update_data(client_username=entrance_client_username)
    await message.answer('Введите номер телефона клиента')
    await AddClientStates.WAITING_FOR_CLIENT_PHONE_NUMBER.set()

@dp.message_handler(state=AddClientStates.WAITING_FOR_CLIENT_PHONE_NUMBER)
async def entrance_client_phone_number(message: types.Message, state: FSMContext):
    entrance_client_phone_number = message.text
    data = await state.get_data()
    client_name = data['client_name']
    client_dob = data['client_dob']
    client_username = data['client_username']
    add_client(client_name, client_dob, client_username, entrance_client_phone_number)

    await message.answer('Клиент добавлен')

    # Сброс состояния FSMContext
    await state.finish()

@dp.message_handler(state=AddModerStates.WAITING_FOR_MODER_USERNAME)
async def entrance_moder_username(message: types.Message, state: FSMContext):
    entrance_moder_username = message.text
    await state.update_data(moder_username=entrance_moder_username)
    await message.answer('Введите пароль модератора')
    await AddModerStates.WAITING_FOR_MODER_PASSWORD.set()


@dp.message_handler(state=AddModerStates.WAITING_FOR_MODER_PASSWORD)
async def entrance_moder_password(message: types.Message, state: FSMContext):
    entrance_moder_password = message.text
    await state.update_data(moder_password=entrance_moder_password)
    data = await state.get_data()
    moder_username = data['moder_username']
    moder_password = data['moder_password']
    add_moderator(moder_username, moder_password)
    await message.answer(f'Модератор {moder_username} добавлен')
    # Сброс состояния FSMContext
    await state.finish()


@dp.message_handler(state=DeleteStates.WAITING_FOR_DELETE_USERNAME)
async def delete_username(message: types.Message, state: FSMContext):
    delete_username = message.text
    delete_user(delete_username)
    await message.answer(f'Пользователь {delete_username} удален')
    # Сброс состояния FSMContext
    await state.finish()
# Обработчик логина при входе
@dp.message_handler(state=EntranceStates.WAITING_FOR_USERNAME)
async def entrance_username(message: types.Message):
    global entrance_username
    entrance_username = message.text
    await message.answer('Введите пароль')
    await EntranceStates.WAITING_FOR_PASSWORD.set()

# Обработчик пароля при входе
@dp.message_handler(state=EntranceStates.WAITING_FOR_PASSWORD)
async def entrance_password(message: types.Message, state: FSMContext):
    global entrance_password
    entrance_password = message.text
    access_level = check_user_bd(entrance_username, entrance_password)

    if access_level == "kbsuper":
        await message.answer(f"Здравствуйте, {entrance_username}!", reply_markup=admin_ikb)
    elif access_level == "kb":
        await message.answer(f"Здравствуйте, {entrance_username}!", reply_markup=moder_ikb)
    else:
        await message.answer("Такого аккаунта не существует")
    await state.finish()

if __name__ == '__main__':
    # executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
    loop = asyncio.get_event_loop()
    loop.create_task(schedule_birthday_greetings(dp))
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)