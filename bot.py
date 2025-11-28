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
# VARIÁVEIS
# ===============================
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    raise Exception("❌ BOT_TOKEN ou CHAT_ID faltando!")

INTERVALO = 60  # segundos entre envios aleatórios
ARQUIVO_LINKS = "links.txt"

# ===============================
# FLASK + TELEGRAM
# ===============================
app = Flask(__name__)
bot = Bot(token=TOKEN)

# ===============================
# FUNÇÃO PARA CARREGAR LINKS
# ===============================
def carregar_links():
    try:
        with open(ARQUIVO_LINKS, "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        logging.error(f"❌ Arquivo {ARQUIVO_LINKS} não encontrado!")
        return []

# ===============================
# ENVIO ALEATÓRIO SEM REPETIÇÃO
# ===============================
enviados = set()

def enviar_links_aleatorios():
    global enviados
    logging.info("🚀 Envio ALEATÓRIO iniciado.")

    while True:
        links = carregar_links()
        if not links:
            logging.warning("❌ links.txt vazio, esperando 10s...")
            time.sleep(10)
            continue

        # Atualiza lista de enviados removendo links que foram apagados
        enviados = {link for link in enviados if link in links}

        # Filtra links ainda não enviados
        nao_enviados = [link for link in links if link not in enviados]

        if not nao_enviados:
            # Resetar quando todos foram enviados
            enviados.clear()
            nao_enviados = links.copy()

        link = random.choice(nao_enviados)
        try:
            mensagem = f"🔥 Achado do momento!\nConfira aqui: {link}"
            bot.send_message(chat_id=CHAT_ID, text=mensagem)
            logging.info(f"Enviado -> {mensagem}")
            enviados.add(link)
        except Exception as e:
            logging.error(f"Erro ao enviar link: {e}")

        time.sleep(INTERVALO)

# ===============================
# INICIAR THREAD
# ===============================
threading.Thread(target=enviar_links_aleatorios, daemon=True).start()

# ===============================
# ROTA PRINCIPAL FLASK
# ===============================
@app.route("/")
def home():
    return "Bot de Achadinhos rodando! Links aleatórios sendo enviados."

# ===============================
# INICIAR SERVIDOR
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
