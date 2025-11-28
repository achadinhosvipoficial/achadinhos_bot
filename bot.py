import os
import asyncio
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

# Intervalo entre envios (em segundos)
INTERVALO = 60  

# ===============================
# FLASK + TELEGRAM
# ===============================
app = Flask(__name__)
bot = Bot(token=TOKEN)

# ===============================
# FUNÇÃO PARA CARREGAR LINKS
# ===============================
def carregar_links():
    """Lê links do arquivo links.txt sempre que chamado."""
    try:
        with open("links.txt", "r", encoding="utf-8") as f:
            links = [linha.strip() for linha in f if linha.strip()]
            if not links:
                logging.warning("⚠️ links.txt está vazio!")
            return links
    except FileNotFoundError:
        logging.error("❌ Arquivo links.txt não encontrado!")
        return []

# ===============================
# GERENCIAMENTO DE LINKS COM LOG
# ===============================
class LinkManager:
    def __init__(self):
        self.links_disponiveis = []
        self.links_enviados = set()

    def obter_link(self):
        todos_links = carregar_links()
        if not todos_links:
            return None

        # Atualiza a lista de disponíveis removendo já enviados
        self.links_disponiveis = [l for l in todos_links if l not in self.links_enviados]

        # Se todos os links foram enviados, reinicia o ciclo
        if not self.links_disponiveis:
            logging.info("♻️ Todos os links foram enviados. Reiniciando ciclo...")
            self.links_enviados.clear()
            self.links_disponiveis = todos_links.copy()

        link = random.choice(self.links_disponiveis)
        self.links_enviados.add(link)

        logging.info(f"📌 Links enviados neste ciclo: {len(self.links_enviados)}/{len(todos_links)}")
        return link

link_manager = LinkManager()

# ===============================
# ENVIO ASSÍNCRONO DE LINKS
# ===============================
async def enviar_links():
    logging.info("🚀 Envio ALEATÓRIO a cada 1 minuto iniciado.")

    while True:
        try:
            link = link_manager.obter_link()
            if not link:
                await asyncio.sleep(INTERVALO)
                continue

            mensagem = f"🔥 Achado do momento!\nConfira aqui: {link}"

            await bot.send_message(chat_id=CHAT_ID, text=mensagem)
            logging.info(f"Enviado -> {mensagem}")

            await asyncio.sleep(INTERVALO)

        except Exception as e:
            logging.error(f"Erro ao enviar: {e}")
            await asyncio.sleep(10)

# ===============================
# ROTA PRINCIPAL
# ===============================
@app.route("/")
def home():
    return "Bot Shopee rodando com mensagem personalizada + link aleatório!"

# ===============================
# INICIAR FLASK + ENVIO ASSÍNCRONO
# ===============================
if __name__ == "__main__":
    from threading import Thread

    def run_flask():
        app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))

    Thread(target=run_flask, daemon=True).start()
    asyncio.run(enviar_links())
