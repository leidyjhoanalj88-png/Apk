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

# Configuración de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN DESDE RAILWAY ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Identidad
OWNER_USER = os.getenv("OWNER_USER", "@Broquicalifoxx")
OWNER_ID = int(os.getenv("OWNER_ID", 8114050673))
BOT_USER = "@doxeos09bot"

# APIs
API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
START_IMAGE_URL = os.getenv("START_IMAGE_URL", "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")
TIMEOUT = 120

# Crear Pool
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="pool_db",
        pool_size=15,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=int(DB_PORT),
        charset="utf8"
    )
    logger.info("✅ Pool de conexiones DB listo.")
except Exception as e:
    logger.error(f"❌ Error DB: {e}")
    pool = None

# ======== UTILIDADES ========

def clean(value):
    if value is None or value == "" or value == "null": return "No registra"
    return "Sí" if value is True else "No" if value is False else str(value)

def obtener_lugar(codigo):
    if not pool or not codigo: return "Desconocido"
    try:
        codigo_limpio = str(codigo)[3:8]
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT lug FROM lug_ori WHERE cod_lug LIKE %s", (f"%{codigo_limpio}%",))
        res = cursor.fetchone()
        conn.close()
        return res['lug'] if res else "No encontrado"
    except: return "Error"

# ======== SISTEMA DE PERMISOS ========

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    if not pool: return False
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        res = cursor.fetchone()
        conn.close()
        return res is not None
    except: return False

def es_admin(user_id):
    if user_id == OWNER_ID: return True
    if not pool: return False
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        res = cursor.fetchone()
        conn.close()
        return res is not None
    except: return False

# ======== COMANDOS PRINCIPALES ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"┃ ⚙️ 𝐁𝐨𝐭: {BOT_USER}\n"
        "┃ ⚔️ /cc - Consulta Cédula v1\n"
        "┃ ⚔️ /c2 - Consulta Cédula v2\n"
        "┃ ⚔️ /nequi - Consulta Nequi\n"
        "┃ ⚔️ /placa - Consulta Placa\n"
        "┃ ⚔️ /nombres - Buscar por Nombre\n"
        "┃ ⚔️ /llave - Consulta Alias\n"
        "┃ ⚔️ /redeem - Activar Key\n"
        "┃ ⚔️ /info - Mi Suscripción\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝘿𝙚𝙨𝙖𝙧𝙧𝙤𝙡𝙡𝙖𝙙𝙤 𝙥𝙤𝙧: {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin suscripción.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <cedula>")
        return
    
    cedula = context.args[0]
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
    d = cursor.fetchone()
    conn.close()

    if d:
        msg = (
            f"🪪 CC: `{d['ANINuip']}`\n"
            f"👤 Nombre: `{d['ANINombre1']} {d['ANINombre2'] or ''}`\n"
            f"👤 Apellidos: `{d['ANIApellido1']} {d['ANIApellido2'] or ''}`\n"
            f"📅 Nacimiento: `{d['ANIFchNacimiento']}`\n"
            f"🏚 Dirección: `{d['ANIDireccion'] or 'No registra'}`\n"
            f"📱 Teléfono: `{d['ANITelefono'] or 'No registra'}`\n"
            f"📍 Origen: `{obtener_lugar(d['LUGIdNacimiento'])}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No encontrado.")

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    try:
        r = requests.post(API_URL_C2, json={"cedula": context.args[0]}, timeout=TIMEOUT).json()
        if r.get("success"):
            data = r["data"]
            res = f"📄 RESULTADO C2\n🆔 ID: {data.get('cedula')}\n👤 Nombre: {data.get('primer_nombre')} {data.get('primer_apellido')}\n📍 Ciudad: {data.get('municipio_residencia')}"
            await update.message.reply_text(res)
    except: await update.message.reply_text("❌ Error API C2")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    try:
        r = requests.post("https://extract.nequialpha.com/consultar", 
                          json={"telefono": context.args[0]}, 
                          headers={"X-Api-Key": NEQUI_API_KEY}, timeout=TIMEOUT).json()
        msg = f"📱 NEQUI\n👤 Nombre: {r.get('nombre_completo')}\n🆔 CC: {r.get('cedula')}"
        await update.message.reply_text(msg)
    except: await update.message.reply_text("❌ Error Nequi")

async def comando_placa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    try:
        r = requests.get(PLACA_API_URL, params={"placa": context.args[0].upper()}).json()
        await update.message.reply_text(f"```json\n{json.dumps(r, indent=2)}\n```", parse_mode="Markdown")
    except: await update.message.reply_text("❌ Error Placa")

async def comando_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    key = context.args[0]
    user_id = update.message.from_user.id
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT key_id FROM user_keys WHERE key_value = %s AND redeemed = FALSE", (key,))
        res = cursor.fetchone()
        if res:
            cursor.execute("UPDATE user_keys SET redeemed = TRUE, user_id = %s WHERE key_id = %s", (user_id, res['key_id']))
            conn.commit()
            await update.message.reply_text("✅ Key activada correctamente.")
        else:
            await update.message.reply_text("❌ Key inválida o usada.")
        conn.close()
    except: pass

async def comando_genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.message.from_user.id): return
    dias = int(context.args[0]) if context.args else 30
    key = "KEY-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    exp = datetime.now() + timedelta(days=dias)
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_keys (key_value, expiration_date) VALUES (%s, %s)", (key, exp))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"🔑 Key Generada: `{key}`\n⏳ Duración: {dias} días", parse_mode="Markdown")

# ======== BUCLE PRINCIPAL ========

def main():
    if not TOKEN: return
    app = Application.builder().token(TOKEN).build()

    # Comandos Usuario
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("c2", comando_c2))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("placa", comando_placa))
    app.add_handler(CommandHandler("redeem", comando_redeem))
    
    # Comandos Admin
    app.add_handler(CommandHandler("genkey", comando_genkey))

    logger.info("🚀 Bot Broquicali Operacional.")
    app.run_polling()

if __name__ == "__main__":
    main()
