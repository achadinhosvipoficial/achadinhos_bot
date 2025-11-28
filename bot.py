import random
import time
import os
from telegram import Bot

# CONFIGURAÇÕES
TOKEN = "SEU_TOKEN_AQUI"
CHAT_ID = "SEU_CHAT_ID_AQUI"
INTERVALO = 60  # tempo em segundos entre envios
ARQUIVO_ENVIADOS = "links_enviados.txt"

# LISTA DE LINKS
links = [
    "https://s.shopee.com.br/Exemplo1",
    "https://s.shopee.com.br/Exemplo2",
    "https://s.shopee.com.br/Exemplo3",
    # adicione mais links aqui
]

# Inicializa bot
bot = Bot(token=TOKEN)

# Função para ler links enviados
def ler_enviados():
    if not os.path.exists(ARQUIVO_ENVIADOS):
        return set()
    with open(ARQUIVO_ENVIADOS, "r") as f:
        return set(line.strip() for line in f if line.strip())

# Função para salvar link enviado
def salvar_enviado(link):
    with open(ARQUIVO_ENVIADOS, "a") as f:
        f.write(link + "\n")

# Função principal de envio
def enviar_links():
    while True:
        enviados = ler_enviados()
        # se todos os links foram enviados, reseta
        if len(enviados) >= len(links):
            print("✅ Todos os links enviados. Reiniciando...")
            os.remove(ARQUIVO_ENVIADOS)
            enviados = set()
        
        # escolhe um link que ainda não foi enviado
        disponiveis = [link for link in links if link not in enviados]
        if not disponiveis:
            continue  # deve reiniciar no próximo loop
        
        link = random.choice(disponiveis)
        mensagem = f"🔥 Achado do momento!\nConfira aqui: {link}"
        try:
            bot.send_message(chat_id=CHAT_ID, text=mensagem)
            print(f"Enviado -> {mensagem}")
            salvar_enviado(link)
        except Exception as e:
            print(f"❌ Erro ao enviar link: {e}")
        
        time.sleep(INTERVALO)

if __name__ == "__main__":
    print("🚀 Bot iniciado")
    enviar_links()