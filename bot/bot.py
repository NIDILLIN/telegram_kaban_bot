# v1.8.8.5
from handlers import *
from header import *
from telebot import types


bot.register_message_handler(commands=["start"], 
                             func=start, 
                             callback="none")

bot.register_message_handler(commands=["auth"], 
                             func=auth, 
                             callback="none")

bot.register_message_handler(commands=["help"], 
                             func=help, 
                             callback="none")

bot.register_message_handler(content_types="text", 
                             func=reply_keyboard_worker, 
                             callback="none")

bot.register_message_handler(content_types="photo", 
                             func=upload_photo_in_private_chat, 
                             callback="none")


@bot.callback_query_handler(func=lambda call: True)
def call(call):
    call_work(call)


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_worker(query):
    query_text(query)


@bot.inline_handler(func=lambda query: len(query.query) == 0)
def empty(query):
    empty_query(query)


if __name__ == "__main__":
    try:
        print("BOT STARTED")
        utils.log.info("BOT STARTED")
        bot.polling()
    except Exception as e:
        utils.log.error(e)
        print(e)
        bot.send_message(ADMIN_ID, "Bot stoped. Trouble occurred")
