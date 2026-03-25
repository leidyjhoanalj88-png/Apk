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

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@BroquicalifoxxBot"
# =========================================================

# Pool de conexiones corregida para Railway
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
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
TIMEOUT = 120

def clean(value):
    if value is None or value == "" or value == "null":
        return "No registra"
    if isinstance(value, bool):
        return "Sí" if value else "No"
    return str(value)

# --- FUNCIONES DE CONSULTA ---
def test_db():
    try:
        conn = pool.get_connection()
        conn.close()
        return "CONECTADA ✅"
    except:
        return "ERROR ❌"

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(API_URL_C2, json={"cedula": str(cedula)}, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
        return r.json()
    except: return None

def consultar_placa(placa):
    try:
        r = requests.get(PLACA_API_URL, params={"placa": placa}, timeout=TIMEOUT)
        return r.json()
    except: return None

def consultar_llave(alias):
    try:
        r = requests.get(LLAVE_API_BASE, params={"hexn": alias}, timeout=TIMEOUT)
        return r.json()
    except: return None

def consultar_nequi(telefono):
    try:
        url = "https://extract.nequialpha.com/consultar"
        headers = {"X-Api-Key": "M43289032FH23B", "Content-Type": "application/json"}
        r = requests.post(url, json={"telefono": str(telefono)}, headers=headers, timeout=TIMEOUT)
        return r.json()
    except: return None

# ======== COMANDOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_status = test_db()
    texto = (
        "乄 𝐏𝐀𝐁𝐋𝐎 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬, 𝐬𝐨𝐥𝐨 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"┃ ⚙️ 𝐁𝐨𝐭: {BOT_USER}\n"
        "┃ ⚔️ /start ➛ 𝐃𝐄𝐒𝐏𝐈𝐄𝐑𝐓𝐀 𝐋𝐀 𝐁𝐄𝐒𝐓𝐈𝐀 \n"
        "┃ ⚔️ /cc ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯1\n"
        "┃ ⚔️ /c2 ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯2\n"
        "┃ ⚔️ /nequi ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯3\n"
        "┃ ⚔️ /llave ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐀𝐋𝐈𝐀𝐒\n"
        "┃ ⚔️ /placa ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        f"┃ 🔋 𝐃𝐁: {db_status}\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "⚠️ 𝐂𝐚𝐝𝐚 𝐎𝐫𝐝𝐞𝐧 𝐄𝐣𝐞𝐜𝐮𝐭𝐚𝐝𝐚 𝐝𝐞𝐣𝐚 𝐜𝐢𝐜𝐚𝐭𝐫𝐢𝐜𝐞𝐬... 𝐔𝐬𝐚𝐥𝐨 𝐜𝐨𝐧 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐚𝐛𝐢𝐥𝐢𝐝𝐚𝐝.\n"
        "═════════════════════════\n"
        f"👑 𝙤𝙬𝙣𝙚rer: {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

async def mostrar_datos_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes una clave activa.")
        return
    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/cc 12345678`", parse_mode="Markdown")
        return
    
    cedula = context.args[0]
    datos = buscar_cedula(cedula, user_id=user_id)

    if datos:
        mensaje = (
            f"🪪 CC: `{cedula}`\n"
            f"👤 Nombres: `{datos['ANINombre1']} {datos['ANINombre2']}`\n"
            f"👤 Apellidos: `{datos['ANIApellido1']} {datos['ANIApellido2']}`\n"
            f"📱 Teléfono: `{datos['ANITelefono']}`\n"
            f"🏚 Dirección: `{datos['ANIDireccion']}`\n\n"
            f"🛡 Creditos: {OWNER_USER}"
        )
        await update.message.reply_text(mensaje, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No se encontraron datos.")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ Key requerida.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /nequi <telefono>")
        return

    res = consultar_nequi(context.args[0])
    if res:
        mensaje = (
            f"🔎 Resultado Nequi\n"
            f"📱 Teléfono: {res.get('telefono')}\n"
            f"🆔 Cédula: {res.get('cedula')}\n"
            f"👤 Nombre: {res.get('nombre_completo')}\n\n"
            f"🔖 by {OWNER_USER}"
        )
        await update.message.reply_text(mensaje)
    else:
        await update.message.reply_text("❌ Error en consulta.")

# --- MANTENIMIENTO DE FUNCIONES EXISTENTES ---
# (Aquí siguen todas tus funciones de buscar_cedula, registrar_usuario, redeem, etc.)
# Asegúrate de mantener 'tiene_key_valida', 'es_admin', 'buscar_cedula' tal cual las tenías.

def tiene_key_valida(user_id):
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        result = cursor.fetchone()
        return result is not None
    except: return False
    finally:
        if 'connection' in locals()
