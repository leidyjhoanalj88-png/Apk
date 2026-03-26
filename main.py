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

# ======== CONFIGURACIÓN DE IDENTIDAD ========
OWNER_USER = "@Broquicalifoxx"
OWNER_ID = 8114050673
BOT_USER = "@doxeos09bot"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"

# ======== CONFIGURACIÓN DE APIs ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
TIMEOUT = 120

# Configuración del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== POOL DE CONEXIONES (TU LOCALHOST) ========
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=15,
    host="localhost",
    user="root",
    password="nabo94nabo94",
    database="ani",
    charset="utf8"
)

# ======== UTILIDADES ========
def clean(value):
    if value is None or value == "" or str(value).lower() == "null":
        return "No registra"
    return str(value).upper()

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    connection = None
    cursor = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()"
        cursor.execute(query, (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

# ======== COMANDO /START (MENÚ ORIGINAL) ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄  𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐯2 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬, 𝐬𝐨𝐥𝐨 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚙️ 𝐂𝐎𝐌𝐀𝐍𝐃𝐎𝐒 𝐃𝐈𝐒𝐏𝐎𝐍𝐈𝐁𝐋𝐄𝐒\n"
        f"┃ ⚙️ Bot: {BOT_USER}\n"
        "┃ ⚔️ /start ➛ MENU PRINCIPAL\n"
        "┃ ⚔️ /cc ➛ CONSULTA CEDULA v1\n"
        "┃ ⚔️ /c2 ➛ CONSULTA CEDULA v2\n"
        "┃ ⚔️ /nequi ➛ CONSULTA NEQUI\n"
        "┃ ⚔️ /llave ➛ CONSULTA ALIAS\n"
        "┃ ⚔️ /placa ➛ CONSULTA PLACA\n"
        "┃ ⚔️ /nombres ➛ BUSCAR POR NOMBRE\n"
        "┃ ⚔️ /redeem ➛ ACTIVAR KEY\n"
        "┃ ⚔️ /info ➛ MI SUSCRIPCIÓN\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "⚠️ Cada Orden Ejecutada deja cicatrices... Usalo con responsabilidad.\n"
        "═════════════════════════\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

# ======== COMANDO /C2 (VERSIÓN FULL) ========
async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ Sin suscripción activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /c2 <documento>")
        return

    doc = context.args[0]
    sent = await update.message.reply_text("🔎 Consultando fondo...")
    try:
        r = requests.post(API_URL_C2, json={"cedula": doc}, timeout=TIMEOUT).json()
        if r.get("success"):
            d = r["data"]
            res = (
                "乄  𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐯2 ⚔️\n"
                "═════════════════════════\n"
                "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
                f"┃ 🆔 Documento: {clean(d.get('cedula'))}\n"
                f"┃ 👤 Nombre: {clean(d.get('primer_nombre'))} {clean(d.get('primer_apellido'))}\n"
                f"┃ 📍 Ciudad: {clean(d.get('municipio_residencia'))}\n"
                f"┃ 🏠 Direccion: {clean(d.get('direccion'))}\n"
                f"┃ 🏥 EPS: {clean(d.get('eps'))}\n"
                f"┃ 📱 Celular: {clean(d.get('celular'))}\n"
                "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
                f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
            )
            await sent.edit_text(res)
        else: await sent.edit_text("❌ No encontrado.")
    except: await sent.edit_text("❌ Error API.")

# ======== COMANDO /CC (TU DB LOCAL) ========
async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id) or not context.args: return
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (context.args[0],))
        d = cursor.fetchone()
        conn.close()
        if d:
            msg = f"🪪 **CC:** `{d['ANINuip']}`\n👤 **Nombres:** `{d['ANINombre1']} {d['ANIApellido1']}`\n🏚 **Dirección:** `{d['ANIDireccion']}`"
            await update.message.reply_text(msg, parse_mode="Markdown")
    except: pass

# ======== COMANDO /NEQUI ========
async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id) or not context.args: return
    try:
        r = requests.post("https://extract.nequialpha.com/consultar", 
                          json={"telefono": context.args[0]}, 
                          headers={"X-Api-Key": "M43289032FH23B"}).json()
        await update.message.reply_text(f"📱 **NEQUI**\n👤 `{r.get('nombre_completo')}`\n🆔 `{r.get('cedula')}`", parse_mode="Markdown")
    except: pass

# ======== SISTEMA DE KEYS (REDEEM & INFO) ========
async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    user_id = update.message.from_user.id
    key = context.args[0]
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user_keys SET redeemed = TRUE, user_id = %s WHERE key_value = %s AND redeemed = FALSE", (user_id, key))
        conn.commit()
        if cursor.rowcount > 0: await update.message.reply_text("✅ Key activada.")
        else: await update.message.reply_text("❌ Key inválida.")
        conn.close()
    except: pass

async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT expiration_date FROM user_keys WHERE user_id = %s ORDER BY expiration_date DESC", (user_id,))
        res = cursor.fetchone()
        conn.close()
        msg = f"⏳ **Tu suscripción expira:** `{res['expiration_date']}`" if res else "❌ Sin suscripción."
        await update.message.reply_text(msg, parse_mode="Markdown")
    except: pass

# ======== MAIN ========
def main():
    app = Application.builder().token("8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU").build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("c2", comando_c2))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("info", info))
    
    print(f"Bot {BOT_USER} iniciado por {OWNER_USER}")
    app.run_polling()

if __name__ == "__main__":
    main()
