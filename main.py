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

# ======== CONFIGURACIÓN LOGGING ========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN RAILWAY (TOKEN ACTUALIZADO) ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
# TOKEN NUEVO INTEGRADO AQUÍ:
TOKEN = "8717607121:AAEjR8NdGjOCASuqYlfV5bLlCYNG4nBApDg" 

OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# ======== POOL DE CONEXIONES ========
try:
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
except Exception as e:
    logger.error(f"❌ Error Pool: {e}")

# ======== CONFIG APIs ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
TIMEOUT = 120

# ======== FUNCIONES LÓGICAS (TODO EL MOTOR) ========

def clean(value):
    if value is None or value == "" or value == "null": return "No registra"
    return "Sí" if isinstance(value, bool) and value else "No" if isinstance(value, bool) else str(value)

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

def obtener_lugar(codigo):
    if not codigo or len(str(codigo)) < 8: return None
    try:
        cod = str(codigo)[3:8]
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT lug FROM lug_ori WHERE cod_lug LIKE %s", (f"%{cod}%",))
        res = cursor.fetchone()
        return res['lug'] if res else None
    except: return None
    finally:
        if conn: conn.close()

# --- Aquí van las funciones de consulta API (C2, Nequi, Placa, Llave) ---
# Se mantienen igual a tu código original por su alta efectividad.

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin suscripción activa.")
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
            ln = obtener_lugar(datos.get('LUGIdNacimiento'))
            le = obtener_lugar(datos.get('LUGIdExpedicion'))
            msg = (f"🪪 **CC:** `{cedula}`\n\n"
                   f"👤 **Nombres:** `{datos['ANINombre1']} {datos['ANINombre2'] or ''}`\n"
                   f"👤 **Apellidos:** `{datos['ANIApellido1']} {datos['ANIApellido2']}`\n"
                   f"👨 **Padre:** `{datos['ANINombresPadre']}`\n"
                   f"📅 **Nacimiento:** `{datos['ANIFchNacimiento']}`\n"
                   f"📍 **Lugar Nac:** `{ln or 'No registra'}`\n"
                   f"📱 **Teléfono:** `{datos['ANITelefono']}`\n\n"
                   f"🛡 **By {OWNER_USER}**")
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No encontrado en DB.")
    finally:
        if conn: conn.close()

# ======== SISTEMA SISBEN IV (SCRAPER) ========
def consultar_sisben(tipo, numero):
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "text/html"})
    try:
        r = session.get("https://reportes.sisben.gov.co/dnp_sisbenconsulta", timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "__RequestVerificationToken"}).get("value")
        data = {"TipoID": tipo, "documento": numero, "__RequestVerificationToken": token}
        r = session.post("https://reportes.sisben.gov.co/dnp_sisbenconsulta", data=data, timeout=15)
        # Aquí iría la lógica de _extraer_sisben que ya tienes en tu código
        return r.text # Simplificado para el ejemplo, usa tu lógica de extracción
    except: return None

# ======== COMANDOS DE ADMIN Y START ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚔️ /cc ➛ CONSULTA V1\n"
        "┃ ⚔️ /c2 ➛ CONSULTA V2\n"
        "┃ ⚔️ /nequi ➛ CONSULTA NEQUI\n"
        "┃ ⚔️ /placa ➛ CONSULTA PLACA\n"
        "┃ ⚔️ /nombres ➛ BUSCAR NOMBRE\n"
        "┃ ⚔️ /redeem ➛ ACTIVAR KEY\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

# ======== EJECUCIÓN ========
def main():
    app = Application.builder().token(TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("redeem", comando_redeem)) # Asegúrate de tener esta función definida
    # ... añadir el resto de handlers según tu código ...

    print("🚀 BOT BROQUICALI ONLINE - MODO FULL")
    app.run_polling()

if __name__ == "__main__":
    main()
