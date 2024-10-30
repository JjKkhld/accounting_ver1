# libraries
import telebot
import sqlite3
import datetime

# connecting with a bot
bot = telebot.TeleBot('8158733015:AAHhE_5JMUCs0rRXL8zGocmZo27JpxI0POc')


"""SECTION 1 - Basic functionality like creating a database, providing the data and adding buttons"""


# crating a menu of commands
commands = [
    telebot.types.BotCommand('providing_data', 'Provide data!'),
    telebot.types.BotCommand('reports', 'Get some reports!')
]
bot.set_my_commands(commands)


# starting a bot
@bot.message_handler(commands=['start'])
def start_func(message):
    bot.send_message(message.chat.id, "Hello, go to the menu in the left side of message field!")


# creating a database
@bot.message_handler(commands=['providing_data'])
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
    markup.add(telebot.types.InlineKeyboardButton('Check the data base', callback_data='check_first'))
    markup.add(telebot.types.InlineKeyboardButton('Clear the database', callback_data='delete'))

    bot.send_message(message.chat.id, "Choose the category below:", reply_markup=markup)


# making a functionality of the buttons and providing a data (category, amount)
@bot.callback_query_handler(func=lambda callback: callback.data in ['Housing & Studies', 'Groceries', 'Transportation',
                                                                    'Clothing & Shoes', 'Body Care & Med.',
                                                                    'Media & Washing', 'Fun & Vacation',
                                                                    'Emergency', 'Other', 'check_first', 'delete'])
def callback_message(callback):
    if callback.data == 'delete':
        conn = sqlite3.connect('base.sql')
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS records;')
        conn.commit()
        cur.close()
        conn.close()
        bot.send_message(callback.message.chat.id, "The database was deleted! Press /providing_data to continue")
    elif callback.data != 'check_first':

        # defining the date (time and day)
        day = datetime.date.today().strftime("%x")
        time = datetime.datetime.now().strftime("%X")
        date = f"{day}, {time}"

        if callback.data == 'Other':
            # Ask for a description for the "Other" category
            bot.send_message(callback.message.chat.id, "Enter a description:")
            bot.register_next_step_handler(callback.message, get_desc, date)
        else:
            # inform the user to enter the amount
            bot.send_message(callback.message.chat.id, f"Great, record {callback.data} was saved! Enter the amount:")

            # store `callback.data` in a global or state to access it later in `amount`
            bot.register_next_step_handler(callback.message, adding, callback.data, date, None)
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
                info += (f"\n<b>DATE</b>: {el[1]}; <b>CATEGORY</b>: {el[2]}; <b>AMOUNT</b>: {el[3]}\n"
                         f"-----------------------------------------------------------------------------------")
            bot.send_message(callback.message.chat.id, info, parse_mode='html')
            start(callback.message)
        else:
            bot.send_message(callback.message.chat.id, "Database is empty! Press /providing_data to enter a data")


def get_desc(message, date):
    # Save the description and ask for the amount
    description = message.text
    bot.send_message(message.chat.id, "Enter the amount for Other:")
    bot.register_next_step_handler(message, adding, 'Other', date, description)


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
    markup.add(telebot.types.InlineKeyboardButton('Check the database', callback_data='check_second'))
    markup.add(telebot.types.InlineKeyboardButton('Clear the database', callback_data='delete'))
    bot.send_message(message.chat.id, "Do you want to continue?", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: callback.data in ['yes', 'no', 'check_second', 'delete'])
def callback_con(callback):
    if callback.data == 'yes':
        start(callback.message)
    elif callback.data == 'no':
        bot.send_message(callback.message.chat.id, "Ok, enter /providing_data to continue")
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
        bot.send_message(callback.message.chat.id, "Ok, enter /providing_data to continue")


"""SECTION 2 - Basic functionality like creating a database, providing the data and adding buttons"""


@bot.message_handler(commands=['reports'])
def func(message):
    markup = telebot.types.ReplyKeyboardMarkup()
    btn1 = telebot.types.KeyboardButton("Daily report")
    btn2 = telebot.types.KeyboardButton("Weekly report")
    markup.row(btn1, btn2)
    btn3 = telebot.types.KeyboardButton("Daily report of the specific category")
    btn4 = telebot.types.KeyboardButton("Weekly report of the specific category")
    markup.row(btn3, btn4)
    bot.send_message(message.chat.id, "Here you can get a report. Choose which one you want get", reply_markup=markup)
    bot.register_next_step_handler(message, on_click)


def on_click(message):

    # defining the day
    day = datetime.date.today().strftime("%x")

    conn = sqlite3.connect('base.sql')
    cur = conn.cursor()
    if message.text == "Daily report":
        cur.execute("SELECT * FROM records WHERE date LIKE '{}%'".format(day))
        records = cur.fetchall()
        if records:
            info = ''
            for el in records:
                info += (f"\n<b>DATE</b>: {el[1]}; <b>CATEGORY</b>: {el[2]}; <b>AMOUNT</b>: {el[3]}\n"
                     f"-----------------------------------------------------------------------------------")
            bot.send_message(message.chat.id, info, parse_mode='html')
        else:
            bot.send_message(message.chat.id, "There are no records from this day, go back to /reports")


    elif message.text == "Weekly report":
        bot.send_message(message.chat.id, "Ok, it's weekly rep.")
    elif message.text == "Daily report of the specific category":
        bot.send_message(message.chat.id, "Ok, it's daily report of the specific category")
    else:
        bot.send_message(message.chat.id, "Ok, it's weekly report of the specific category")
    cur.close()
    conn.close()


bot.infinity_polling()