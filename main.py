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

# Cargar variables de entorno
load_dotenv()

# Configuración del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Pool de conexiones a MySQL usando .env
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db", pool_size=10,
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME", "ani"),
    charset="utf8"
)

# Configuración de APIs
API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
PLACA_API_URL = os.getenv("PLACA_API_URL", "https://alex-bookmark-univ-survival.trycloudflare.com/index.php")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")
START_IMAGE_URL = os.getenv("START_IMAGE_URL")
TIMEOUT = 120

# --- FUNCIONES DE SEGURIDAD Y LIMPIEZA ---
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

# --- COMANDOS DE BÚSQUEDA ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner = os.getenv("OWNER_USERNAME", "@Broquicalifoxx")
    texto = (
        "乄 𝐂𝐀𝐋𝐈𝐅𝐎𝐗𝐗 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚔️ /cc [cedula] ➛ CONSULTA DB\n"
        "┃ ⚔️ /c2 [cedula] ➛ CONSULTA API\n"
        "┃ ⚔️ /nequi [celular] ➛ NEQUI\n"
        "┃ ⚔️ /placa [placa] ➛ RUNT\n"
        "┃ ⚔️ /redeem [key] ➛ ACTIVAR\n"
        "┃ ⚔️ /info ➛ MI ESTADO\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {owner}"
    )
    if START_IMAGE_URL:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    else:
        await update.message.reply_text(texto)

async def consulta_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        return await update.message.reply_text("❌ No tienes suscripción activa.")
    if not context.args: return
    
    cedula = context.args[0]
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
    d = cursor.fetchone()
    conn.close()

    if d:
        msg = f"👤 {d['ANINombre1']} {clean(d['ANINombre2'])}\n🆔 CC: {cedula}\n🏠 Dir: {clean(d['ANIDireccion'])}"
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("No encontrado en base de datos.")

async def consulta_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    
    tel = context.args[0]
    try:
        r = requests.post("https://extract.nequialpha.com/consultar", 
                         json={"telefono": tel}, headers={"X-Api-Key": NEQUI_API_KEY}, timeout=TIMEOUT)
        data = r.json()
        await update.message.reply_text(f"🔎 NEQUI:\n🆔 CC: {data.get('cedula')}\n👤 Nombre: {data.get('nombre_completo')}")
    except: await update.message.reply_text("Error en API Nequi.")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    key = context.args[0]
    user_id = update.message.from_user.id
    conn = pool.get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_keys SET redeemed=TRUE, user_id=%s WHERE key_value=%s AND redeemed=FALSE", (user_id, key))
    conn.commit()
    if cursor.rowcount > 0:
        await update.message.reply_text("✅ Key activada con éxito.")
    else:
        await update.message.reply_text("❌ Key inválida o ya usada.")
    conn.close()

# --- MAIN ---
def main():
    token = os.getenv("TELEGRAM_TOKEN")
    if not token: return print("Falta TOKEN en .env")

    app = Application.builder().token(token).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", consulta_cc))
    app.add_handler(CommandHandler("nequi", consulta_nequi))
    app.add_handler(CommandHandler("redeem", redeem))

    print("--- BOT CALIFOXX ONLINE ---")
    app.run_polling()

if __name__ == "__main__":
    main()
