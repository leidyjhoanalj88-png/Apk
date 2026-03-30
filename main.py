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

# Configuración de Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== VARIABLES DE ENTORNO ========
# Render las tomará de la pestaña 'Environment'
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# ======== POOL RESISTENTE (ANTI-CAÍDAS) ========
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="pool_db",
        pool_size=5,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=int(DB_PORT),
        charset="utf8",
        connect_timeout=10 # Tiempo límite para no trabar el bot
    )
    logger.info("✅ Pool de base de datos iniciado correctamente.")
except Exception as e:
    logger.error(f"⚠️ Error de conexión a DB: {e}. El bot funcionará solo con APIs externas.")
    pool = None

# ======== CONFIG APIs ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
API_DOX_EXTRANJERO = "https://par-bottles-straight-bernard.trycloudflare.com/hexn-dox-api"
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"

# --- FUNCIONES DE AYUDA ---
def clean(value):
    return str(value) if value and value != "null" else "No registra"

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    if not pool: return False # Si no hay DB, nadie tiene key (excepto Owner)
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        res = cursor.fetchone()
        connection.close()
        return res is not None
    except: return False

# --- CONSULTAS API ---
def consultar_extranjero(cedula):
    try:
        r = requests.get(API_DOX_EXTRANJERO, params={"cc": str(cedula)}, timeout=15)
        return r.json()
    except: return None

# [AQUÍ IRÍAN LAS DEMÁS FUNCIONES: consultar_cedula_c2, consultar_placa, etc.]
# (Mantén las que tenías en el código anterior, están perfectas)

# ======== COMANDO EXTRANJERO NUEVO ========
async def comando_extranjero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /ext <documento>")
        return
    
    cedula = context.args[0]
    msg = await update.message.reply_text(f"🔎 Consultando base extranjera para: `{cedula}`...", parse_mode="Markdown")
    
    datos = consultar_extranjero(cedula)
    if not datos or datos.get("Estado") != "OK":
        await msg.edit_text("❌ No se encontró información.")
        return

    id_info = datos.get('IDENTIDAD', {})
    salud = datos.get('SALUD', {})
    ubi = datos.get('UBICACIÓN', {})

    respuesta = (
        f"🇻🇪 **DATOS EXTRANJERO / MIGRACIÓN**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Nombre:** `{id_info.get('Primer Nombre')} {id_info.get('Primer Apellido')}`\n"
        f"🆔 **Doc:** `{datos.get('Documento')}`\n"
        f"📍 **Origen:** `{ubi.get('Pais Nacimiento')}`\n"
        f"🏥 **EPS:** `{salud.get('Regimen Afiliacion')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💻 {OWNER_USER}"
    )
    await msg.edit_text(respuesta, parse_mode="Markdown")

# ======== MAIN ========
def main():
    application = Application.builder().token(TOKEN).build()

    # Comandos básicos
    application.add_handler(CommandHandler("ext", comando_extranjero))
    # ... Agrega aquí todos los demás handlers que ya tenías ...

    logger.info("🚀 Bot iniciado en Render.")
    application.run_polling()

if __name__ == "__main__":
    main()
