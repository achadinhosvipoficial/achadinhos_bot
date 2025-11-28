import os
import sys
import time
import asyncio
import logging
from typing import List, Set
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse, ParseResult

import requests
from bs4 import BeautifulSoup
import schedule

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
AFFILIATE_ID_SHOPEE = os.getenv("AFFILIATE_ID_SHOPEE")

missing = []
if not TELEGRAM_BOT_TOKEN:
    missing.append("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_CHAT_ID:
    missing.append("TELEGRAM_CHAT_ID")
if not AFFILIATE_ID_SHOPEE:
    missing.append("AFFILIATE_ID_SHOPEE")

if missing:
    print(f"[FATAL] Variáveis faltando: {', '.join(missing)}")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shopee-bot")

links_enviados: Set[str] = set()

def raspar_ofertas() -> List[str]:
    urls = []
    example_pages = ["https://shopee.example.com/categoria/x"]
    headers = {"User-Agent": "Mozilla"}

    for page in example_pages:
        try:
            logger.info(f"Conectando em {page}")
            resp = requests.get(page, headers=headers, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            logger.warning(f"Erro ao acessar {page}: {e}")
            continue

        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if "/product/" in href:
                    urls.append(href)
        except Exception as e:
            logger.warning(f"Erro ao parsear HTML: {e}")

    if not urls:
        urls = [
            "https://shopee.example.com/product/12345",
            "https://shopee.example.com/product/23456",
            "https://shopee.example.com/product/34567",
        ]

    return urls

def gerar_link_afiliado(url: str, aff: str) -> str:
    try:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        qs["affiliate_id"] = [aff]
        new_query = urlencode(qs, doseq=True)
        new_url = urlunparse(parsed._replace(query=new_query))
        return new_url
    except:
        return url

def enviar_telegram(texto: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": texto},
            timeout=10,
        )
        return True
    except:
        return False

async def buscar_e_enviar_ofertas():
    logger.info("Rodando ciclo…")
    ofertas = raspar_ofertas()

    for url in ofertas:
        if url in links_enviados:
            continue

        link = gerar_link_afiliado(url, AFFILIATE_ID_SHOPEE)
        ok = enviar_telegram("🔥 Oferta Shopee:\n" + link)
        if ok:
            links_enviados.add(url)
            await asyncio.sleep(1)

def agendar_jobs():
    schedule.every(3).minutes.do(
        lambda: asyncio.get_event_loop().create_task(buscar_e_enviar_ofertas())
    )
    print("[START] Agendamento iniciado.")

async def scheduler_loop():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)

def main():
    agendar_jobs()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scheduler_loop())

if __name__ == "__main__":
    main()