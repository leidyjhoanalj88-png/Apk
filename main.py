import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mysql.connector import pooling
import logging
import random
import string
import os
import requests
import json
import tempfile
import subprocess
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

# ======== CONFIG MYSQL DESDE RAILWAY (FIX) ========
mysql_url = os.getenv("MYSQL_URL")

if not mysql_url:
    raise ValueError("MYSQL_URL no está configurada en Railway")

url = urlparse(mysql_url)

DB_HOST = url.hostname
DB_USER = url.username
DB_PASS = url.password
DB_NAME = url.path[1:]
DB_PORT = url.port

TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# ======== POOL ========
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=10,
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    port=int(DB_PORT),
    charset="utf8"
)

# ======== APIs ========
API_URL_C2 = os.getenv("API_URL", "https://extract.nequialpha.com/doxing")
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
TIMEOUT = 120

# ======== FIX NEQUI 🔥 ========
def consultar_nequi_scraping(telefono):
    urls = [
        "https://api.puntosred.co/api/v1/recargas/operadores/nequi/consultar",
        "https://recargas.puntored.co/api/v1/recargas/operadores/nequi/consultar"
    ]

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    payload = {"celular": str(telefono)}

    for url in urls:
        try:
            r = requests.post(url, json=payload, headers=headers, timeout=10)

            if r.status_code == 200:
                data = r.json()
                nombre = data.get("nombre") or data.get("cliente") or data.get("full_name")
                if nombre:
                    return {"success": True, "nombre": nombre}

        except Exception as e:
            logger.warning(f"Fallo en {url}: {e}")

    return {"success": False, "error": "Servicio no disponible."}

# ======== RESTO IGUAL (NO TOCADO) ========

def tiene_key_valida(user_id):
    if user_id == OWNER_ID:
        return True
    try:
        conn = pool.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM user_keys WHERE user_id=%s AND redeemed=TRUE AND expiration_date>NOW()", (user_id,))
        return cur.fetchone() is not None
    except:
        return False
    finally:
        try: conn.close()
        except: pass

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return

    if not context.args:
        await update.message.reply_text("📌 Uso: /nequi <telefono>")
        return

    telefono = context.args[0]
    msg = await update.message.reply_text(f"🔍 Consultando `{telefono}`...", parse_mode="Markdown")

    res = consultar_nequi_scraping(telefono)

    if res["success"]:
        await msg.edit_text(
            f"📱 `{telefono}`\n👤 `{res['nombre']}`",
            parse_mode="Markdown"
        )
    else:
        await msg.edit_text(f"❌ {res['error']}")

# ======== MAIN ========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.run_polling()

if __name__ == "__main__":
    main()