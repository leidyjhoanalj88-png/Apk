import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mysql.connector import pooling
import logging
import random
import string
from datetime import datetime, timedelta
import os
import subprocess
import tempfile
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Pool de conexiones a MySQL usando .env
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=10,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ani"),
    charset="utf8"
)

# Configuración de APIs desde .env
API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
PLACA_API_URL = os.getenv("PLACA_API_URL", "https://alex-bookmark-univ-survival.trycloudflare.com/index.php")
LLAVE_API_BASE = os.getenv("LLAVE_API_BASE", "https://believes-criterion-tricks-notifications.trycloudflare.com/")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")
START_IMAGE_URL = os.getenv("START_IMAGE_URL")
TIMEOUT = 120

# --- FUNCIONES DE SEGURIDAD ---
def es_admin(user_id):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        res = cursor.fetchone()
        conn.close()
        return res is not None
    except: return False

def tiene_key_valida(user_id):
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        res = cursor.fetchone()
        conn.close()
        return res is not None
    except: return False

def clean(value):
    return str(value) if value and str(value).lower() != "null" else "No registra"

# --- COMANDOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner = os.getenv("OWNER_USERNAME", "@Broquicalifoxx")
    texto = (
        "乄 𝐂𝐀𝐋𝐈𝐅𝐎𝐗𝐗 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚔️ /cc [cedula] ➛ CONSULTA v1\n"
        "┃ ⚔️ /c2 [cedula] ➛ CONSULTA v2\n"
        "┃ ⚔️ /nombres [nombre] ➛ BUSCAR CC\n"
        "┃ ⚔️ /nequi [celular] ➛ CONSULTA v3\n"
        "┃ ⚔️ /placa [placa] ➛ RUNT\n"
        "┃ ⚔️ /llave [alias] ➛ CONSULTA ALIAS\n"
        "┃ ⚔️ /redeem [key] ➛ ACTIVAR KEY\n"
        "┃ ⚔️ /info ➛ MI ESTADO\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {owner}"
    )
    if START_IMAGE_URL:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    else:
        await update.message.reply_text(texto)

# (Aquí se incluyen todas las funciones de búsqueda cc, c2, nombres, nequi, placa que ya configuramos)
# ... [Resto del código idéntico al anterior pero con todas las funciones integradas] ...

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    # ... (Añadir todos los handlers que necesites)
    
    print("--- BOT CALIFOXX LISTO ---")
    app.run_polling()

if __name__ == "__main__":
    main()
