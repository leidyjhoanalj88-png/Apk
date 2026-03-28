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
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# Configuración de Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN DE ENTORNO ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")

OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# ======== POOL DE CONEXIONES MYSQL ========
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=15, # Aumentado para mayor tráfico
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    port=int(DB_PORT),
    charset="utf8"
)

# APIs EXTERNAS
COLZIA_BASE_URL = "https://ios.colzia.cc"
COLZIA_BEARER_TOKEN = os.getenv("COLZIA_BEARER_TOKEN", "")
NEQUI_ALPHA_URL = "https://extract.nequialpha.com/consultar"
NEQUI_ALPHA_KEY = os.getenv("NEQUI_ALPHA_KEY", "Z5k4Y1n4n0vS")
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"

# ======== FUNCIONES DE BASE DE DATOS (ANI) ========

def buscar_cedula_local(cedula):
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM ani WHERE ANINuip = %s LIMIT 1"
        cursor.execute(query, (cedula,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error DB local: {e}")
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

# ======== COMANDOS DEL BOT ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"┃ ⚔️ /cc      ➛ 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯1 (Local)\n"
        "┃ ⚔️ /nequi   ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐍𝐄𝐐𝐔𝐈\n"
        "┃ ⚔️ /sisben  ➛ 𝐒𝐈𝐒𝐁𝐄𝐍 𝐈𝐕\n"
        "┃ ⚔️ /redeem  ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐊𝐄𝐘\n"
        "┃ ⚔️ /info    ➛ 𝐌𝐈 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝘿𝙚𝙨𝙖𝙧𝙧𝙤𝙡𝙡𝙖𝙙𝙤 𝙥𝙤𝙧: {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes una Key activa. Contacta a @Broquicalifoxx")
        return

    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <cedula>")
        return

    cedula = context.args[0]
    res = buscar_cedula_local(cedula)
    
    if res:
        msg = (
            f"🪪 *DATOS ENCONTRADOS* (Local)\n\n"
            f"🆔 CC: `{res['ANINuip']}`\n"
            f"👤 Nombre: {res['ANINombre1']} {res.get('ANINombre2','')}\n"
            f"👤 Apellidos: {res['ANIApellido1']} {res.get('ANIApellido2','')}\n"
            f"📅 Nacimiento: {res.get('ANIFchNacimiento','No registra')}\n"
            f"🏚 Dirección: {res.get('ANIDireccion','No registra')}\n"
            f"📱 Teléfono: {res.get('ANITelefono','No registra')}\n"
            f"\n💻 Desarrollado por {OWNER_USER}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No se encontró en la base de datos local.")

# [Aquí irían las demás funciones de Nequi y Sisben que ya tenemos configuradas]

def main():
    # Inicializar tablas si no existen
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS user_keys (user_id BIGINT PRIMARY KEY, redeemed BOOLEAN, expiration_date DATETIME, key_value VARCHAR(50))")
    conn.commit()
    conn.close()

    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    # Agregar handlers para sisben, nequi, redeem, etc.

    print("🚀 Bot Broquicali iniciado con éxito")
    app.run_polling()

if __name__ == "__main__":
    main()
