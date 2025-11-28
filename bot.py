import random
import time
from telegram import Bot
from flask import Flask

# === CONFIGURAÇÕES ===
TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"
ARQUIVO_LINKS = "links.txt"
INTERVALO_SEGUNDOS = 60  # tempo entre envios

bot = Bot(token=TOKEN)
app = Flask(__name__)

def ler_links():
    with open(ARQUIVO_LINKS, "r") as f:
        links = [linha.strip() for linha in f if linha.strip()]
    return links

def enviar_links():
    links = ler_links()
    if not links:
        print("Nenhum link encontrado!")
        return

    enviados = set()
    while True:
        if len(enviados) == len(links):
            print("Todos os links foram enviados. Reiniciando ciclo...")
            enviados.clear()

        link = random.choice(links)
        while link in enviados:
            link = random.choice(links)

        mensagem = f"🔥 Achado do momento!\nConfira aqui: {link}"
        bot.send_message(chat_id=CHAT_ID, text=mensagem)
        print(f"Enviado -> {mensagem}")
        enviados.add(link)

        time.sleep(INTERVALO_SEGUNDOS)

@app.route("/")
def home():
    return "Bot de Achadinhos Online 🚀"

if __name__ == "__main__":
    from threading import Thread
    # Rodando o envio de links em paralelo
    Thread(target=enviar_links).start()
    app.run(host="0.0.0.0", port=10000)