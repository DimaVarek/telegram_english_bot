import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters)
from Types import ChatStates, MyChat
from chatgptapi import ChatGPTClient
from texttospeechapi import sample_synthesize_speech
from utils import random_name
from tokens import TELEGRAM_TOKEN


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


CHATS_TABLE = {}
chat_client = ChatGPTClient()


def change_status(chat_id: int, status: ChatStates):
    CHATS_TABLE[chat_id]['status'] = status


async def show_enter_buttons(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    keyboard = [
        [InlineKeyboardButton("Enter a word", callback_data="1")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id,
                                   text=f"If you want to start, click button below",
                                   reply_markup=reply_markup)


async def show_level_buttons(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    keyboard = [
        [InlineKeyboardButton("A1", callback_data="A1"),
         InlineKeyboardButton("A2", callback_data="A2"),
         InlineKeyboardButton("B1", callback_data="B1")],
        [InlineKeyboardButton("B2", callback_data="B1"),
         InlineKeyboardButton("C1", callback_data="C1"),
         InlineKeyboardButton("C2", callback_data="C2")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id,
                                   text=f"Choose your level of english:",
                                   reply_markup=reply_markup)


async def show_generated_buttons(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    generated_list = await chat_client.generate_list(CHATS_TABLE[chat_id]['last_word'],
                                                     CHATS_TABLE[chat_id]['level'])
    CHATS_TABLE[chat_id]['last_list'] = generated_list

    keyboard = [
        [InlineKeyboardButton("regenerate text", callback_data="regenerate")],
        [InlineKeyboardButton("change level", callback_data="change")],
        [InlineKeyboardButton("generate audio", callback_data="audio")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=generated_list)
    await context.bot.send_message(chat_id=chat_id, text=f"Choose next step:", reply_markup=reply_markup)


async def show_audio_settings_buttons(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    keyboard = [
        [InlineKeyboardButton("0.5", callback_data=0.5),
         InlineKeyboardButton("0.75", callback_data=0.75),
         InlineKeyboardButton("1", callback_data=1)],
        [InlineKeyboardButton("1.25", callback_data=1.25),
         InlineKeyboardButton("1.5", callback_data=1.5),
         InlineKeyboardButton("2", callback_data=2)],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat_id, text=f"Choose speed of speech:", reply_markup=reply_markup)


async def show_generated_audio_buttons(context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    name = random_name()
    await sample_synthesize_speech(CHATS_TABLE[chat_id]["last_list"],
                                   name,
                                   CHATS_TABLE[chat_id]['speed'])
    await context.bot.send_audio(chat_id=chat_id,
                                 audio=open(f'mp3/{name}', 'rb'))
    change_status(chat_id, ChatStates.GenerateAudio)
    try:
        os.remove(f'mp3/{name}')
    except OSError:
        pass

    keyboard = [
        [InlineKeyboardButton("change speed", callback_data="change")],
        [InlineKeyboardButton("go to the start", callback_data="start")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(chat_id=chat_id, text=f"Choose next step:", reply_markup=reply_markup)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat: MyChat = {
        'status': ChatStates.NoWord,
        'last_word': "",
        'last_list': "",
        'level': "",
        'speed': ""
    }
    CHATS_TABLE[update.effective_chat.id] = chat
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi, I'm a bot who will help " +
                                                                          "you to learn english. ")
    await show_enter_buttons(context, update.effective_chat.id)


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in CHATS_TABLE:
        await context.bot.send_message(chat_id=chat_id, text="use command /start")
        return
    if CHATS_TABLE[chat_id]["status"] == ChatStates.SetWord:

        change_status(chat_id, ChatStates.SetLevel)
        CHATS_TABLE[chat_id]['last_word'] = update.message.text
        await show_level_buttons(context, chat_id)
    else:
        await context.bot.send_message(chat_id=chat_id, text="use buttons")


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    if chat_id not in CHATS_TABLE:
        await context.bot.send_message(chat_id=chat_id, text="use command /start")
        return

    query = update.callback_query
    await query.answer()

    match CHATS_TABLE[chat_id]["status"]:
        case ChatStates.NoWord:
            change_status(chat_id, ChatStates.SetWord)
            await query.edit_message_text(text=f"Write down a word:")
        case ChatStates.SetLevel:
            CHATS_TABLE[chat_id]['level'] = query.data
            change_status(chat_id, ChatStates.GenerateList)
            await query.edit_message_text(
                text=f"Word: {CHATS_TABLE[chat_id]['last_word']}, level: {CHATS_TABLE[chat_id]['level']}")
            await show_generated_buttons(context, chat_id)
        case ChatStates.GenerateList:
            match query.data:
                case 'regenerate':
                    await query.edit_message_text(text=f"You chose to regenerate text")
                    await show_generated_buttons(context, chat_id)
                case 'change':
                    change_status(chat_id, ChatStates.SetLevel)
                    await query.edit_message_text(text=f"You chose to change level")
                    await show_level_buttons(context, chat_id)
                case 'audio':
                    await query.edit_message_text(text=f"You chose to go ahead")
                    change_status(chat_id, ChatStates.SetAudioSettings)
                    await show_audio_settings_buttons(context, chat_id)
        case ChatStates.SetAudioSettings:
            CHATS_TABLE[chat_id]['speed'] = float(query.data)
            await query.edit_message_text(text=f"Chosen speed is {CHATS_TABLE[chat_id]['speed']}")
            await show_generated_audio_buttons(context, chat_id)
        case ChatStates.GenerateAudio:
            match query.data:
                case 'change':
                    await query.edit_message_text(text=f"You chose to change speed")
                    change_status(chat_id, ChatStates.SetAudioSettings)
                    await show_audio_settings_buttons(context, chat_id)
                case 'start':
                    await query.edit_message_text(text=f"Enjoy it!")
                    change_status(chat_id, ChatStates.NoWord)
                    await show_enter_buttons(context, chat_id)
        case _:
            await context.bot.send_message(chat_id=chat_id, text="we have a problem")


if __name__ == '__main__':
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    start_handler = CommandHandler('start', start)
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
    application.add_handler(start_handler)
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(echo_handler)

    application.run_polling()
