import json 
import requests
import time
import urllib
from dbhelper import DBHelper

TOKEN = "430034156:AAFw4qnhX68xKUwkOUbpm0eu-IYt1JKvwjU"
URL = "https://api.telegram.org/bot{}/".format(TOKEN)
TIMEOUT = 100
db = DBHelper()

def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


def get_updates(offset=None):
    url = URL + "getUpdates?timeout={}".format(TIMEOUT)
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    if(len(updates["result"]) > 0):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        if('message' in updates["result"][last_update]):
            text = updates["result"][last_update]["message"]["text"]
            chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        elif('edited_message' in updates["result"][last_update]):
            text = updates["result"][last_update]["edited_message"]["text"]
            chat_id = updates["result"][last_update]["edited_message"]["chat"]["id"]
        return (text, chat_id)
    else:
        return (None, None)

def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)

def handle_updates(updates):
    for update in updates["result"]:
        try:
            if('message' in update):
                text = update["message"]["text"]
                chat = update["message"]["chat"]["id"]
            elif('edited_message' in update):
                text = update["edited_message"]["text"]
                chat = update["edited_message"]["chat"]["id"]
            items = db.get_items()
            if text in items:
                db.delete_item(text)
                items = db.get_items()
            else:
                db.add_item(text)
                items = db.get_items()
                message = "\n".join(items)
                send_message(message, chat)
        except KeyError:
            pass

def send_message(text, chat_id):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}".format(text, chat_id)
    get_url(url)
    

text, chat_id = get_last_chat_id_and_text(get_updates())
send_message(text, chat_id)

def main():
    last_update_id = None
    while True:
        updates = get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            echo_all_updates(updates)
            time.sleep(0.3)


if __name__ == '__main__':
    main()
