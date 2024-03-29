import random
from header import utils, bot, helpMenu, userDB, adminMenu, userMenu, adminPicDB, adminJokeDB
from config import ADMIN_ID, KEYS, BOT_MESSAGE
from server.admin.admin_utils.suggestions import Suggestions
import server.admin.admin_funcs as admin_funcs
from server.utils.ban import BannedDB
from server.user.user_funcs import get_wct_photo

def start(message):
    keyboard = utils.ReplyKeyboard()
    keyboard.set(KEYS.START)
    bot.send_message(message.chat.id, "Хрю хрю, кабан {0.first_name}!"
        .format(message.from_user, bot.get_me()), reply_markup=keyboard)


def ban(message):
    if message.from_user.id == ADMIN_ID:
        err = admin_funcs.ban_user(message)
        if err != None:
            bot.reply_to(message, err)
        else:
            bot.reply_to(message, "Забанил пользователя")


def unban(message):
    if message.from_user.id == ADMIN_ID:
        admin_funcs.unban_user(message)
        bot.reply_to(message, "Разбанил пользователя")


def banList(message):
    if message.from_user.id == ADMIN_ID:
        banDB = BannedDB()
        banList = banDB.get_users_idName_list()
        if not banList:
            bot.reply_to(message, "Забаненных пользователей нет")
        else:
            bot.send_message(message.chat.id, banList)


def auth(message):
    userID = message.from_user.id
    if userID == ADMIN_ID:
        admin(message)
    else:
        usersList = userDB.get_users_list()
        if userID not in usersList:
            userDB.add_user(userID)
        user(message)


def help(message):
    helpMenu.set_message(BOT_MESSAGE.HELP(photo_count = adminPicDB.get_records_count(), joke_count = adminJokeDB.get_records_count()))
    bot.send_message(message.chat.id, helpMenu.message, parse_mode="html")


def admin(message):
    adminMenu.set_message("Админ меню")
    suggestions = Suggestions()
    if suggestions.exist():
        adminMenu.set_message(suggestions.get_message())
    bot.send_message(message.chat.id, adminMenu.message, reply_markup=adminMenu.get_inline_keyboard(), parse_mode="html")


def user(message):
    bot.send_message(message.chat.id, userMenu.message, reply_markup=userMenu.get_inline_keyboard())


def send_wct(message):
    check_suggestions()
    user_id = message.from_user.id
    users = userDB.get_users_list()

    if user_id != ADMIN_ID and user_id not in users:
        bot.send_message(message.chat.id, "Ты не зарегистрировался. Нажми /auth, чтобы зарегистрироваться", reply_to_message_id=message.message_id)
        return None
    else:
        boar, caption = get_wct_photo(message)
        bot.send_photo(message.chat.id, boar, reply_to_message_id=message.message_id, caption=caption)


def send_joke(message):
    check_suggestions()
    bot.send_message(message.chat.id, 
        adminJokeDB.get_record(row=random.randint(0, adminJokeDB.get_records_count() - 1)))


def send_photo(message): # by file_id
    check_suggestions()
    bot.send_photo(message.chat.id, 
        adminPicDB.get_record(row=random.randint(0, adminPicDB.get_records_count() - 1), col=1))


def check_suggestions():
    suggestions = Suggestions()
    if suggestions.limit_reached():
        bot.send_message(ADMIN_ID, f"Есть новые {suggestions.all_suggestions} предложений")