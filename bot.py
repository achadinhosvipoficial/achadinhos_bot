import os
import threading
import time
import logging
import asyncio
from flask import Flask
from telegram import Bot
from telegram.error import TelegramError

# ===========================
# LOG
# ===========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

# ===========================
# VARIÁVEIS DO RENDER
# ===========================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
INTERVALO = 180
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    logging.error("❌ BOT_TOKEN não foi definido!")
if not CHAT_ID:
    logging.error("❌ CHAT_ID não foi definido!")

bot = Bot(token=TOKEN)
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# ===========================
# FLASK
# ===========================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Shopee rodando 24h no Render! 🚀"

@app.route("/test")
def test():
    try:
        loop.run_until_complete(
            bot.send_message(chat_id=CHAT_ID, text="Bot funcionando! 🚀")
        )
        return "Mensagem enviada!"
    except Exception as e:
        return f"Erro: {e}"

# ===========================
# LINKS
# ===========================
def carregar_links():
    if not os.path.exists("links.txt"):
        logging.error("❌ links.txt não existe!")
        return []

    with open("links.txt", "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]

LINKS = carregar_links()

# ===========================
# THREAD DE ENVIO
# ===========================
def enviar_links():
    if not LINKS:
        logging.error("❌ Nenhum link encontrado.")
        return

    idx = 0

    while True:
        try:
            link = LINKS[idx]
            logging.info(f"➡️ Enviando: {link}")

            loop.run_until_complete(
                bot.send_message(chat_id=CHAT_ID, text=link)
            )

            idx = (idx + 1) % len(LINKS)
            time.sleep(INTERVALO)

        except TelegramError as e:
            logging.error(f"⚠️ Erro Telegram: {e}")
            time.sleep(10)

        except Exception as e:
            logging.error(f"❌ Erro inesperado: {e}")
            time.sleep(10)

# ===========================
# INICIAR THREAD
# ===========================
threading.Thread(target=enviar_links, daemon=True).start()
print("Thread iniciada! Bot está ativo.")

# ===========================
# INICIAR SERVIDOR
# ===========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
