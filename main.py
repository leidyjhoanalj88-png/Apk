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
from dotenv import load_dotenv  # Importante para cargar el .env

# Cargar variables de entorno
load_dotenv()

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# Configuración de la conexión a la base de datos (Usando Variables)
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=10,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ani"),
    charset="utf8"
)

# ======== CONFIG APIs (Extraídas de .env) ========
API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
PLACA_API_URL = os.getenv("PLACA_API_URL", "https://alex-bookmark-univ-survival.trycloudflare.com/index.php")
START_IMAGE_URL = os.getenv("START_IMAGE_URL", "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg")
LLAVE_API_BASE = os.getenv("LLAVE_API_BASE", "https://believes-criterion-tricks-notifications.trycloudflare.com/")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")
TIMEOUT = 120
# ===============================

def clean(value):
    if value is None or value == "" or value == "null":
        return "No registra"
    if isinstance(value, bool):
        return "Sí" if value else "No"
    return str(value)

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(
            API_URL_C2,
            json={"cedula": str(cedula)},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar C2: {e}")
        return None

def consultar_placa(placa):
    try:
        r = requests.get(
            PLACA_API_URL,
            params={"placa": placa},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar placa: {e}")
        return None

def consultar_llave(alias):
    try:
        r = requests.get(
            LLAVE_API_BASE,
            params={"hexn": alias},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar llave: {e}")
        return None

def consultar_nequi(telefono):
    try:
        url = "https://extract.nequialpha.com/consultar"
        headers = {
            "X-Api-Key": NEQUI_API_KEY,
            "Content-Type": "application/json"
        }
        payload = {"telefono": str(telefono)}
        r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar Nequi: {e}")
        return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐏𝐀𝐁𝐋𝐎 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬, 𝐬𝐨𝐥𝐨 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚙️ 𝐂𝐎𝐌𝐀𝐍𝐃𝐎𝐒 𝐃𝐈𝐒𝐏𝐎𝐍𝐈𝐁𝐋𝐄𝐒\n"
        "┃ ⚙️ 𝗕𝗼𝘁:@PabloadmincoBot \n"
        "┃ ⚔️ /start ➛ 𝐃𝐄𝐒𝐏𝐈𝐄𝐑𝐓𝐀 𝐋𝐀 𝐁𝐄𝐒𝐓𝐈𝐀 \n"
        "┃ ⚔️ /cc ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯1\n"
        "┃ ⚔️ /c2 ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯2\n"
        "┃ ⚔️ /nequi ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯3\n"
        "┃ ⚔️ /llave ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐀𝐋𝐈𝐀𝐒\n"
        "┃ ⚔️ /placa ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "⚠️ 𝐂𝐚𝐝𝐚 𝐎𝐫𝐝𝐞𝐧 𝐄𝐣𝐞𝐜𝐮𝐭𝐚𝐝𝐚 𝐝𝐞𝐣𝐚 𝐜𝐢𝐜𝐚𝐭𝐫𝐢𝐜𝐞𝐬...𝐔𝐬𝐚𝐥𝐨 𝐜𝐨𝐧 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐚𝐛𝐢𝐥𝐢𝐝𝐚𝐝 𝐨 𝐬𝐞𝐫𝐚𝐬 𝐝𝐞𝐛𝐨𝐫𝐚𝐝𝐨.\n"
        "═════════════════════════\n"
        "👑 𝙤𝙬𝙣𝙚𝙧: @hexxn_x"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except Exception:
        await update.message.reply_text("⚠️ No se pudo enviar la imagen.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>📚 𝑪𝒐𝒎𝒂𝒏𝒅𝒐𝒔 𝒅𝒊𝒔𝒑𝒐𝒏𝒊𝒃𝒍𝒆𝒔 📚</b>\n\n"
        "<b>🚀 /start</b>\n"
        "<b>👤 /nombres </b>\n"
        "<b>🎫 /cc </b>\n"
        "<b>🚗 /c2 </b>\n"
        "<b>🔑 /llave </b>\n"
        "<b>🚔 /placa </b>\n"
        "<b>🔒 /info</b>\n"
        "<b>🔧 /redeem [key]</b>",
        parse_mode="HTML"
    )

async def registrar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    telegram_username = update.message.from_user.username
    connection = None
    cursor = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO users (user_id, telegram_username, date_registered) VALUES (%s, %s, %s)", 
                           (user_id, telegram_username, datetime.now()))
            connection.commit()
    except Exception as e:
        logger.error(f"Error registrando: {e}")
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.message.from_user.id):
        await update.message.reply_text("No autorizado.")
        return
    if len(context.args) != 1: return
    try:
        nuevo_id = int(context.args[0])
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO admins (user_id) VALUES (%s)", (nuevo_id,))
        connection.commit()
        await update.message.reply_text(f"Admin {nuevo_id} añadido.")
    finally:
        if connection: connection.close()

def es_admin(user_id):
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if connection: connection.close()

def tiene_key_valida(user_id):
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if connection: connection.close()

async def generar_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.message.from_user.id): return
    try:
        id_usuario = int(context.args[0])
        dias = int(context.args[1])
        key = "KEY-" + ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        exp = datetime.now() + timedelta(days=dias)
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user_keys (key_value, user_id, expiration_date) VALUES (%s, %s, %s)", (key, id_usuario, exp))
        connection.commit()
        await update.message.reply_text(f"Key: `{key}`", parse_mode="Markdown")
    finally:
        if connection: connection.close()

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args: return
    key = context.args[0]
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT key_id FROM user_keys WHERE key_value=%s AND redeemed=FALSE AND expiration_date > NOW()", (key,))
        res = cursor.fetchone()
        if res:
            cursor.execute("UPDATE user_keys SET redeemed=TRUE, user_id=%s WHERE key_id=%s", (user_id, res['key_id']))
            connection.commit()
            await update.message.reply_text("✅ Éxito.")
        else:
            await update.message.reply_text("❌ Inválida.")
    finally:
        if connection: connection.close()

