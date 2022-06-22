import telebot, random
from datetime import date
import config
import utils

# from dialog import Dialog
# from shedule import Shedule

bot = telebot.TeleBot(token=config.token)
msgCounter = 0 # records counter that`s used to see user msgs in admin menu
userDB = utils.UserDB()
boarDB = utils.BoarDB()
adminJokeDB = utils.JokeDB("adminJokes")
userJokeDB = utils.JokeDB("userJokes")
msgDB = utils.MsgDB()
adminPicDB = utils.PicDB("accPics")
adminMenu = utils.Menu()
userMenu = utils.Menu()
helpMenu = utils.Menu()

# soon...
# shed = Shed()
# dialog = Dialog()

helpMenu.setMsg(config.helpMsg)
adminMenu.setMsg(config.adminMsg)
adminMenu.setInlineKeyboard(config.adminKeys)
adminMenu.rowInlineKeyboard()
userMenu.setMsg(config.userMsg)
userMenu.setInlineKeyboard(config.userKeys)
userMenu.rowInlineKeyboard()


@bot.message_handler(commands=["start"])
def start(message):
    keyboard = utils.ReplyKeyboard()
    keyboard.add(config.startKeys)
    keyboard.autoRow()
    bot.send_message(message.chat.id, "Вечер в хату, кабан {0.first_name}!"
        .format(message.from_user, bot.get_me()), reply_markup=keyboard.get())


@bot.message_handler(commands=["auth"])
def auth(message):
    # as long as ...user.id is integer, userID get it in string to be recorded to DB (column has string type)
    userID = str(message.from_user.id) 
    if userID == str(config.adminID):
        admin(message)
    else:
        usersList = userDB.getUsersList()
        if userID not in usersList:
            userDB.addUser(userID)
            user(message)
        else:
            user(message)


def admin(message):
    bot.send_message(message.chat.id, adminMenu.getMsg(), reply_markup=adminMenu.getInlineKeyboard())


