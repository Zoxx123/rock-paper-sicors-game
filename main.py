import requests
import time
import os
import json
from random import randint
import sqlite3

TOKEN = "TOKEN"
URL = f"https://api.telegram.org/bot{TOKEN}/"
on_bot = True
CONNECT = sqlite3.connect('.\stats.db')
CURSOR = CONNECT.cursor()

data_symb = {
    'rock': '🪨',
    'paper': '📄',
    'sicors': '✂'
}

def initial_db():
     CURSOR.execute('''
                CREATE TABLE IF NOT EXISTS Stats(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chatid INTEGER,
                    games_won INTEGER,
                    games_lost INTEGER
                )
    ''')
     
def get_user(userid):
    CURSOR.execute(f'SELECT * FROM Stats WHERE chatid == {userid}')
    user = CURSOR.fetchone()
    return user
    
def create_user(userid):
    user = get_user(userid)
    if user == None:
        CURSOR.execute(f'INSERT INTO Stats (chatid,games_won,games_lost) VALUES({userid},0,0)')
        CONNECT.commit()

def get_random_symb():
    a = randint(1,3)
    if a == 1:
        return "rock"
    elif a == 2:
        return "paper"
    else:
        return "sicors"

def get_game_result(user_symb, chatid):
    user = get_user(chatid)
    bot_symb = get_random_symb()

    if user_symb == bot_symb: 
        return f"My asnwer is {data_symb[bot_symb]}, we have a tie!"
    if bot_symb == "rock" and user_symb == "sicors":
        CURSOR.execute(f'UPDATE Stats SET games_lost = {user[3] + 1} WHERE chatid == {chatid}')
        CONNECT.commit()
        return f"I had:  {data_symb[bot_symb]}\nYou had: {data_symb[user_symb]}\n I won"
    if bot_symb == "rock" and user_symb == "paper":
        CURSOR.execute(f'UPDATE Stats SET games_won = {user[2] + 1} WHERE chatid == {chatid}')
        CONNECT.commit()
        return f"I had:  {data_symb[bot_symb]}\nYou had: {data_symb[user_symb]}\n You won"
    if bot_symb == "paper" and user_symb == "rock":
        CURSOR.execute(f'UPDATE Stats SET games_lost = {user[3] + 1} WHERE chatid == {chatid}')
        CONNECT.commit()
        return f"I had:  {data_symb[bot_symb]}\nYou had: {data_symb[user_symb]}\n I won"
    if bot_symb == "paper"  and user_symb == "sicors":
        CURSOR.execute(f'UPDATE Stats SET games_won = {user[2] + 1} WHERE chatid == {chatid}')
        CONNECT.commit()
        return f"I had:  {data_symb[bot_symb]}\nYou had: {data_symb[user_symb]}\n You won"
    if bot_symb == "sicors"  and user_symb == "paper":
        CURSOR.execute(f'UPDATE Stats SET games_lost = {user[3] + 1} WHERE chatid == {chatid}')
        CONNECT.commit()
        return f"I had:  {data_symb[bot_symb]}\nYou had: {data_symb[user_symb]}\n I won"
    if bot_symb == "sicors"  and user_symb == "rock":
        CURSOR.execute(f'UPDATE Stats SET games_won = {user[2] + 1} WHERE chatid == {chatid}')
        CONNECT.commit()
        return  f"I had:  {data_symb[bot_symb]}\nYou had: {data_symb[user_symb]}\n You won"
        
    return "i dont know this item"

def get_updates(update_id):
    resp = requests.get(URL+"getUpdates", params={'offset': update_id})
    data = resp.json()
    updates = data['result']
    return updates


def send_message(chat_id,text,keyboard=None):
    params = {
        'chat_id': chat_id, 
        'text':text,
    }
    if not keyboard is None:
        params["reply_markup"] = json.dumps(keyboard)

    resp = requests.get(URL+"sendMessage", params=params)
    print(resp)

def handler_message(text,chat_id,name):
    user = get_user(chat_id)
    if text == "Start Game":
        keyboard = {
            "inline_keyboard": [
                [{"text":"🪨", "callback_data": "rock"},{"text":"📄", "callback_data": "paper"},{"text":"✂", "callback_data": "sicors"}],
            ]
        }
        send_message(chat_id, "Game started, pls enter your item.",keyboard)
    elif text == "My Profile":
        winrate = int((user[2]/(user[2]+user[3]))*100)
        send_message(chat_id,f"Games: {user[2]+user[3]}\nStats: {user[2]}/{user[3]}\nWinrate: {winrate}%")
    else:
        send_message(chat_id, f"{name}, type /start to start the game")
   
  
def handle_commands(command,chat_id,name):
    if command == "/start":
        create_user(chat_id)
        keyboard = {
            "keyboard": [
                ["Start Game"],
                ["My Profile"],
                ["/info", "/help"]
                
            ],
            "resize_keyboard": True,
        }
        send_message(chat_id, "pls start", keyboard)
    elif command == "/info":
         send_message(chat_id,"This bot is to play 🪨 📄 ✂")
    elif command == "/help":
        send_message(chat_id,"Write a thing and it will reply with another thing and calculete who won")

def handler_callback(text,chat_id,name):
    if text == "rock" or text == 'paper' or text == 'sicors':
        result_game = get_game_result(text,chat_id)
        send_message(chat_id,result_game)
    
if __name__ == "__main__":
    update_id = None
    initial_db()
    print("Bot start")
    while on_bot:
        for update in get_updates(update_id):
            update_id = update['update_id'] + 1
            if 'callback_query' in update:
                chat_id =update['callback_query']['message']['chat']['id']
                name = update['callback_query']['message']['chat']['first_name']
                text =  update['callback_query']['data']
                handler_callback(text,chat_id,name)
            else:
                chat_id = update['message']['from']['id']
                name = update['message']['from']['first_name']
                text = update['message']['text']

                if text.startswith('/'):
                    handle_commands(text,chat_id,name,)
                else:
                    handler_message(text,chat_id,name,) 
    time.sleep(1)




