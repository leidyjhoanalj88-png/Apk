import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mysql.connector import pooling
import logging
import random
import string
from datetime import datetime, timedelta
import os
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuración de la conexión a la base de datos (Usando variables de entorno)
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=10,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ani"),
    charset="utf8"
)

# ======== CONFIGURACIÓN DE APIs ========
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")
START_IMAGE_URL = os.getenv("START_IMAGE_URL", "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg")
TIMEOUT = 120

# Funciones de utilidad
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

# Comandos del Bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner = os.getenv("OWNER_USERNAME", "@Broquicalifoxx")
    texto = (
        "乄 𝐂𝐀𝐋𝐈𝐅𝐎𝐗𝐗 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚙️ 𝐂𝐎𝐌𝐀𝐍𝐃𝐎𝐒 𝐃𝐈𝐒𝐏𝐎𝐍𝐈𝐁𝐋𝐄𝐒\n"
        "┃ ⚙️ 𝗕𝗼𝘁: @BroquicalifoxxBot\n"
        "┃ ⚔️ /cc ➛ CONSULTA v1\n"
        "┃ ⚔️ /c2 ➛ CONSULTA v2\n"
        "┃ ⚔️ /nequi ➛ CONSULTA v3\n"
        "┃ ⚔️ /info ➛ MI ESTADO\n"
        "┃ ⚔️ /redeem ➛ ACTIVAR KEY\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {owner}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def registrar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO users (user_id, telegram_username, date_registered) VALUES (%s, %s, %s)", 
                       (user.id, user.username, datetime.now()))
        conn.commit()
        conn.close()
    except Exception as e: logger.error(f"Error registro: {e}")

async def generar_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.message.from_user.id): return
    if len(context.args) < 2:
        await update.message.reply_text("Uso: /generar_key [ID] [DIAS]")
        return
    
    target_id = int(context.args[0])
    dias = int(context.args[1])
    key = "FOX-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    exp = datetime.now() + timedelta(days=dias)

    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_keys (key_value, user_id, expiration_date) VALUES (%s, %s, %s)", (key, target_id, exp))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"✅ Key Generada:\n`{key}`", parse_mode="Markdown")
    except Exception as e: await update.message.reply_text(f"Error: {e}")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    key = context.args[0]
    user_id = update.message.from_user.id
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_keys WHERE key_value=%s AND redeemed=FALSE", (key,))
        res = cursor.fetchone()
        if res:
            cursor.execute("UPDATE user_keys SET redeemed=TRUE, user_id=%s WHERE key_id=%s", (user_id, res['key_id']))
            conn.commit()
            await update.message.reply_text("✅ Suscripción activada correctamente.")
        else:
            await update.message.reply_text("❌ Key inválida o ya usada.")
        conn.close()
    except Exception as e: logger.error(e)

async def mostrar_datos_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ No tienes una suscripción activa.")
        return
    if not context.args: return
    cedula = context.args[0]
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        datos = cursor.fetchone()
        if datos:
            msg = f"👤 {datos['ANINombre1']} {datos['ANIApellido1']}\n🆔 {cedula}"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("No encontrado en DB local.")
        conn.close()
    except Exception as e: logger.error(e)

def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("Falta TELEGRAM_TOKEN en .env")
        return

    app = Application.builder().token(token).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", mostrar_datos_cedula))
    app.add_handler(CommandHandler("generar_key", generar_key))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_usuario))

    print("--- BOT CALIFOXX INICIADO ---")
    app.run_polling()

if __name__ == "__main__":
    main()
