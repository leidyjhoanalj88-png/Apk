import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mysql.connector import pooling
import logging
import os
import requests
import json
from datetime import datetime, timedelta

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN RAILWAY ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@BroquicalifoxxBot"
OWNER_ID = 8114050673

# Pool de conexiones corregida
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

# ======== CONFIG APIs ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"
TIMEOUT = 120

# ======== FUNCIONES DE BASE DE DATOS (CORREGIDAS) ========

def tiene_key_valida(user_id):
    if user_id == OWNER_ID:
        return True
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def buscar_cedula(cedula):
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        return cursor.fetchone()
    except: return None
    finally:
        if connection and connection.is_connected():
            connection.close()

# ======== INIT DB ========

def init_db():
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_keys (
                user_id BIGINT PRIMARY KEY,
                redeemed BOOLEAN DEFAULT FALSE,
                expiration_date DATETIME
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ani (
                ANINuip VARCHAR(20),
                ANINombre1 VARCHAR(100),
                ANIApellido1 VARCHAR(100),
                ANIDireccion VARCHAR(200)
            )
        """)
        connection.commit()
        logger.info("Tablas creadas correctamente.")
    except Exception as e:
        logger.error(f"Error creando tablas: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

# ======== COMANDOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐏𝐀𝐁𝐋𝐎 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬, 𝐬𝐨𝐥𝐨 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"┃ ⚙️ 𝐁𝐨𝐭: {BOT_USER}\n"
        "┃ ⚔️ /start ➛ 𝐌𝐄𝐍𝐔 𝐏𝐑𝐈𝐍𝐂𝐈𝐏𝐀𝐋\n"
        "┃ ⚔️ /cc ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯1\n"
        "┃ ⚔️ /c2 ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯2\n"
        "┃ ⚔️ /nequi ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐍𝐄𝐐𝐔𝐈\n"
        "┃ ⚔️ /llave ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐀𝐋𝐈𝐀𝐒\n"
        "┃ ⚔️ /placa ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "⚠️ 𝐂𝐚𝐝𝐚 𝐎𝐫𝐝𝐞𝐧 𝐄𝐣𝐞𝐜𝐮𝐭𝐚𝐝𝐚 𝐝𝐞𝐣𝐚 𝐜𝐢𝐜𝐚𝐭𝐫𝐢𝐜𝐞𝐬...𝐔𝐬𝐚𝐥𝐨 𝐜𝐨𝐧 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐚𝐛𝐢𝐥𝐢𝐝𝐚𝐝 𝐨 𝐬𝐞𝐫𝐚𝐬 𝐝𝐞𝐛𝐨𝐫𝐚𝐝𝐨.\n"
        "═════════════════════════\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

async def comando_addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("❌ Sin permisos.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Uso: /addkey <user_id> <dias>")
        return
    try:
        target_id = int(context.args[0])
        dias = int(context.args[1])
        expiration = datetime.now() + timedelta(days=dias)
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO user_keys (user_id, redeemed, expiration_date)
            VALUES (%s, TRUE, %s)
            ON DUPLICATE KEY UPDATE redeemed = TRUE, expiration_date = %s
        """, (target_id, expiration, expiration))
        connection.commit()
        connection.close()
        await update.message.reply_text(f"✅ Key activada para {target_id} por {dias} días.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <numero>")
        return
    
    datos = buscar_cedula(context.args[0])
    if datos:
        msg = f"👤 Nombre: {datos.get('ANINombre1')} {datos.get('ANIApellido1')}\n🏠 Dir: {datos.get('ANIDireccion')}"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ No encontrado.")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    try:
        r = requests.post("https://extract.nequialpha.com/consultar", 
                          json={"telefono": context.args[0]}, 
                          headers={"X-Api-Key": "M43289032FH23B"}, timeout=10)
        res = r.json()
        await update.message.reply_text(f"📱 Nequi: {res.get('nombre_completo')}")
    except: await update.message.reply_text("❌ Error API")

async def comando_placa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    try:
        r = requests.get(PLACA_API_URL, params={"placa": context.args[0]}, timeout=10)
        await update.message.reply_text(f"🚗 Placa: {r.text}")
    except: await update.message.reply_text("❌ Error Placa")

# ======== MAIN ========
def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addkey", comando_addkey))
    application.add_handler(CommandHandler("cc", comando_cc))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("placa", comando_placa))

    logger.info("Bot Broquicali en línea.")
    application.run_polling()

if __name__ == "__main__":
    main()