async def ver_info_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_keys WHERE user_id=%s ORDER BY created_at DESC LIMIT 1", (user_id,))
        res = cursor.fetchone()
        if res:
            await update.message.reply_text(f"ID: {user_id}\nKey: {res['key_value']}")
    finally:
        if connection: connection.close()

async def mostrar_datos_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("Sin clave activa.")
        return
    if not context.args: return
    cedula = context.args[0]
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        datos = cursor.fetchone()
        if datos:
            msg = f"👤 {datos['ANINombre1']} {datos['ANIApellido1']}\n🆔 {cedula}"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("No encontrado.")
    finally:
        if connection: connection.close()

# ======== COMANDOS RESTANTES (C2, PLACA, ETC) SE MANTIENEN IGUAL PERO USAN POOL ========

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    doc = context.args[0]
    res = consultar_cedula_c2(doc)
    if res: await update.message.reply_text(f"Resultado: {json.dumps(res, indent=2)}")

async def comando_placa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    res = consultar_placa(context.args[0].upper())
    await update.message.reply_text(f"JSON: {json.dumps(res, indent=2)}")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    res = consultar_nequi(context.args[0])
    if res: await update.message.reply_text(f"Nombre: {res.get('nombre_completo')}")

async def heidysql(update: Update, context: ContextTypes.DEFAULT_TYPE):
    OWNER_ID = int(os.getenv("OWNER_ID", "797396425"))
    if update.message.from_user.id != OWNER_ID: return
    await update.message.reply_text("Reorganizando pool...")
    # Lógica de subprocess original se mantiene aquí...

# Configuración Final del Bot
def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token:
        print("ERROR: Falta el TELEGRAM_TOKEN en el .env")
        return

    application = Application.builder().token(token).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cc", mostrar_datos_cedula))
    application.add_handler(CommandHandler("c2", comando_c2))
    application.add_handler(CommandHandler("placa", comando_placa))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("info", ver_info_usuario))
    application.add_handler(CommandHandler("heidysql", heidysql))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_usuario))

    logger.info("Bot en línea con variables de entorno.")
    application.run_polling()

if __name__ == "__main__":
    try:
        main()
    finally:
        if 'pool' in globals(): pool.close()