def user(message):
    bot.send_message(message.chat.id, userMenu.getMsg(), reply_markup=userMenu.getInlineKeyboard()) 


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, helpMenu.getMsg(), parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
def callWorker(call):
    global msgCounter 


    if call.data == 'Загрузить картинку': #+
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Пришли картинку, или нажми /brake", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.register_next_step_handler(call.message, uploadPicture)
    elif call.data == 'Загрузить анекдот': #+
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Напиши анекдот, или нажми /brake", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.register_next_step_handler(call.message, uploadJoke)
    elif call.data == "Остановить бота": #+
        bot.answer_callback_query(call.id, 'Бот остановлен')
        utils.log.info("ОСТАНОВКА БОТА")
        bot.stop_polling()
    elif call.data == "Анекдоты": #+
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        see_jokes(call.message)
    elif call.data == "Выйти": #+
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text=adminMenu.getMsg(), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=adminMenu.getInlineKeyboard())
    elif call.data == "Далее": #joke
        msgCounter += 1
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        see_jokes(call.message)
    elif call.data == "Далее>>": #msg
        msgCounter += 1
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        seeMsgs(call.message)
    elif call.data == "Принять": #joke
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        adminJokeDB.newRecord(userJokeDB.getJoke(msgCounter))
        userJokeDB.delRecord(userJokeDB.getJoke(msgCounter))
        msgCounter += 1
        see_jokes(call.message)
    elif call.data == "Удалить": #joke
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        userJokeDB.delRecord(userJokeDB.getJoke(msgCounter))
        msgCounter = 0
        see_jokes(call.message)
    elif call.data == "Вычеркнуть": #msg
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msgDB.delRecord(msgDB.seeMsg(msgCounter))
        msgCounter = 0
        seeMsgs(call.message)
    elif call.data == "Рассылка": #+
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Напиши сообщение пользователям", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.register_next_step_handler(call.message, notify)
    elif call.data == "Пользовательское меню": #+
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text=userMenu.getMsg(), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=userMenu.getInlineKeyboard())
    elif call.data == "Сообщения":
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        seeMsgs(call.message)
    elif call.data == "Картинки":
        bot.answer_callback_query(call.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        seePics(call.message)
    elif call.data == "Сообщение админу":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Напиши сообщение или нажми /brake", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.register_next_step_handler(call.message, uploadMsg)
    elif call.data == "Добавить кабана":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text="Отправь фото или нажми /brake", chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.register_next_step_handler(call.message, uploadWct)
    elif call.data == "Статистика":
        stats = utils.Statistics()
        bot.answer_callback_query(call.id)
        back = utils.InlineKeyboard()
        back.add(["Назад"])
        bot.edit_message_text(text=stats.get(), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=back.get(), parse_mode="html")
        del stats
    elif call.data == "Назад":
        bot.answer_callback_query(call.id)
        bot.edit_message_text(text=adminMenu.getMsg(), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=adminMenu.getInlineKeyboard())


def see_jokes(message):
    global msgCounter
    
    stand_keys = [
        "Выйти", "Далее",
        "Принять","Удалить"
    ]

    back_key = ["Выйти"]

    stand_keyboard = utils.InlineKeyboard()
    stand_keyboard.add(stand_keys)
    stand_keyboard.autoRow()
    back_keyboard = utils.InlineKeyboard()
    back_keyboard.add(back_key)

    # get records len with jokeDB method
    record_len = userJokeDB.getRecCount()
    if record_len != 0:
        if msgCounter < record_len: # msgCounter is counter which increase and count every each record 
            bot.send_message(message.chat.id,
                f"{record_len} записей\n" +
                f"{userJokeDB.getJoke(recNum=msgCounter)}",
                reply_markup=stand_keyboard.get())
        else:
            msgCounter = 0
            bot.send_message(
                message.chat.id,
                "Анекдоты кончились",
                reply_markup=back_keyboard.get())
    else:
        bot.send_message(message.chat.id, "Анекдотов нет", reply_markup=back_keyboard.get())


def seePics(message):
    pass


def seeMsgs(message):
    global msgCounter

    stand_keys = [
        "Выйти", "Далее>>",
            "Вычеркнуть"
    ]

    back_key = ["Выйти"]

    stand_keyboard = utils.InlineKeyboard()
    stand_keyboard.add(stand_keys)
    stand_keyboard.autoRow()
    back_keyboard = utils.InlineKeyboard()
    back_keyboard.add(back_key)

    # get records len with msgDB method
    record_len = msgDB.getRecCount()
    if record_len != 0:
        if msgCounter < record_len: # msgCounter is counter which increase and count every each record 
            bot.send_message(message.chat.id,
                f"{record_len} записей\n" +
                f"{msgDB.seeMsg(recNum=msgCounter)}",
                reply_markup=stand_keyboard.get())
        else:
            msgCounter = 0
            bot.send_message(
                message.chat.id,
                "Сообщения кончились",
                reply_markup=back_keyboard.get())
    else:
        bot.send_message(message.chat.id, "Сообщений нет", reply_markup=back_keyboard.get())


def notify(message):
    msg = message.text
    users = userDB.getUsersList()
    if len(users) != 0:
        for i in users:
            bot.send_message(i[0], 
            "<b>Сообщение от админа:</b>\n" + msg, parse_mode="html")
    else:
        bot.send_message(config.adminID, "Пользователей для рассылки нет")


def uploadPicture(message): 
    if message.content_type == 'photo':
        if message.content_type == "media_group": # able to save not only one pic
            bot.send_message(message.chat.id, "Пришли только одну картинку")
            bot.register_next_step_handler(message, uploadPicture)
        else:
            id = message.from_user.id
            picDB = utils.PicDB("accPics")
            # Checking ID of user, if admin is adding, pics`ll be added to main folder "photos/
            # if not, bot send photo id to DB, after all admin`ll be able to save pics to "photos/
            # uploadPic('admin') is saving pics to main -- "photos/"; picDB saving photo id to accepted pics table
            if id == config.adminID: upPic = utils.UploadPic('admin'); txt = "Сохранил"
            else: upPic = utils.UploadPic('user'); txt = "Добавлено на рассмотрение"; picDB.setTableName("pics")
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            file = bot.download_file(file_info.file_path)
            # saving photo id to DB of pics, either accepted pics table or pics table
            picDB.newRecord(file_info.file_path.replace('photos/', ''))
            upPic.upload(file, file_info)
            bot.send_message(message.chat.id, txt)
            bot.send_message(message.chat.id, "Пришли еще картинку, или нажми /brake")
            del picDB
            bot.register_next_step_handler(message, uploadPicture)
    else:
        if message.content_type == "text":
            if message.text.lower() == "/brake":
                bot.send_message(message.chat.id, "Отменено")  
            else:
                bot.send_message(message.chat.id, "Это не картинка!")
                bot.register_next_step_handler(message, uploadPicture)    
        else:      
            bot.send_message(message.chat.id, "Это не картинка!")
            bot.register_next_step_handler(message, uploadPicture)


def uploadJoke(message):
    if message.content_type == "text":
        if message.text.lower() != "/brake":
            joke = message.text
            id = message.from_user.id 
            jokeDB = utils.JokeDB("adminJokes")
            if id == config.adminID: txt = "Сохранил"
            else: jokeDB.setTableName('userJokes'); txt = "Добавлено на рассмотрение"
            jokeDB.newRecord(joke)
            bot.send_message(message.chat.id, txt)
            bot.send_message(message.chat.id, "Напиши анекдот, или нажми /brake")
            bot.register_next_step_handler(message, uploadJoke)
        else:
            bot.send_message(message.chat.id, "Отменено")
    else:
        bot.send_message(message.chat.id, "Только текст, пиши или нажми /brake")
        bot.register_next_step_handler(message, uploadJoke)


def uploadMsg(message): 
    if message.content_type == "text":
        if message.text.lower() != "/brake":
            msg = message.text
            msgDB.newRecord(msg)
            bot.send_message(message.chat.id, "Отправлено")
        else:
            bot.send_message(message.chat.id, "Отменено")
    else:
        bot.send_message(message.chat.id, "Только текст, пиши или нажми /brake")
        bot.register_next_step_handler(message, uploadMsg)


def uploadWct(message):
    if message.content_type == 'photo':
        if message.content_type == "media_group": # able to save not only one pic
            bot.send_message(message.chat.id, "Пришли только одну картинку")
            bot.register_next_step_handler(message, uploadWct)
        else:
            upPic = utils.UploadPic('wct')
            file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
            file = bot.download_file(file_info.file_path)
            boarDB.newRecord(file_info.file_path.replace('photos/', ''))
            upPic.upload(file, file_info)
            bot.send_message(message.chat.id, "Сохранил")
    else:
        if message.content_type == "text":
            if message.text.lower() == "/brake":
                bot.send_message(message.chat.id, "Отменено")  
            else:
                bot.send_message(message.chat.id, "Это не картинка, пришли фото или жми /brake")
                bot.register_next_step_handler(message, uploadWct)    
        else:      
            bot.send_message(message.chat.id, "Это не картинка, пришли фото или жми /brake")
            bot.register_next_step_handler(message, uploadWct)


def getWct(message):
    # WCT is "Which Caban (boar) you Today is"
    # every day user changes his "board id"
    # if user in one day, when he used function in bot, will use wct again, wct give the same "boar id"
    
    id = message.from_user.id 
    users = userDB.getUsersList()
    if id != config.adminID and id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрировался. Нажми /auth, чтобы зарегистрироваться")
        return None
    else:
        now = date.today()
        now_day = now.day
        prev_day = userDB.getPrevDay(id)
        if now_day == prev_day:
            boarID = userDB.getWctForUser(id)
            boar = boarDB.getID(boarID)
            return open(config.wct_path + boar, 'rb')
        else:
            userDB.setPrevDay(now_day, id)
            boarID = random.randint(0, boarDB.getRecCount() - 1)
            userDB.setWctForUser(id, boarID)
            boar = boarDB.getID(boarID)
            return open(config.wct_path + boar, 'rb')


@bot.message_handler(content_types="text") #+
def textWorker(message):
    msg = message.text.lower()
    if msg == "фотокарточка":
        bot.send_photo(message.chat.id, 
        open("../photos/" + adminPicDB.getPicID(recNum=random.randint(0, adminPicDB.getRecCount() - 1)), "rb"))
    elif msg == "анекдот":
        bot.send_message(message.chat.id, 
        adminJokeDB.getJoke(recNum=random.randint(0, adminJokeDB.getRecCount() - 1)))
    elif msg == "какой я кабан сегодня":
        if getWct(message) != None:
            bot.send_photo(message.chat.id, getWct(message))



if __name__ == "__main__":
    print("BOT STARTED")
    utils.log.info("BOT STARTED")
    bot.polling()