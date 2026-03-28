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
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN RAILWAY (TUS DATOS) ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# Pool de Conexiones
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db", pool_size=10, host=DB_HOST, user=DB_USER,
    password=DB_PASS, database=DB_NAME, port=int(DB_PORT), charset="utf8"
)

# APIs CONFIG
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
TIMEOUT = 120

# ======== MOTOR WEB (HILO APARTE) ========
def run_web_server():
    PORT = int(os.environ.get("PORT", 8080))
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format, *args): return # No llenar consola
    
    with socketserver.TCPServer(("", PORT), QuietHandler) as httpd:
        logger.info(f"🌐 Servidor Web en puerto {PORT}")
        httpd.serve_forever()

# ======== FUNCIONES DE CONSULTA (TUS ORIGINALES) ========

def clean(value):
    return str(value) if value and value != "null" else "No registra"

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally: 
        if conn: conn.close()

# --- CONSULTAS API ---
def consultar_nequi(telefono):
    try:
        headers = {"X-Api-Key": "Z5k4Y1n4n0vS", "Content-Type": "application/json"}
        r = requests.post("https://extract.nequialpha.com/consultar", json={"telefono": str(telefono)}, headers=headers, timeout=15)
        return r.json()
    except: return None

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(API_URL_C2, json={"cedula": str(cedula)}, headers={"Content-Type": "application/json"}, timeout=15)
        return r.json()
    except: return None

# ======== COMANDOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Generar link dinámico
    web_link = f"https://{os.getenv('RAILWAY_STATIC_URL', 'tudominio.up.railway.app')}/"
    
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        f"┃ 🌐 𝐖𝐞𝐛 𝐂𝐡𝐚𝐭: {web_link}\n"
        "┃ ⚔️ /cc ➛ CÉDULA V1\n"
        "┃ ⚔️ /c2 ➛ CÉDULA V2\n"
        "┃ ⚔️ /nequi ➛ NEQUI\n"
        "┃ ⚔️ /sisben ➛ SISBEN\n"
        "┃ ⚔️ /placa ➛ PLACA\n"
        "┃ ⚔️ /info ➛ SUSCRIPCIÓN\n"
        "═════════════════════════\n"
        f"👑 Desarrollado por: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /nequi <telefono>")
        return
    res = consultar_nequi(context.args[0])
    if res:
        await update.message.reply_text(f"📱 Tel: {res.get('telefono')}\n🆔 CC: {res.get('cedula')}\n👤 Nom: {res.get('nombre_completo')}")
    else:
        await update.message.reply_text("❌ No encontrado.")

# (Aquí sigues pegando tus comandos comando_cc, comando_sisben, etc, igualitos como los tenías)

# ======== INICIO ========
def main():
    # 1. Web en hilo aparte (Indispensable para que responda Telegram)
    threading.Thread(target=run_web_server, daemon=True).start()

    # 2. Iniciar Bot
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    # Registra aquí el resto de tus handlers (cc, placa, sisben, redeem, info...)

    logger.info("🚀 SISTEMA ONLINE (Bot + Web)")
    application.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
