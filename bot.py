import requests
import time
import os
import json
from request_retrier import retry_request_till_success
from database import insert_row, get_is_changed_from_last_check
from network import get_total_current_gb_count


SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS = os.getenv("SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS") or 300
BOT_TOKEN = os.getenv("BOT_TOKEN")
GET_UPDATES_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"


def check_update_and_save() -> bool:
    timestamp = int(time.time())
    total_current_gb_count = get_total_current_gb_count()
    is_changed_from_last_check = get_is_changed_from_last_check(total_current_gb_count)
    insert_row((timestamp, total_current_gb_count, is_changed_from_last_check))
    return is_changed_from_last_check, total_current_gb_count


def make_keyboard_with_text(text):
    reply_keyboard_markup = {
        "keyboard": [
            [
                {
                    "text": text
                }
            ]
        ],
        "resize_keyboard": True
    }
    return json.dumps(reply_keyboard_markup)

def respond_with_a_message_to_user(text, user_id, keyboard_button_text=""):
    if text is None:
        return
    params = {
        "chat_id": user_id,
        "text": text,
        "reply_markup": make_keyboard_with_text(keyboard_button_text)
    }
    URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = retry_request_till_success(lambda: requests.get(URL, params=params))()
    return response.json()


def pin_message(chat_id, message_id):
    params = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    URL = f"https://api.telegram.org/bot{BOT_TOKEN}/pinChatMessage"
    retry_request_till_success(lambda: requests.get(URL, params=params))()


text = ""
last_update_id = -1
params = {
    'offset': last_update_id,
    'timeout': 0,
    'allowed_updates': ['message']
}

update_count = 0
keep_update_on_telegram_servers = False
while True:
    if keep_update_on_telegram_servers == True:
        params['offset'] = -1
    elif update_count != 0:
        params['offset'] = last_update_id+1
        params['timeout'] = 50

    response = retry_request_till_success(
        lambda: requests.get(GET_UPDATES_URL, params=params, timeout=params['timeout']+10)
    )()
    
    try:
        last_update_id = response.json()['result'][0]['update_id']
        text = response.json()['result'][0]['message']['text']
        user_id = response.json()['result'][0]['message']['from']['id']
    except IndexError:
        text = ""
    except KeyError:
        text = ""

    message_to_send = None
    sleep_for_sec = 0

    if text == "/start":
        respond_with_a_message_to_user(
            (
                "Press on a button to start checking for updates\n"
                "When you press the Stop button, the bot will no longer be fetching the data, "
                "but the confirmation message about it might come after some while"
            ),
            user_id,
            "Start data monitoring"
        )

        last_update_id = response.json()['result'][0]['update_id']

    elif text == "Start data monitoring":
        sleep_for_sec = SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS
        if keep_update_on_telegram_servers == False:
            respond_with_a_message_to_user(
                "Started",
                user_id,
                (
                    "Stop data monitoring (might take up to "
                    f"{SECONDS_DELAY_BETWEEN_VODAFONE_API_REQUESTS} seconds) "
                    "to receive the confirmation message"
                )
            )
        keep_update_on_telegram_servers = True

        is_changed_from_last_check, total_current_gb_count = check_update_and_save()
        if is_changed_from_last_check:
            sent_message = respond_with_a_message_to_user(f'{total_current_gb_count}GB left', user_id)
            sent_message_id = sent_message['result']['message_id']
            pin_message(user_id, sent_message_id)

    elif text.startswith("Stop data monitoring (might take up to"):
        sleep_for_sec = 0
        respond_with_a_message_to_user("Stopped", user_id, "Start data monitoring")
        keep_update_on_telegram_servers = False
        last_update_id = response.json()['result'][0]['update_id']
    
    update_count += 1
    time.sleep(sleep_for_sec)