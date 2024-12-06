import os

from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from telegram import ReplyKeyboardMarkup, KeyboardButton

import time
from database import insert_row, get_is_changed_from_last_check
from network import get_total_current_gb_count

import asyncio


SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS = os.getenv("SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS") or 300
BOT_TOKEN = os.getenv("BOT_TOKEN")

WELCOME_MESSAGE = (
    "Press on a button to start checking for updates\n"
    "When you press the Stop button, the bot will no longer be fetching the data, "
    "but the confirmation message about it might come after some while"
)
START_KEYBOARD_TEXT = "Start data monitoring"
STARTED_MESSAGE = "Started"
END_KEYBOARD_TEXT = "Stop data monitoring"
STOPPED_MESSAGE = "Stopped"


start_keyboard = ReplyKeyboardMarkup([[KeyboardButton(START_KEYBOARD_TEXT)]], resize_keyboard=True)
end_keyboard = ReplyKeyboardMarkup([[KeyboardButton(END_KEYBOARD_TEXT)]], resize_keyboard=True)


def check_update_and_save() -> bool:
    timestamp = int(time.time())
    total_current_gb_count = get_total_current_gb_count()
    is_changed_from_last_check = get_is_changed_from_last_check(total_current_gb_count)
    insert_row((timestamp, total_current_gb_count, is_changed_from_last_check))
    return is_changed_from_last_check, total_current_gb_count


future_reference = {"ref": None}

async def monitor_vodafone_API(update: Update, context: ContextTypes.DEFAULT_TYPE):
    while True:
        is_changed_from_last_check, total_current_gb_count = check_update_and_save()
        if is_changed_from_last_check:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'{total_current_gb_count}GB left', reply_markup=end_keyboard)
        await asyncio.sleep(SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS)

async def handle_start_data_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text != START_KEYBOARD_TEXT:
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=STARTED_MESSAGE, reply_markup=end_keyboard)
    ref = asyncio.ensure_future(monitor_vodafone_API(update, context))
    future_reference["ref"] = ref


async def handle_stop_data_monitoring(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text != END_KEYBOARD_TEXT:
        return
    await context.bot.send_message(chat_id=update.effective_chat.id, text=STOPPED_MESSAGE, reply_markup=start_keyboard)
    future_reference["ref"].cancel() if future_reference["ref"] else ...


async def start_bot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=WELCOME_MESSAGE, reply_markup=start_keyboard)

async def process_text_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await handle_start_data_monitoring(update, context)
    await handle_stop_data_monitoring(update, context)



if __name__ == "__main__":
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    start_handler = CommandHandler('start', start_bot_command)
    application.add_handler(start_handler)

    text_messages_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), process_text_messages)
    application.add_handler(text_messages_handler)

    application.run_polling()