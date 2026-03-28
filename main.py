import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mysql.connector import pooling
import logging
import os
import requests
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver
from datetime import datetime

# Logging para ver errores en la consola de Railway
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN ========
TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
OWNER_ID = 8114050673
OWNER_USER = "@Broquicalifoxx"

# Configuración BD (Usando variables de Railway)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql.railway.internal"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "nabo94nabo94"),
    "database": os.getenv("DB_NAME", "ani"),
    "port": int(os.getenv("DB_PORT", 3306))
}

try:
    pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CONFIG)
except Exception as e:
    logger.error(f"Error BD: {e}")

# ======== SERVIDOR WEB (HILO APARTE) ========
def run_web():
    port = int(os.environ.get("PORT", 8080))
    # Esto sirve los archivos index.html y script.js que tienes en la raíz
    handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        logger.info(f"🌐 Web activa en puerto {port}")
        httpd.serve_forever()

# ======== COMANDOS ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # El link será el dominio que te dé Railway
    web_link = f"https://{os.getenv('RAILWAY_STATIC_URL', 'tusitio.up.railway.app')}/"
    
    await update.message.reply_text(
        f"乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        f"══════════════════\n"
        f"⚙️ 𝐁𝐨𝐭 𝐀𝐜𝐭𝐢𝐯𝐨\n"
        f"🌐 𝐖𝐞𝐛 𝐂𝐡𝐚𝐭: {web_link}\n"
        f"⚔️ /cc - Consulta Cédula\n"
        f"⚔️ /nequi - Consulta Nequi\n"
        f"══════════════════\n"
        f"👑 Owner: {OWNER_USER}"
    )

# ======== INICIO DEL BOT ========
if __name__ == "__main__":
    # 1. Arrancar la web en SEGUNDO PLANO (Importante para que no se trabe)
    threading.Thread(target=run_web, daemon=True).start()

    # 2. Arrancar el Bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    # Aquí puedes ir pegando tus otros comandos (cc, nequi, etc) uno por uno
    
    logger.info("🚀 Bot iniciado correctamente")
    app.run_polling()
