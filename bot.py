import os
import threading
import time
import random
import logging
from flask import Flask
from telegram import Bot, TelegramError

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
            links = [linha.strip() for linha in f if linha.strip()]
            logging.info(f"Links carregados: {len(links)}")
            return links
    except FileNotFoundError:
        logging.error(f"❌ Arquivo {ARQUIVO_LINKS} não encontrado!")
        return []

# ===============================
# TESTE DE ENVIO
# ===============================
def teste_envio():
    try:
        bot.send_message(chat_id=CHAT_ID, text="✅ Bot iniciado com sucesso!")
        logging.info("Teste de envio realizado com sucesso.")
    except TelegramError as e:
        logging.error(f"Erro no envio de teste: {e}")

# ===============================
# ENVIO ALEATÓRIO DE LINKS
# ===============================
def enviar_links_aleatorios():
    logging.info("🚀 Envio ALEATÓRIO iniciado.")
    while True:
        try:
            links = carregar_links()
            if not links:
                logging.warning("❌ links.txt vazio, esperando 10s...")
                time.sleep(10)
                continue

            link = random.choice(links)
            mensagem = f"🔥 Achado do momento!\nConfira aqui: {link}"
            bot.send_message(chat_id=CHAT_ID, text=mensagem)
            logging.info(f"Enviado -> {mensagem}")

            time.sleep(INTERVALO)

        except TelegramError as e:
            logging.error(f"Erro no envio aleatório: {e}")
            time.sleep(10)
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            time.sleep(10)

# ===============================
# ENVIO IMEDIATO DE LINKS NOVOS
# ===============================
def monitorar_links_novos():
    ultimo_tamanho = 0
    logging.info("🚀 Monitoramento de links novos iniciado.")
    while True:
        try:
            if os.path.exists(ARQUIVO_LINKS):
                tamanho_atual = os.path.getsize(ARQUIVO_LINKS)
                if tamanho_atual != ultimo_tamanho:
                    links = carregar_links()
                    if links:
                        novo_link = links[-1]
                        mensagem = f"🔥 Novo achado!\nConfira aqui: {novo_link}"
                        bot.send_message(chat_id=CHAT_ID, text=mensagem)
                        logging.info(f"Enviado -> {mensagem}")
                    ultimo_tamanho = tamanho_atual
            time.sleep(5)
        except TelegramError as e:
            logging.error(f"Erro no envio de link novo: {e}")
            time.sleep(10)
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            time.sleep(10)

# ===============================
# INICIAR THREADS
# ===============================
threading.Thread(target=enviar_links_aleatorios, daemon=True).start()
threading.Thread(target=monitorar_links_novos, daemon=True).start()

# ===============================
# TESTE DE ENVIO INICIAL
# ===============================
teste_envio()

# ===============================
# ROTA PRINCIPAL FLASK
# ===============================
@app.route("/")
def home():
    return "Bot de Achadinhos rodando! Links aleatórios e novos sendo enviados."

# ===============================
# INICIAR SERVIDOR
# ===============================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
