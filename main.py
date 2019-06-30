# -*- coding: utf-8 -*-
import telebot
import os
import datetime
import random
import sqlite3
import time
import logging
from flask import Flask, request


conn = sqlite3.connect('all_db.sqlite', check_same_thread=False)
cur = conn.cursor()

event = []
commands = ['Сколько дней мы вместе?', 'Рандомная фотка', 'Показать все фотки']
board = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
for c in commands:
    board.add(c)

currentDateTime = datetime.datetime.today()
ourTime = datetime.datetime(2017, 9, 4)
delta = currentDateTime - ourTime
strDelta = str(delta.days)

chat_id_angelina = '399683820'
chat_id_misha = '216036961'
token = '484695046:AAHdIL-gVwIGzbA2-KQAOsi2R5v3P-I-oO8'
bot = telebot.TeleBot(token)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


def log(s):
    f = open('log.log', 'a')
    f.write(str(datetime.datetime.today()) + '\t')
    f.write(s)
    f.write('\n')
    f.close()


@bot.message_handler(commands=["start"])
def handle_start(message):
    log(str(message.chat.id) + ':start')
    s = "Ангелина, Привет! Меня зовут НашБот. Я был разработан в честь полгода отношений с Мишей, с чем тебя и поздравляю " + u'\U0001F618'
    bot.send_message(message.chat.id, s, reply_markup=board)


@bot.message_handler(commands=['help'])
def handle_help(message):
    log(str(message.chat.id) + ':help')
    bot.send_message(message.chat.id,
                     "Сломался бот? Обратись к этому красавчику @pythonyasha. Говорят, он крутой, потому что встречается с тобой ;)",reply_markup=board)


@bot.message_handler(func=lambda message: message.text == 'Рандомная фотка')
def randomPhoto(message):
    log(str(message.chat.id) + ':randomphoto')
    sql = 'SELECT * FROM Photos'
    cur.execute(sql)
    row = cur.fetchone()
    c = 1
    if row is not None:
        while row is not None:
            row = cur.fetchone()
            c = c + 1
        print('c=', c)
        rnd = random.randint(1, c)
        print('rnd=', rnd)
        cur.execute(sql)
        for i in range(1, c):
            row = cur.fetchone()
            if i == rnd:
                row = str(row)
                print('row=', row)
                bot.send_photo(message.chat.id, row[2:(len(row) - 3)])
    else:
        bot.send_message(message.chat.id, 'Отсутвуют фотографии')
    conn.commit()


def checktime(s):
    try:
        hours = s[0:2]
        min = s[3:]
        print('hours=', hours)
        print('min=', min)
        if 0 <= int(hours) <= 23:
            if 0 <= int(min) <= 59:
                return True
            else:
                return False
        else:
            return False
    except:
        return False


def checkdate(s):
    year = datetime.datetime.today().year
    leap_year = False
    if year % 400 == 0:
        leap_year = True
    else:
        if year % 4 == 0:
            if year % 100 != 0:
                leap_year = True
    month30 = ['апреля', 'июня', 'сентября', 'ноября']
    month31 = ['января', 'марта', 'мая', 'июля', 'августа', 'октября', 'ноября', 'декабря']
    day = s[0]
    month = ''
    if s[1] == ' ':
        month = s[2:]
    else:
        day = day + s[1]
        month = s[3:]
    flag = 0
    for m in month30:
        if m == month:
            flag = 30
    for m in month31:
        if m == month:
            flag = 31
    if month == 'февраля':
        if leap_year:
            flag = 29
        else:
            flag = 28
    if flag == 0:
        return False
    elif flag == 30 or flag == 31 or flag == 28 or flag == 29:
        if 1 <= int(day) <= flag:
            return True
        else:
            return False
    else:
        return False


@bot.message_handler(func=lambda message: message.text == 'Сколько дней мы вместе?')
def timeTogether(message):
    log(str(message.chat.id) + ':timetogether')
    day = ""
    if int(strDelta[-1]) == 1:
        day = " день"
    elif int(strDelta[-1]) == 2 or int(strDelta[-1]) == 3 or int(strDelta[-1]) == 4:
        day = " дня"
    else:
        day = " дней"
    s = "Мы вместе уже " + str(delta.days) + day
    bot.send_message(message.chat.id, s, reply_markup=board)


@bot.message_handler(func=lambda message: message.text == 'Показать все фотки')
def showphotos(message):
    log(str(message.chat.id) + ':show_photos')
    bot.send_message(message.chat.id, 'Начинается загрузка всех фотографий')
    cur.execute("SELECT * FROM Photos")
    row = cur.fetchone()
    while row is not None:
        row = str(row)
        bot.send_photo(message.chat.id, row[2:(len(row) - 3)])
        print(row)
        row = cur.fetchone()
        time.sleep(0.33)
    bot.send_message(message.chat.id, 'Загрузка фото завершена', reply_markup=board)
    conn.commit()


