import os
import logging
import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Logs para ver errores en Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== VARIABLES SEGÚN TU IMAGEN .ENV ========
TOKEN = os.getenv("TELEGRAM_TOKEN", "8717607121:AAEjR8NdGjOCASuqY1fV5bL1CYNG4nBpDg")
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal") # IMPORTANTE: Cambia localhost en el panel
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = int(os.getenv("DB_PORT", 3306))

def conectar_db():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME,
            port=DB_PORT,
            connect_timeout=5
        )
    except Exception as e:
        logger.error(f"Error conectando a DB: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = conectar_db()
    status = "CONECTADA ✅" if conn and conn.is_connected() else "ERROR EN DB ❌ (Cambia localhost)"
    if conn: conn.close()
    
    await update.message.reply_text(
        f"⚔️ PABLO MENU ⚔️\n\nBase de Datos: {status}\n\nUsa /nequi o /cc"
    )

def main():
    # drop_pending_updates=True limpia el error de "Conflict" y mensajes viejos
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    logger.info("🚀 Bot encendido con el nuevo Token")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
