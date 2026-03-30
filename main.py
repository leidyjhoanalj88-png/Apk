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
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN DE IDENTIDAD ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")

OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# ======== CONFIG APIs & TÚNELES ========
API_HEXN_DOX = "https://par-bottles-straight-bernard.trycloudflare.com/hexn-dox-api"
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
COLZIA_BEARER_TOKEN = os.getenv("COLZIA_BEARER_TOKEN", "")

# ======== POOL DE BASE DE DATOS (REFORZADO PARA RENDER) ========
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=15,
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    port=int(DB_PORT),
    charset="utf8",
    connect_timeout=20
)

# ======== UTILIDADES DE LIMPIEZA ========
def clean(value):
    if value is None or value == "" or value == "null":
        return "No registra"
    if isinstance(value, bool):
        return "Sí" if value else "No"
    return str(value)

# ======== FUNCIONES DE CONSULTA EXTERNA ========

def consultar_hexn_api(cedula):
    """Nueva API Hexn Dox"""
    try:
        r = requests.get(f"{API_HEXN_DOX}?cc={cedula}", timeout=15)
        return r.json() if r.status_code == 200 else None
    except: return None

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(API_URL_C2, json={"cedula": str(cedula)}, timeout=15)
        return r.json()
    except: return None

def consultar_nequi(telefono):
    headers = {"X-Api-Key": "Z5k4Y1n4n0vS", "Content-Type": "application/json"}
    try:
        r = requests.post("https://extract.nequialpha.com/consultar", 
                          json={"telefono": str(telefono)}, headers=headers, timeout=15)
        return r.json()
    except: return None

# ======== LÓGICA DE BASE DE DATOS LOCAL (ANI) ========

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if conn: conn.close()

def buscar_cedula_db(cedula):
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        return cursor.fetchone()
    except: return None
    finally:
        if conn: conn.close()

# ======== SCRAPER SISBEN IV ========

def consultar_sisben(tipo, numero):
    url_sis = "https://reportes.sisben.gov.co/dnp_sisbenconsulta"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        session = requests.Session()
        r = session.get(url_sis, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "__RequestVerificationToken"}).get("value")
        data = {"TipoID": tipo, "documento": numero, "__RequestVerificationToken": token}
        r_post = session.post(url_sis, data=data, timeout=15)
        
        soup_res = BeautifulSoup(r_post.text, "html.parser")
        res = {}
        g = soup_res.find("p", class_="text-white")
        if g: res["grupo"] = g.get_text(strip=True)
        # (Aquí puedes expandir la extracción de campos específicos como nombres/municipio)
        return res if res else None
    except: return None

# ======== COMANDOS DEL BOT ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 **𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨** ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬 ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"┃ ⚙️ **𝐁𝐨𝐭:** {BOT_USER}\n"
        "┃ ⚔️ `/start` ➛ 𝐌𝐄𝐍𝐔 𝐏𝐑𝐈𝐍𝐂𝐈𝐏𝐀𝐋\n"
        "┃ ⚔️ `/cc` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯1\n"
        "┃ ⚔️ `/c2` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯2\n"
        "┃ ⚔️ `/nequi` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐍𝐄𝐐𝐔𝐈\n"
        "┃ ⚔️ `/placa` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        "┃ ⚔️ `/sisben` ➛ 𝐒𝐈𝐒𝐁𝐄𝐍 𝐈𝐕\n"
        "┃ ⚔️ `/redeem` ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐊𝐄𝐘\n"
        "┃ ⚔️ `/info` ➛ 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 **𝘿𝙚𝙨𝙖𝙧𝙧𝙤𝙡𝙡𝙖𝙙𝙤 𝙥𝙤𝙧:** {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto, parse_mode="Markdown")

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: `/cc <cedula>`")
        return

    cc = context.args[0]
    m = await update.message.reply_text(f"⏳ **Consultando Matrix:** `{cc}`...")

    # Consultar DB Local + API Hexn Dox
    db = buscar_cedula_db(cc)
    api = consultar_hexn_api(cc)

    if db or api:
        nombre = db.get('ANINombre1') if db else api.get('nombre', 'No registra')
        ape1 = db.get('ANIApellido1') if db else ""
        
        res = (
            "⚔️ **RESULTADO ENCONTRADO** ⚔️\n"
            "═════════════════════════\n"
            f"👤 **Nombres:** `{nombre} {db.get('ANINombre2', '') if db else ''}`\n"
            f"👤 **Apellidos:** `{ape1} {db.get('ANIApellido2', '') if db else ''}`\n"
            f"🆔 **Documento:** `{cc}`\n"
            f"📅 **Nacimiento:** `{db.get('ANIFchNacimiento', 'N/A') if db else 'N/A'}`\n"
            f"🏠 **Dirección:** `{db.get('ANIDireccion', 'No registra') if db else 'No registra'}`\n"
            "═════════════════════════\n"
            f"💻 By {OWNER_USER}"
        )
        await m.edit_text(res, parse_mode="Markdown")
    else:
        await m.edit_text("❌ No se registraron datos.")

async def comando_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    key = context.args[0]
    uid = update.message.from_user.id
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_keys WHERE key_value = %s AND redeemed = FALSE", (key,))
        result = cursor.fetchone()
        if result:
            exp = datetime.now() + timedelta(days=30) # Ejemplo 30 días
            cursor.execute("UPDATE user_keys SET redeemed = TRUE, user_id = %s, expiration_date = %s WHERE key_id = %s", 
                           (uid, exp, result['key_id']))
            conn.commit()
            await update.message.reply_text(f"✅ **KEY ACTIVADA**\nExpira: `{exp.date()}`")
        else:
            await update.message.reply_text("❌ Key inválida.")
    finally:
        if conn: conn.close()

# ======== INICIO DEL BOT ========

def main():
    app = Application.builder().token(TOKEN).build()

    # Registro de comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("redeem", comando_redeem))
    # (Añadir /nequi, /sisben, /placa con la misma lógica de los otros)

    logger.info("🚀 BROQUI-BOT ONLINE")
    app.run_polling()

if __name__ == "__main__":
    main()