@bot.message_handler(content_types=['photo'])
def photo(message):
    log(str(message.chat.id) + ':uploading photo')
    print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    print('fileID =', fileID)
    sql = "INSERT INTO Photos VALUES ('" + fileID + "')"
    cur.execute(sql)
    conn.commit()
    bot.send_message(message.chat.id, "Фотка загружена", reply_markup=board)


def admin_message(message):
    text = bot.send_message(chat_id_misha, 'Админский текст:')
    bot.register_next_step_handler(text, sendadmintext)


def sendadmintext(message):
    bot.send_message(chat_id_angelina, message.text, reply_markup=board)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    print('chat.id=', message.chat.id)
    if message.text == 'odmin':
        admin_message(message)
    elif message.text == 'clsLog':
        f = open('log.log', 'w')
        f.close()
    else:
        bot.send_message(message.chat.id, "Не грузи плиз", reply_markup=board)

# @bot.message_handler(func=lambda message: message.text == 'Создать свидание')
# def handle_event(message):
#     log(str(message.chat.id) + ':event')
#     bot.send_message(message.chat.id, "Ого! Ты хочешь назначить новую встречу со своей половинкой? Замечательно!")
#     time_event = bot.send_message(message.chat.id, '1. Время встречи (Формат ЧЧ:ММ)')
#     bot.register_next_step_handler(time_event, date_event)


# def date_event(message):
#     if checktime(message.text):
#         pass
#     else:
#         bot.reply_to(message, 'Неверный формат')
#         handle_event(message)
#         return
#     event.append(message.text)
#     day = bot.send_message(message.chat.id, "2. Дата встречи (Введи число и месяц. Например, '4 сентября')")
#     bot.register_next_step_handler(day, place_event)


# def place_event(message):
#     if checkdate(message.text):
#         pass
#     else:
#         bot.reply_to(message, 'Неверный формат')
#         handle_event(message)
#         return
#     event.append(message.text)
#     place = bot.send_message(message.chat.id, '3. Где встреча?')
#     bot.register_next_step_handler(place, insert_db)


# def insert_db(message):
#     event.append(message.text)
#     sql = "INSERT INTO Events VALUES ('" + event[0] + "', '" + event[1] + "','" + event[2] + "')"
#     bot.send_message(message.chat.id, "Свидание успешно добавлено")
#     cur.execute(sql)
#     conn.commit()
#     event.clear()

# @bot.message_handler(func=lambda message: message.text == 'Показать все свидания')
# def handle_allevents(message):
#     log(str(message.chat.id) + ':allevents')
#     cur.execute("SELECT * FROM Events")
#     row = cur.fetchone()
#     mess = ''
#     if row is not None:
#         bot.send_message(message.chat.id, "Вот список ваших свиданий:")
#         while row is not None:
#             text = row[0] + "\t" + row[1] + '\t' + row[2]
#             mess = mess + "\n" + text
#             row = cur.fetchone()
#         bot.send_message(message.chat.id, mess)
#     else:
#         bot.send_message(message.chat.id,
#                          "Список свидание пуст :(\nВоспользуйтесь командой 'Создать свидание' на кливиатуре для создания нового свидания")


# Проверим, есть ли переменная окружения Хероку (как ее добавить смотрите ниже)
if "HEROKU" in list(os.environ.keys()):
    print('heroku')
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)
    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200
    @server.route("/")
    def webhook():
        
        bot.remove_webhook()
        bot.set_webhook(url="https://ourtelegrambot.herokuapp.com/") # этот url нужно заменить на url вашего Хероку приложения
        return "?", 200
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
else:
    # если переменной окружения HEROKU нету, значит это запуск с машины разработчика.  
    # Удаляем вебхук на всякий случай, и запускаем с обычным поллингом.
    print('not heroku')
    logger = telebot.logger
    telebot.logger.setLevel(logging.INFO)

    server = Flask(__name__)
    @server.route("/bot", methods=['POST'])
    def getMessage():
        bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
        return "!", 200
    @server.route("/")
    def webhook():
        
        bot.remove_webhook()
        bot.set_webhook(url="https://ourtelegrambot.herokuapp.com/") # этот url нужно заменить на url вашего Хероку приложения
        return "?", 200
    server.run(host="0.0.0.0", port=os.environ.get('PORT', 80))
    #bot.polling(none_stop=True)