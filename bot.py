import os
import threading
import time
from flask import Flask
from telegram import Bot

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")  # ID do grupo
INTERVALO = 180  # 3 minutos

app = Flask(__name__)
bot = Bot(token=TOKEN)

def carregar_links():
    with open("links.txt", "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]

def enviar_links():
    links = carregar_links()
    idx = 0

    while True:
        try:
            link = links[idx]
            bot.send_message(chat_id=CHAT_ID, text=link)

            idx = (idx + 1) % len(links)
            time.sleep(INTERVALO)

        except Exception as e:
            print("Erro ao enviar link:", e)
            time.sleep(10)

# Thread em paralelo para enviar os links sem travar o Render
threading.Thread(target=enviar_links, daemon=True).start()

@app.route("/")
def home():
    return "Bot Shopee rodando 24h no Render!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
