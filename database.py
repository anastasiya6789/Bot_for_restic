import sqlite3 as sql

def check_client_bd(chat_id):
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()

    query = f"SELECT * FROM clients WHERE chatId='{chat_id}' "
    cur.execute(query)
    result = cur.fetchone()
    cur.close()
    con.close()
    if result:
        return True
    else:
        return False
def check_user_bd(entrance_username, entrance_password):
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()

    query = f"SELECT * FROM moder WHERE login='{entrance_username}' AND password='{entrance_password}'"
    cur.execute(query)
    result = cur.fetchone()

    cur.close()
    con.close()

    if result:
        if result[3] == 1:  # Проверяем значение столбца access (индекс 3 в кортеже)

            return "kbsuper"  # Возвращаем 'kbsuper', если access равен 1
        else:

            return "kb"  # Возвращаем 'kb', если access равен 0

    return None  # Возвращаем None, если пользователя не существует

def get_reservation_data():
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()

    # Выполните запрос к базе данных для получения данных о забронированных столиках
    query = "SELECT * FROM reservation"
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    con.close()

    # Преобразуйте результат в список, где каждый элемент представляет собой строку данных
    table_data = []
    for row in result:
        table_data.append(row)
    return table_data

def get_users_with_access_0():
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()
    query = "SELECT login FROM moder WHERE access = 0"
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    con.close()
    user_logins = [row[0] for row in result]
    return user_logins

def delete_user(username):
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()
    query = f"DELETE FROM moder WHERE login = '{username}'"
    cur.execute(query)
    con.commit()
    cur.close()
    con.close()

def add_moderator(username, password):
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()

    query = f"INSERT INTO moder (login, password, access) VALUES ('{username}', '{password}', 0)"
    cur.execute(query)
    con.commit()

    cur.close()
    con.close()

def add_client(client_name, client_dob, client_username, entrance_client_phone_number):
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()

    query = f"INSERT INTO clients (lastName, firstName, surName, dateOfBirth, userName, phone_number) " \
            f"VALUES ('{client_name[0]}', '{client_name[1]}', '{client_name[2]}', '{client_dob}', '{client_username}', '{entrance_client_phone_number}')"
    cur.execute(query)
    con.commit()

    cur.close()
    con.close()


def check_table(guests):
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()

    # Получаем все столы, отсортированные по возрастанию вместимости
    query = "SELECT table_number, capacity FROM tables WHERE capacity >= ? ORDER BY capacity"
    cur.execute(query, (guests,))
    result = cur.fetchall()

    tables = [row[0] for row in result]

    cur.close()
    con.close()
   # print(tables)

    return tables


def check_reservation_on_bd(date, time, guests, chat_id, telegram_username):
    tables = check_table(guests)  # Предположим, что у вас уже есть реализация функции check_table
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()

    # Определим временные границы для поиска свободных столов
    start_time = time_minus_5_hours(time)
    end_time = time_plus_5_hours(time)

    # Проверяем каждый стол из списка tables
    for table in tables:
        # Формируем SQL-запрос для проверки наличия резервации
        query = "SELECT * FROM reservation WHERE table_number=? AND date=? AND time BETWEEN ? AND ?"
        cur.execute(query, (table, date, start_time, end_time))

        if cur.fetchone() is None:
            query_1 = "SELECT firstName, phone_number FROM clients WHERE chatId=?"
            cur.execute(query_1, (chat_id,))
            result = cur.fetchone()
            if result:
                firstName, phone_number = result

                # Если не найдено резерваций, добавляем новую запись в базу данных
                insert_query = "INSERT INTO reservation (date, table_number, time, name, userName, phoneNumber) VALUES (?, ?, ?, ?, ?,?)"
                cur.execute(insert_query, (date, table, time, firstName, telegram_username, phone_number))

                con.commit()
                con.close()

                return True

    con.close()
    return False

def check_reservation_on_bd_2(name, date, time, guests, chat_id, telegram_username):
    tables = check_table(guests)  # Assuming you already have the implementation of the check_table function
    con = sql.connect('Gaudi_bot.db')
    cur = con.cursor()

    # Define the time boundaries for searching available tables
    start_time = time_minus_5_hours(time)
    end_time = time_plus_5_hours(time)

    # Check each table from the tables list
    for table in tables:
        # Formulate the SQL query to check for existing reservations
        query = "SELECT * FROM reservation WHERE table_number=? AND date=? AND time BETWEEN ? AND ?"
        cur.execute(query, (table, date, start_time, end_time))

        if cur.fetchone() is None:
            query_1 = "SELECT phone_number FROM clients_default WHERE chatId=?"
            cur.execute(query_1, (chat_id,))
            result = cur.fetchone()
            if result:
                phone_number = result[0]
              #  print(phone_number)
              #  print(name)
              #  print(date)
               # print(table)
               # print(telegram_username)


                # If no reservations are found, add a new entry to the database
                insert_query = "INSERT INTO reservation (name, date, table_number, time, userName, phoneNumber) VALUES (?, ?, ?, ?, ?, ?)"
                cur.execute(insert_query, (name, date, table, time, telegram_username, phone_number))

                con.commit()
                con.close()
               # print("OK")

                return True

    con.close()
    return False



# Функция для вычисления времени минус 5 часов
def time_minus_5_hours(time):
    hour, minute = time.split(':')
    hour = int(hour)

    minute = int(minute)


    # Вычитаем 5 часов
    hour -= 3

    # Обрабатываем случай, когда результат может быть отрицательным
    if hour < 0:
        hour += 24

    # Возвращаем строковое представление времени

    return f"{hour:02d}:{minute:02d}"


# Функция для вычисления времени плюс 5 часов
def time_plus_5_hours(time):
    hour, minute = time.split(':')
    hour = int(hour)
    minute = int(minute)

    # Добавляем 5 часов
    hour += 3

    # Обрабатываем случай, когда результат превышает 23:59
    if hour >= 24:
        hour -= 24

    # Возвращаем строковое представление времени
    return f"{hour:02d}:{minute:02d}"


#check_reservation_on_bd_2("Анастасия", "2003.12.02", "16:00", 8, "555", "telegram_username")


