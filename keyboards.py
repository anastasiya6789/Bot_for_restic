from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

# Функция для создания клавиатуры с кнопками "Вперед" и "Назад"

default_ikb = InlineKeyboardMarkup()
ikb1 = InlineKeyboardButton('Забронировать стол', callback_data='addReservation')
ikb2 = InlineKeyboardButton('Перейти на сайт', callback_data='websity')
ikb3 = InlineKeyboardButton('Посмотреть актуальное меню', callback_data='menu_pdf')
ikb4 = InlineKeyboardButton('Открыть номер телефона', callback_data='number_phone')
ikb5 = InlineKeyboardButton('Режим работы', callback_data='opening_hours')
ikb6 = InlineKeyboardButton('Актуальные спецпредложения', callback_data='info_promotion')

default_ikb.row(ikb1)
default_ikb.row(ikb2, ikb3)
default_ikb.row(ikb4, ikb5)
default_ikb.row(ikb6)

default_kb=ReplyKeyboardMarkup(resize_keyboard=True) # параметр one_time_keyboard=False чтобы клавиатура не пропадала
b1=KeyboardButton('/menu')
default_kb.add(b1)

entrance_ikb=InlineKeyboardMarkup(row_width=2)
ib1=InlineKeyboardButton('Вход',
                         callback_data='entrance')

entrance_ikb.add(ib1)

moder_ikb=InlineKeyboardMarkup(row_width=2)
ib1=InlineKeyboardButton('Узнать бронь',
                         callback_data='reservation')
moder_ikb.add(ib1)

admin_ikb=InlineKeyboardMarkup(row_width=2)
ib1=InlineKeyboardButton('Узнать бронь',
                         callback_data='reservation')
ib2=InlineKeyboardButton('Удалить менеджера',
                         callback_data='deleteModer')
ib3=InlineKeyboardButton('Добавить менеджера',
                         callback_data='addModer')
ib4=InlineKeyboardButton('Добавить постоянного клиента',
                         callback_data='addClient')

admin_ikb.add(ib4).add(ib3).add(ib2).add(ib1)

reservation_ikb=InlineKeyboardMarkup(row_width=2)
ib1=InlineKeyboardButton('Забронировать стол',
                         callback_data='addReservation')
reservation_ikb.add(ib1)

check_ikb=InlineKeyboardMarkup(row_width=2)
ib1=InlineKeyboardButton('Подтвердить',
                         callback_data='checkDatabaseReservation')
ib2=InlineKeyboardButton('Ввести заново',
                         callback_data='addReservation')
check_ikb.add(ib1,ib2)

