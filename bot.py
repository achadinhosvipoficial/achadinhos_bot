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

INTERVALO = 60  # Intervalo entre envios em segundos

# ===============================
# FLASK + TELEGRAM
# ===============================
app = Flask(__name__)
bot = Bot(token=TOKEN)

# ===============================
# ARQUIVOS
# ===============================
LINKS_FILE = "links.txt"
ENVIADOS_FILE = "enviados.txt"

# ===============================
# FUNÇÕES DE CARREGAMENTO
# ===============================
def carregar_links():
    try:
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            return [linha.strip() for linha in f if linha.strip()]
    except FileNotFoundError:
        logging.error("❌ Arquivo links.txt não encontrado!")
        return []

def carregar_enviados():
    if not os.path.exists(ENVIADOS_FILE):
        return set()
    with open(ENVIADOS_FILE, "r", encoding="utf-8") as f:
        return set(linha.strip() for linha in f)

def salvar_enviado(link):
    with open(ENVIADOS_FILE, "a", encoding="utf-8") as f:
        f.write(link + "\n")

# ===============================
# FUNÇÃO DE ENVIO ALEATÓRIO
# ===============================
def enviar_links():
    logging.info("🚀 Bot iniciado, enviando links aleatórios a cada 1 minuto...")
    while True:
        try:
            links = carregar_links()
            enviados = carregar_enviados()
            disponiveis = [l for l in links if l not in enviados]

            if not disponiveis:
                logging.info("⚠️ Nenhum link novo disponível no momento. Aguardando...")
                time.sleep(INTERVALO)
                continue

            link = random.choice(disponiveis)
            mensagem = f"🔥 Achado do momento!\nConfira aqui: {link}"
            bot.send_message(chat_id=CHAT_ID, text=mensagem)
            salvar_enviado(link)
            logging.info(f"Enviado -> {mensagem}")
            time.sleep(INTERVALO)

        except Exception as e:
            logging.error(f"❌ Erro ao enviar link: {e}")
            time.sleep(10)

# ===============================
# ROTA FLASK
# ===============================
@app.route("/")
def home():
    return "Bot de Achadinhos rodando! 🚀"

# ===============================
# THREAD PARA ENVIO
# ===============================
threading.Thread(target=enviar_links, daemon=True).start()

# ===============================
# INICIAR SERVIDOR
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
