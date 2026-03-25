import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mysql.connector import pooling
import logging
import os
import requests
from datetime import datetime

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN DE VARIABLES (IGUAL QUE EN TU RAILWAY) ========
# Estas variables coinciden exactamente con la imagen que me pasaste
TOKEN = os.getenv("TELEGRAM_TOK", "8048814862:AAHbxLQ_Ie7By5ygJN1tgoSnJO2ZqeY8RM4")
OWNER_ID = int(os.getenv("OWNER_ID", "8114050673"))

# Configuración de Base de Datos usando tus nombres (DB_HOST, DB_USER, etc.)
# IMPORTANTE: En Railway, cambia el valor de DB_HOST de "localhost" a "mysql.railway.internal"
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=10,
    host=os.getenv("DB_HOST", "mysql.railway.internal"), 
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "nabo94nabo94"),
    database=os.getenv("DB_NAME", "ani"),
    port=int(os.getenv("DB_PORT", 3306)),
    charset="utf8"
)

# APIs sacadas de tus variables
API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
START_IMAGE_URL = os.getenv("START_IMAGE_U", "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg")
NEQUI_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")

# ======== FUNCIONES DE APOYO ========

def tiene_key_valida(user_id):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if 'conn' in locals() and conn.is_connected(): cursor.close(); conn.close()

# ======== COMANDOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐏𝐀𝐁𝐋𝐎 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨... 𝐚𝐪𝐮𝐢 𝐭𝐨𝐝𝐨 𝐞𝐬𝐭𝐚 𝐜𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐚𝐝𝐨 ⚔️\n"
        "═════════════════════════\n"
        "┃ ⚔️ /start ➛ Menú\n"
        "┃ ⚔️ /cc ➛ Consulta CC\n"
        "┃ ⚔️ /nequi ➛ Consulta Nequi\n"
        "═════════════════════════\n"
        "👑 owner: @Broquicalifoxx"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

async def registrar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (user_id, telegram_username, date_registered) VALUES (%s, %s, %s)", 
                           (user_id, username, datetime.now()))
            conn.commit()
    except: pass
    finally:
        if 'conn' in locals() and conn.is_connected(): cursor.close(); conn.close()

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_usuario))
    
    logger.info("Bot iniciado con variables de Railway")
    application.run_polling()

if __name__ == "__main__":
    main()
