import os
import threading
import time
import random
import logging
from flask import Flask
from telegram import Bot

# ===============================
# LOG
# ===============================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# ===============================
# VARIÁVEIS DO RENDER
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("❌ BOT_TOKEN ou CHAT_ID faltando no Render!")

# Intervalo (1 minuto)
INTERVALO = 60  

# ===============================
# FLASK + TELEGRAM
# ===============================
app = Flask(__name__)
bot = Bot(token=TOKEN)

# ===============================
# CARREGAR LINKS
# ===============================
def carregar_links():
    try:
        with open("links.txt", "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        logging.error("❌ Arquivo links.txt não encontrado!")
        return []

# ===============================
# ENVIO ALEATÓRIO COM TEXTO
# ===============================
def enviar_links():
    links = carregar_links()

    if not links:
        logging.error("❌ links.txt está vazio!")
        return

    logging.info("🚀 Envio ALEATÓRIO a cada 1 minuto iniciado.")

    while True:
        try:
            link = random.choice(links)

            mensagem = f"🔥 Achado do momento!\nConfira aqui: {link}"

            bot.send_message(chat_id=CHAT_ID, text=mensagem)

            logging.info(f"Enviado -> {mensagem}")

            time.sleep(INTERVALO)

        except Exception as e:
            logging.error(f"Erro ao enviar: {e}")
            time.sleep(10)

# ===============================
# THREAD PARA NÃO TRAVAR RENDER
# ===============================
threading.Thread(target=enviar_links, daemon=True).start()

# ===============================
# ROTA PRINCIPAL
# ===============================
@app.route("/")
def home():
    return "Bot Shopee rodando com mensagem personalizada + link aleatório!"

# ===============================
# INICIAR SERVIDOR
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
