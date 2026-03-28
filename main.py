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
import time
import threading # <--- AGREGADO PARA LA WEB
from http.server import SimpleHTTPRequestHandler # <--- AGREGADO PARA LA WEB
import socketserver # <--- AGREGADO PARA LA WEB
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Configuración de Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN RAILWAY (TUS DATOS ORIGINALES) ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# Pool de Conexiones
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db", pool_size=10, host=DB_HOST, user=DB_USER,
    password=DB_PASS, database=DB_NAME, port=int(DB_PORT), charset="utf8"
)

# APIs CONFIG (TUS LINKS ORIGINALES)
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
TIMEOUT = 120

# ======== SERVIDOR WEB (AGREGADO SIN DAÑAR NADA) ========
def run_web_server():
    # Railway usa la variable PORT, si no existe usa 8080
    PORT = int(os.environ.get("PORT", 8080))
    Handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logger.info(f"🌐 Servidor Web activo en puerto {PORT}")
        httpd.serve_forever()

# --- AQUÍ EMPIEZAN TODAS TUS FUNCIONES ORIGINALES (NO TOCADAS) ---

def clean(value):
    if value is None or value == "" or value == "null": return "No registra"
    return str(value)

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(API_URL_C2, json={"cedula": str(cedula)}, timeout=TIMEOUT)
        return r.json()
    except: return None

def consultar_nequi(telefono):
    try:
        headers = {"X-Api-Key": "Z5k4Y1n4n0vS", "Content-Type": "application/json"}
        r = requests.post("https://extract.nequialpha.com/consultar", json={"telefono": str(telefono)}, headers=headers, timeout=TIMEOUT)
        return r.json()
    except: return None

# ... [MANTÉN AQUÍ EL RESTO DE TUS FUNCIONES: buscar_cedula, tiene_key_valida, etc.] ...

# ======== COMANDO START (ACTUALIZADO CON TU WEB) ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Detecta tu URL de Railway para el link de la trampa
    web_link = f"https://{os.getenv('RAILWAY_STATIC_URL', 'tudominio.up.railway.app')}/"
    
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        f"┃ 🌐 𝐖𝐞𝐛 𝐂𝐡𝐚𝐭: {web_link}\n"
        "┃ ⚔️ /cc ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝐄𝐃𝐔𝐋𝐀\n"
        "┃ ⚔️ /nequi ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐍𝐄𝐐𝐔𝐈\n"
        "┃ ⚔️ /placa ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        "┃ ⚔️ /sisben ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐒𝐈𝐒𝐁𝐄𝐍\n"
        "┃ ⚔️ /info ➛ 𝐌𝐈 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "═════════════════════════\n"
        f"👑 𝘿𝙚𝙨𝙖𝙧𝙧𝙤𝙡𝙡𝙖𝙙𝙤 𝙥𝙤𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

# ======== MAIN (EL MODO CORRECTO DE ARRANCAR) ========
def main():
    # 1. Ejecutar el hilo de la web antes que el bot
    threading.Thread(target=run_web_server, daemon=True).start()

    # 2. Iniciar el Bot con todos tus handlers originales
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cc", comando_cc))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("sisben", comando_sisben))
    application.add_handler(CommandHandler("placa", comando_placa))
    # ... [AGREGA AQUÍ TODOS LOS HANDLERS QUE TENÍAS ORIGINALMENTE] ...

    logger.info("🚀 Bot y Web listos.")
    application.run_polling()

if __name__ == "__main__":
    main()
