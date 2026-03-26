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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN CARGADA DESDE TUS VARIABLES DE RAILWAY ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "nabo94nabo94") # Cambiado de DB_PASSWORD a DB_PASS
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN") # Coincide con tu captura

# Configuraciones de Identidad
OWNER_USER = os.getenv("OWNER_USER", "@Broquicalifoxx")
OWNER_ID = int(os.getenv("OWNER_ID", 8114050673))
BOT_USER = "@doxeos09bot"

# ======== POOL DE CONEXIÓN ========
try:
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
    logger.info("✅ Pool de conexiones creado con éxito.")
except Exception as e:
    logger.error(f"❌ Error crítico al crear el pool: {e}")
    # Esto evitará que el bot crashee de inmediato si la DB tarda un poco
    pool = None

# ======== CONFIG APIs ========
API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
START_IMAGE_URL = os.getenv("START_IMAGE_URL", "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")
TIMEOUT = 120

# [ ... El resto de las funciones: tiene_key_valida, consultar_cedula, etc. se mantienen igual ... ]
# [ Para ahorrar espacio y que sea fácil de copiar, asegúrate de mantener todas las funciones del mensaje anterior ]

# IMPORTANTE: Asegúrate de que las funciones de búsqueda usen la variable 'pool' global.

def tiene_key_valida(user_id):
    if user_id == OWNER_ID:
        return True
    if not pool: return False
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except:
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

# ... (Copia aquí el resto de las funciones del bloque de código largo anterior) ...

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬, 𝐬𝐨𝐥𝐨 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 ⚔️\n"
        "═════════════════════════\n"
        f"👑 𝘿𝙚𝙨𝙖𝙧𝙧𝙤𝙡𝙡𝙖𝙙𝙤 𝙥𝙤𝙧: {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

# ======== MAIN ========
def main():
    if not TOKEN:
        logger.error("❌ No se encontró el TELEGRAM_TOKEN en las variables de entorno.")
        return

    application = Application.builder().token(TOKEN).build()

    # Añadir los handlers (Start, Help, CC, etc.) igual que antes
    application.add_handler(CommandHandler("start", start))
    # ... (añade aquí todos los CommandHandlers que tenías)

    logger.info("🚀 Bot Broquicali iniciado con variables de Railway.")
    application.run_polling()

if __name__ == "__main__":
    main()
