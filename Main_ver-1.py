# libraries
import telebot
import sqlite3
import datetime

# connecting with a bot
bot = telebot.TeleBot('8158733015:AAHhE_5JMUCs0rRXL8zGocmZo27JpxI0POc')


# creating menu of the categories (command - start)
@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('base.sql')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS records (id INTEGER PRIMARY KEY, '
                'date DATE, category varchar(50), amount float, info varchar(100))')
    conn.commit()
    cur.close()
    conn.close()

    # category buttons
    markup = telebot.types.InlineKeyboardMarkup()
    cat_btn1 = telebot.types.InlineKeyboardButton('Housing & Studies', callback_data='Housing & Studies')
    cat_btn2 = telebot.types.InlineKeyboardButton('Groceries', callback_data='Groceries')
    cat_btn3 = telebot.types.InlineKeyboardButton('Transportation', callback_data='Transportation')
    markup.row(cat_btn1, cat_btn2, cat_btn3)
    cat_btn4 = telebot.types.InlineKeyboardButton('Clothing & Shoes', callback_data='Clothing & Shoes')
    cat_btn5 = telebot.types.InlineKeyboardButton('Body Care & Med.', callback_data='Body Care & Med.')
    cat_btn6 = telebot.types.InlineKeyboardButton('Media & Washing', callback_data='Media & Washing')
    markup.row(cat_btn4, cat_btn5, cat_btn6)
    cat_btn7 = telebot.types.InlineKeyboardButton('Fun & Vacation', callback_data='Fun & Vacation')
    cat_btn8 = telebot.types.InlineKeyboardButton('Emergency', callback_data='Emergency')
    cat_btn9 = telebot.types.InlineKeyboardButton('Other', callback_data='Other')
    markup.row(cat_btn7, cat_btn8, cat_btn9)
    cat_btn10 = telebot.types.InlineKeyboardButton('Check the data base', callback_data='check_first')
    markup.add(cat_btn10)

    bot.send_message(message.chat.id, "Choose the category below:", reply_markup=markup)


# making a functionality of the buttons and providing a data (category, amount)
@bot.callback_query_handler(func=lambda callback: callback.data in ['Housing & Studies', 'Groceries', 'Transportation',
                                                                    'Clothing & Shoes', 'Body Care & Med.',
                                                                    'Media & Washing', 'Fun & Vacation',
                                                                    'Emergency', 'Other', 'check_first'])
def callback_message(callback):
    if callback.data != 'check_first':

        # defining the date (time and day)
        day = datetime.date.today().strftime("%x")
        time = datetime.datetime.now().strftime("%X")
        date = f"{day}, {time}"

        info = None

        # inform the user to enter the amount
        bot.send_message(callback.message.chat.id, f"Great, record {callback.data} was saved! Enter the amount:")

        # store `callback.data` in a global or state to access it later in `amount`
        bot.register_next_step_handler(callback.message, adding, callback.data, date, info)
    else:
        # query database and show records
        conn = sqlite3.connect('base.sql')
        cur = conn.cursor()
        cur.execute("SELECT * FROM records")
        records = cur.fetchall()
        cur.close()
        conn.close()

        if records:
            info = ''
            for el in records:
                info += (f"\n<b>DATE</b>: {el[1]}; <b>CATEGORY</b>: {el[2]}; <b>AMOUNT</b>: {el[3]}, Info: {el[4]}\n"
                         f"-----------------------------------------------------------------------------------")
            bot.send_message(callback.message.chat.id, info, parse_mode='html')
            start(callback.message)
        else:
            bot.send_message(callback.message.chat.id, "Database is empty!")
            start(callback.message)


def adding(message, category, date, info):
    # process and save the amount to the database
    num = message.text
    bot.send_message(message.chat.id, f"Ok, the amount {num} was added to data base!")

    # database operations with parameterized query
    conn = sqlite3.connect('base.sql')
    cur = conn.cursor()
    cur.execute("INSERT INTO records (category, amount, date, info) VALUES('%s', '%s', '%s', '%s')" % (category, num, date, info))
    conn.commit()
    cur.close()
    conn.close()

    cont(message)


def cont(message):
    # 'yes'&'no' buttons
    markup = telebot.types.InlineKeyboardMarkup()
    end_btn1 = telebot.types.InlineKeyboardButton('Yes', callback_data='yes')
    end_btn2 = telebot.types.InlineKeyboardButton('No', callback_data='no')
    markup.row(end_btn1, end_btn2)
    markup.add(telebot.types.InlineKeyboardButton('Ckeck the database', callback_data='check_second'))
    bot.send_message(message.chat.id, "Do you want to continue?", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data in ['yes', 'no', 'check_second'])
def callback_con(callback):
    if callback.data == 'yes':
        start(callback.message)
    elif callback.data == 'no':
        bot.send_message(callback.message.chat.id, "Ok, enter /start to continue")
    else:
        # query database and show records
        conn = sqlite3.connect('base.sql')
        cur = conn.cursor()
        cur.execute("SELECT * FROM records")
        records = cur.fetchall()
        cur.close()
        conn.close()
        info = ''
        for el in records:
            info += (f"\n<b>DATE</b>: {el[1]}; <b>CATEGORY</b>: {el[2]}; <b>AMOUNT</b>: {el[3]}\n"
                     f"-----------------------------------------------------------------------------------")
        bot.send_message(callback.message.chat.id, info, parse_mode='html')
        bot.send_message(callback.message.chat.id, "Ok, enter /start to continue")


bot.infinity_polling()