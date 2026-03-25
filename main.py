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
import tempfile
import subprocess
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Pool de conexiones a MySQL
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=10,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ani"),
    charset="utf8"
)

# Configuración de APIs
API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
PLACA_API_URL = os.getenv("PLACA_API_URL", "https://alex-bookmark-univ-survival.trycloudflare.com/index.php")
LLAVE_API_BASE = os.getenv("LLAVE_API_BASE", "https://believes-criterion-tricks-notifications.trycloudflare.com/")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")
START_IMAGE_URL = os.getenv("START_IMAGE_URL")
TIMEOUT = 120

# --- FUNCIONES DE APOYO ---
def clean(value):
    return str(value) if value and str(value).lower() != "null" else "No registra"

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

# --- LÓGICA DE BÚSQUEDA (Extraída de tu archivo) ---
def obtener_lugar(codigo):
    try:
        codigo_limpio = str(codigo)[3:8] if len(str(codigo)) >= 8 else None
        if not codigo_limpio: return "Desconocido"
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT lug FROM lug_ori WHERE cod_lug LIKE %s", (f"%{codigo_limpio}%",))
        res = cursor.fetchone()
        conn.close()
        return res['lug'] if res else "No encontrado"
    except: return "Error"

# --- COMANDOS PRINCIPALES ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner = os.getenv("OWNER_USERNAME", "@Broquicalifoxx")
    texto = (
        "乄 𝐂𝐀𝐋𝐈𝐅𝐎𝐗𝐗 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚙️ 𝐂𝐎𝐌𝐀𝐍𝐃𝐎𝐒 𝐃𝐈𝐒𝐏𝐎𝐍𝐈𝐁𝐋𝐄𝐒\n"
        "┃ ⚔️ /cc [cedula] ➛ CONSULTA v1\n"
        "┃ ⚔️ /c2 [cedula] ➛ CONSULTA v2\n"
        "┃ ⚔️ /nombres [nombre] ➛ BUSCAR CC\n"
        "┃ ⚔️ /nequi [celular] ➛ CONSULTA v3\n"
        "┃ ⚔️ /placa [placa] ➛ RUNT\n"
        "┃ ⚔️ /info ➛ MI ESTADO\n"
        "┃ ⚔️ /redeem [key] ➛ ACTIVAR\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {owner}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def consulta_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        return await update.message.reply_text("❌ Sin suscripción activa.")
    
    cedula = context.args[0] if context.args else None
    if not cedula: return
    
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
    d = cursor.fetchone()
    conn.close()

    if d:
        msg = (
            f"🪪 CC: `{cedula}`\n"
            f"👤 Nombres: `{d['ANINombre1']} {clean(d['ANINombre2'])}`\n"
            f"👤 Apellidos: `{d['ANIApellido1']} {clean(d['ANIApellido2'])}`\n"
            f"👨 Padre: `{clean(d['ANINombresPadre'])}`\n"
            f"👩 Madre: `{clean(d['ANINombresMadre'])}`\n"
            f"🏠 Dirección: `{clean(d['ANIDireccion'])}`\n"
            f"📍 Lugar Nac: `{obtener_lugar(d['LUGIdNacimiento'])}`"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("No encontrado.")

async def consulta_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    tel = context.args[0] if context.args else None
    if not tel: return

    try:
        r = requests.post("https://extract.nequialpha.com/consultar", 
                         json={"telefono": tel}, 
                         headers={"X-Api-Key": NEQUI_API_KEY}, timeout=TIMEOUT)
        data = r.json()
        res = (f"🔎 Resultado Nequi\n\n🆔 CC: {data.get('cedula')}\n👤 Nombre: {data.get('nombre_completo')}\n"
               f"📍 Municipio: {data.get('municipio')}\n🔖 by @Broquicalifoxx")
        await update.message.reply_text(res)
    except: await update.message.reply_text("Error en API Nequi.")

# --- ADMINISTRACIÓN ---
async def generar_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.message.from_user.id): return
    target_id, dias = int(context.args[0]), int(context.args[1])
    key = "FOX-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    exp = datetime.now() + timedelta(days=dias)
    
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_keys (key_value, user_id, expiration_date) VALUES (%s, %s, %s)", (key, target_id, exp))
    conn.commit()
    conn.close()
    await update.message.reply_text(f"✅ Key: `{key}`", parse_mode="Markdown")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    key = context.args[0] if context.args else None
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_keys SET redeemed=TRUE, user_id=%s WHERE key_value=%s AND redeemed=FALSE", (update.message.from_user.id, key))
    conn.commit()
    conn.close()
    await update.message.reply_text("✅ Activado.")

def main():
    app = Application.builder().token(os.getenv("TELEGRAM_TOKEN")).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", consulta_cc))
    app.add_handler(CommandHandler("nequi", consulta_nequi))
    app.add_handler(CommandHandler("generar_key", generar_key))
    app.add_handler(CommandHandler("redeem", redeem))
    app.run_polling()

if __name__ == "__main__":
    main()
