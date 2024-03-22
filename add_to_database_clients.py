import pandas as pd
import sqlite3

con = sqlite3.connect('Gaudi_bot.db')
cur = con.cursor()

df = pd.read_excel('clients_to_add.xlsx')

for index, row in df.iterrows():
    first_name = row['имя']
    phone_number = row['номер телефона']
    dob = row['дата рождения']


    cur.execute("INSERT INTO clients (firstName, dateOfBirth, phone_number) VALUES (?, ?, ?)",
                (first_name, dob, phone_number))

con.commit()
con.close()