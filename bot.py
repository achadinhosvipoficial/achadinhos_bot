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

# Intervalo em segundos (1 minuto)
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
# CARREGAR LINKS ENVIADOS
# ===============================
def carregar_enviados():
    if not os.path.exists("enviados.txt"):
        open("enviados.txt", "w").close()
    with open("enviados.txt", "r", encoding="utf-8") as f:
        return set(linha.strip() for linha in f if linha.strip())

# ===============================
# SALVAR LINK ENVIADO
# ===============================
def salvar_enviado(link):
    with open("enviados.txt", "a", encoding="utf-8") as f:
        f.write(link + "\n")

# ===============================
# ENVIO ALEATÓRIO COM TEXTO
# ===============================
def enviar_links():
    logging.info("🚀 Envio ALEATÓRIO iniciado.")
    
    while True:
        links = carregar_links()
        enviados = carregar_enviados()
        
        # Filtra os links que ainda não foram enviados
        nao_enviados = [l for l in links if l not in enviados]

        if not nao_enviados:
            logging.info("🔄 Todos os links foram enviados, reiniciando ciclo...")
            # Limpa enviados.txt para recomeçar o ciclo
            open("enviados.txt", "w").close()
            time.sleep(5)
            continue

        # Escolhe um link aleatório não enviado
        link = random.choice(nao_enviados)
        mensagem = f"🔥 Achado do momento!\nConfira aqui: {link}"
        
        try:
            bot.send_message(chat_id=CHAT_ID, text=mensagem)
            logging.info(f"Enviado -> {mensagem}")
            salvar_enviado(link)
        except Exception as e:
            logging.error(f"Erro ao enviar: {e}")
        
        time.sleep(INTERVALO)

# ===============================
# THREAD PARA NÃO TRAVAR RENDER
# ===============================
threading.Thread(target=enviar_links, daemon=True).start()

# ===============================
# ROTA PRINCIPAL
# ===============================
@app.route("/")
def home():
    return "Bot Achadinhos rodando com mensagem personalizada + link aleatório!"

# ===============================
# INICIAR SERVIDOR
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
