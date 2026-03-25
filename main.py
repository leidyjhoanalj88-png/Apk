import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging
import os

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== VARIABLES SEGÚN TU CAPTURA DE RAILWAY ========
TOKEN = os.getenv("TELEGRAM_TOKEN")
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal") # Cambia localhost en Railway por esto
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = int(os.getenv("DB_PORT", 3306))
IMG_URL = os.getenv("START_IMAGE_URL", "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg")

# Función de conexión
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            port=DB_PORT,
            charset="utf8"
        )
    except Exception as e:
        logger.error(f"❌ Error conectando a la DB en {DB_HOST}: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    if conn and conn.is_connected():
        status = "✅ BASE DE DATOS: CONECTADA"
        conn.close()
    else:
        status = "❌ BASE DE DATOS: ERROR (Revisa DB_HOST)"
    
    await update.message.reply_photo(
        photo=IMG_URL, 
        caption=f"乄 𝐏𝐀𝐁𝐋𝐎 𝗠𝗘𝗡𝗨 ⚔️\n\n{status}\n\n👑 Owner: @Broquicalifoxx",
        parse_mode="Markdown"
    )

def main():
    if not TOKEN:
        logger.error("Falta la variable TELEGRAM_TOKEN")
        return

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    logger.info(f"Bot iniciado. Intentando conectar a: {DB_HOST}")
    app.run_polling()

if __name__ == "__main__":
    main()
