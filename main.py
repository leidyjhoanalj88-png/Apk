import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mysql.connector import pooling
import logging
import os
import threading
from http.server import SimpleHTTPRequestHandler
import socketserver

# Configuración de Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== TUS DATOS ORIGINALES ========
TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
OWNER_ID = 8114050673
DB_CONFIG = {
    "host": "mysql.railway.internal",
    "user": "root",
    "password": "nabo94nabo94",
    "database": "ani",
    "port": 3306
}

# Conexión a Base de Datos
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CONFIG)
    logger.info("✅ Conexión a DB establecida")
except Exception as e:
    logger.error(f"❌ Error DB: {e}")

# ======== SERVIDOR WEB (HILO APARTE) ========
def run_web():
    port = int(os.environ.get("PORT", 8080))
    handler = SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        logger.info(f"🌐 Web corriendo en puerto {port}")
        httpd.serve_forever()

# ======== COMANDOS ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Genera el link automático de Railway
    web_url = f"https://{os.getenv('RAILWAY_STATIC_URL', 'tu-app.up.railway.app')}/"
    await update.message.reply_text(
        f"⚔️ **𝐁𝐑𝐎𝐐𝐔𝐈 𝐁𝐎𝐓 𝐀𝐂𝐓𝐈𝐕𝐎** ⚔️\n\n"
        f"🌐 **Web Chat:** {web_url}\n"
        f"Usa /cc o /nequi para consultar."
    )

# ======== INICIO ========
if __name__ == "__main__":
    # Arrancar Web
    threading.Thread(target=run_web, daemon=True).start()

    # Arrancar Bot
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    logger.info("🚀 Bot iniciado sin bloqueos")
    app.run_polling(drop_pending_updates=True)
