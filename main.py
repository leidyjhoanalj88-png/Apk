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

# ======== CONFIGURACIÓN ========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")

OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# Pool de conexiones
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db", pool_size=15, host=DB_HOST, user=DB_USER,
    password=DB_PASS, database=DB_NAME, port=int(DB_PORT), charset="utf8"
)

# APIs
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
COLZIA_BASE_URL = "https://ios.colzia.cc"
COLZIA_BEARER_TOKEN = os.getenv("COLZIA_BEARER_TOKEN", "") 
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"

# ======== UTILIDADES ========

def clean(value):
    return str(value) if value and value != "null" else "No registra"

def c2_clean(text):
    if not text: return "No registra"
    try: return text.encode("latin-1").decode("utf-8")
    except: return text

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

# ======== FUNCIONES DE CONSULTA (APIS VIVAS) ========

def consultar_salud_total(cedula):
    try:
        r = requests.get(f"https://prestadores.saludtotal.com.co/api/afiliado/consultar/{cedula}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(API_URL_C2, json={"cedula": str(cedula)}, timeout=15)
        return r.json() if r.status_code == 200 else None
    except: return None

# ======== COMANDOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "┃ ⚔️ /cc [cedula] ➛ 𝐀𝐍𝐈\n"
        "┃ ⚔️ /c1 [cedula] ➛ 𝐒𝐀𝐋𝐔𝐃 𝐓𝐎𝐓𝐀𝐋\n"
        "┃ ⚔️ /c2 [cedula] ➛ 𝐃𝐎𝐗𝐈𝐍𝐆\n"
        "┃ ⚔️ /nequi [cel] ➛ 𝐍𝐄𝐐𝐔𝐈\n"
        "┃ ⚔️ /sisben [t] [d] ➛ 𝐒𝐈𝐒𝐁𝐄𝐍\n"
        "┃ ⚔️ /placa [placa] ➛ 𝐑𝐔𝐍𝐓\n"
        "┃ ⚔️ /info ➛ 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "═════════════════════════\n"
        f"👑 𝘿𝙚𝙨𝙖𝙧𝙧𝙤𝙡𝙡𝙖𝙙𝙤 𝙥𝙤𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <cedula>")
        return
    
    cedula = context.args[0]
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        datos = cursor.fetchone()
        if datos:
            msg = (
                f"🪪 *REGISTRO ANI*\n\n"
                f"👤 Nombres: `{c2_clean(datos.get('ANINombre1'))} {c2_clean(datos.get('ANINombre2')) or ''}`\n"
                f"👤 Apellidos: `{c2_clean(datos.get('ANIApellido1'))} {c2_clean(datos.get('ANIApellido2')) or ''}`\n"
                f"📅 Nacimiento: `{datos.get('ANIFchNacimiento')}`\n"
                f"🏚 Dir: `{datos.get('ANIDireccion') or 'No registra'}`\n\n"
                f"💻 By {OWNER_USER}"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No encontrado.")
    finally:
        if conn: conn.close()

async def comando_c1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    res = consultar_salud_total(context.args[0])
    if res:
        await update.message.reply_text(f"🏥 *SALUD TOTAL*\n\n👤 Nombre: `{c2_clean(res.get('nombreCompleto'))}`\n✅ Estado: `{res.get('estadoAfiliacion')}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Sin datos.")

async def comando_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args: return
    key = context.args[0]
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT key_id, expiration_date FROM user_keys WHERE key_value = %s AND redeemed = FALSE", (key,))
        result = cursor.fetchone()
        if result:
            cursor.execute("UPDATE user_keys SET redeemed = TRUE, user_id = %s WHERE key_id = %s", (user_id, result["key_id"]))
            conn.commit()
            await update.message.reply_text("✅ Key activada.")
        else:
            await update.message.reply_text("❌ Key inválida.")
    finally:
        if conn: conn.close()

# ======== MAIN ========
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("c1", comando_c1))
    app.add_handler(CommandHandler("redeem", comando_redeem))
    # Agrega aquí el resto de handlers que necesites (c2, nequi, etc)
    print("Bot en línea.")
    app.run_polling()

if __name__ == "__main__":
    main()
