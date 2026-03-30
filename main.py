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

# Cargar variables de entorno
load_dotenv()

# Logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== VARIABLES DEL .ENV ========
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "8114050673"))
OWNER_USER = os.getenv("OWNER_USER", "@Broquicalifoxx")

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "3306")

API_URL_C2 = os.getenv("API_URL_C2", "https://extract.nequialpha.com/doxing")
START_IMAGE_URL = os.getenv("START_IMAGE_URL")

# APIs Externas
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
API_DOX_EXTRANJERO = "https://par-bottles-straight-bernard.trycloudflare.com/hexn-dox-api"

# ======== POOL DE BASE DE DATOS (REFORZADO) ========
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="pool_db",
        pool_size=10,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=int(DB_PORT),
        charset="utf8",
        connect_timeout=10
    )
    logger.info("✅ Pool de DB iniciado.")
except Exception as e:
    logger.error(f"⚠️ Error DB: {e}")
    pool = None

# ======== UTILS & SEGURIDAD ========

def clean(value):
    return str(value) if value and value != "null" else "No registra"

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    if not pool: return False
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        res = cursor.fetchone()
        connection.close()
        return res is not None
    except: return False

# ======== FUNCIONES DE CONSULTA (APIs) ========

def consultar_extranjero(cedula):
    try:
        r = requests.get(API_DOX_EXTRANJERO, params={"cc": str(cedula)}, timeout=20)
        return r.json()
    except: return None

def consultar_nequi(telefono):
    try:
        headers = {"X-Api-Key": "Z5k4Y1n4n0vS", "Content-Type": "application/json"}
        r = requests.post("https://extract.nequialpha.com/consultar", json={"telefono": str(telefono)}, headers=headers, timeout=20)
        return r.json()
    except: return None

def consultar_placa(placa):
    try:
        r = requests.get(PLACA_API_URL, params={"placa": placa.upper()}, timeout=20)
        return r.json()
    except: return None

def consultar_llave(alias):
    try:
        r = requests.get(LLAVE_API_BASE, params={"hexn": alias}, timeout=20)
        return r.json()
    except: return None

# ======== COMANDOS DEL BOT ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝐌𝐄𝐍𝐔 ⚔️\n"
        "═════════════════════════\n"
        "┃ ⚔️ /cc ➛ CÉDULA V1\n"
        "┃ ⚔️ /c2 ➛ CÉDULA V2\n"
        "┃ ⚔️ /ext ➛ EXTRANJERO\n"
        "┃ ⚔️ /nequi ➛ NEQUI\n"
        "┃ ⚔️ /llave ➛ ALIAS\n"
        "┃ ⚔️ /placa ➛ PLACA\n"
        "┃ ⚔️ /sisben ➛ SISBEN IV\n"
        "┃ ⚔️ /info ➛ SUSCRIPCIÓN\n"
        "═════════════════════════\n"
        f"👑 Owner: {OWNER_USER}"
    )
    if START_IMAGE_URL:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    else:
        await update.message.reply_text(texto)

async def comando_extranjero(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /ext <documento>")
        return
    
    cedula = context.args[0]
    msg = await update.message.reply_text("🔎 Consultando base migratoria...")
    datos = consultar_extranjero(cedula)
    
    if not datos or datos.get("Estado") != "OK":
        await msg.edit_text("❌ No se encontró información en esta base.")
        return

    id_i = datos.get('IDENTIDAD', {})
    res = (
        f"🇻🇪 **DATOS EXTRANJERO**\n"
        f"👤 **Nombre:** `{id_i.get('Primer Nombre')} {id_i.get('Primer Apellido')}`\n"
        f"🆔 **Doc:** `{datos.get('Documento')}`\n"
        f"🎂 **Nace:** `{id_i.get('Fecha Nacimiento')}`\n"
        f"📍 **Origen:** `{datos.get('UBICACIÓN', {}).get('Pais Nacimiento')}`\n"
        f"━━━━━━━━━━━━━━\n"
        f"💻 {OWNER_USER}"
    )
    await msg.edit_text(res, parse_mode="Markdown")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args:
        await update.message.reply_text("📌 Uso: /nequi <celular>")
        return
    res = consultar_nequi(context.args[0])
    if res:
        msg = f"📱 **NEQUI DATA**\n\n👤 `{res.get('nombre_completo')}`\n🆔 `{res.get('cedula')}`\n📍 `{res.get('municipio')}`"
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Sin respuesta.")

async def comando_placa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    res = consultar_placa(context.args[0])
    await update.message.reply_text(f"```json\n{json.dumps(res, indent=2, ensure_ascii=False)[:4000]}\n```", parse_mode="Markdown")

async def comando_llave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    res = consultar_llave(context.args[0])
    await update.message.reply_text(f"```json\n{json.dumps(res, indent=2, ensure_ascii=False)}\n```", parse_mode="Markdown")

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    try:
        r = requests.post(API_URL_C2, json={"cedula": context.args[0]}, timeout=20).json()
        if r.get("success"):
            d = r.get("data", {})
            msg = f"📄 **DATOS C2**\n👤 {d.get('primer_nombre')} {d.get('primer_apellido')}\n📍 {d.get('municipio_residencia')}"
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("❌ No encontrado.")
    except: await update.message.reply_text("❌ Error API.")

# ======== MAIN ========

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ext", comando_extranjero))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("placa", comando_placa))
    application.add_handler(CommandHandler("llave", comando_llave))
    application.add_handler(CommandHandler("c2", comando_c2))

    print("🚀 Bot Full activo en Render.")
    application.run_polling()

if __name__ == "__main__":
    main()
