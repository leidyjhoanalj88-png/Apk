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
import time
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Cargar variables desde el archivo .env
load_dotenv()

# Configuración de Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== VARIABLES DESDE EL .ENV ========
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "8114050673"))
OWNER_USER = os.getenv("OWNER_USER", "@Broquicalifoxx")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD") # Coincide con tu .env
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "3306")

API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
START_IMAGE_URL = os.getenv("START_IMAGE_URL")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY")

# APIs FIJAS (TryCloudflare)
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
API_DOX_EXTRANJERO = "https://par-bottles-straight-bernard.trycloudflare.com/hexn-dox-api"

# ======== POOL DE BASE DE DATOS ========
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
        connect_timeout=10
    )
    logger.info("✅ Conexión al Pool exitosa.")
except Exception as e:
    logger.error(f"⚠️ No se pudo conectar a la DB: {e}. El bot funcionará solo con APIs externas.")
    pool = None

# ======== UTILS & SEGURIDAD ========

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    if not pool: return False
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        res = cursor.fetchone()
        return res is not None
    except: return False
    finally:
        if connection and connection.is_connected(): connection.close()

def clean(value):
    return str(value) if value and value != "null" else "No registra"

# ======== FUNCIONES DE CONSULTA ========

def consultar_extranjero(cedula):
    try:
        r = requests.get(API_DOX_EXTRANJERO, params={"cc": str(cedula)}, timeout=15)
        r.raise_for_status()
        return r.json()
    except: return None

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(API_URL_C2, json={"cedula": str(cedula)}, timeout=15)
        return r.json()
    except: return None

# ======== COMANDOS DEL BOT ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "⚔️ **MENU PRINCIPAL** ⚔️\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "• /cc - Consulta Cédula v1\n"
        "• /c2 - Consulta Cédula v2\n"
        "• /ext - Consulta Extranjero\n"
        "• /placa - Consulta Vehicular\n"
        "• /info - Mi Suscripción\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 Owner: {OWNER_USER}"
    )
    if START_IMAGE_URL:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto, parse_mode="Markdown")
    else:
        await update.message.reply_text(texto, parse_mode="Markdown")

async def comando_extranjero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /ext <documento>")
        return
    
    cedula = context.args[0]
    msg = await update.message.reply_text(f"🔎 Consultando base extranjera...")
    
    datos = consultar_extranjero(cedula)
    if not datos or datos.get("Estado") != "OK":
        await msg.edit_text("❌ No se encontró información.")
        return

    id_info = datos.get('IDENTIDAD', {})
    respuesta = (
        f"🇻🇪 **DATOS EXTRANJERO**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 **Nombre:** `{id_info.get('Primer Nombre')} {id_info.get('Primer Apellido')}`\n"
        f"🆔 **Documento:** `{datos.get('Documento')}`\n"
        f"🎂 **Nacimiento:** `{id_info.get('Fecha Nacimiento')}`\n"
        f"⚧ **Sexo:** `{id_info.get('Sexo')}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💻 Desarrollado por {OWNER_USER}"
    )
    await msg.edit_text(respuesta, parse_mode="Markdown")

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == OWNER_ID:
        await update.message.reply_text("👑 Eres el Administrador Principal (Acceso Ilimitado).")
        return
    # Aquí iría la lógica de consulta a la DB si el pool está activo
    await update.message.reply_text("ℹ️ Consulta tu estado con el administrador.")

# ======== MAIN ========

def main():
    if not TOKEN:
        print("❌ ERROR: No se encontró el TELEGRAM_TOKEN en el archivo .env")
        return

    application = Application.builder().token(TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ext", comando_extranjero))
    application.add_handler(CommandHandler("info", info))

    print("🚀 Bot iniciado correctamente...")
    application.run_polling()

if __name__ == "__main__":
    main()
