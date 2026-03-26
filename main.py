import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mysql.connector import pooling
import logging
import os
import requests
import json
import random
import string
from datetime import datetime, timedelta

# Configuración de logs
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN RAILWAY ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN")

OWNER_USER = os.getenv("OWNER_USER", "@Broquicalifoxx")
OWNER_ID = 8114050673
BOT_USER = "@doxeos09bot"

# ======== POOL DE CONEXIONES ========
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="pool_db",
        pool_size=25,
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        port=int(DB_PORT),
        charset="utf8"
    )
except Exception as e:
    logger.error(f"Error Crítico DB: {e}")
    pool = None

# ======== UTILIDADES ========
def clean(val):
    return str(val).upper() if val and str(val).lower() != "null" else "No registra"

def tiene_key(user_id):
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

# ======== COMANDOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "⚔️ **BROQUI MENU** ⚔️\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "**Bienvenido al infierno digital... aca no hay reglas, solo comandos** ⚔️\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        "───────────────⩺\n"
        f"┃ ⚙️ **Bot:** {BOT_USER}\n"
        "┃ ⚔️ `/start` ➛ **MENU PRINCIPAL**\n"
        "┃ ⚔️ `/cc` ➛ **CONSULTA CEDULA v1**\n"
        "┃ ⚔️ `/c2` ➛ **CONSULTA CEDULA v2**\n"
        "┃ ⚔️ `/nequi` ➛ **CONSULTA NEQUI**\n"
        "┃ ⚔️ `/llave` ➛ **CONSULTA ALIAS**\n"
        "┃ ⚔️ `/placa` ➛ **CONSULTA PLACA**\n"
        "┃ ⚔️ `/nombres` ➛ **BUSCAR POR NOMBRE**\n"
        "┃ ⚔️ `/redeem` ➛ **ACTIVAR KEY**\n"
        "┃ ⚔️ `/info` ➛ **MI SUSCRIPCIÓN**\n"
        "┃ ⚔️ `/help` ➛ **AYUDA**\n"
        "───────────────⩺\n"
        "⚠️ **Cada Orden Ejecutada deja cicatrices... Usalo con responsabilidad o seras deborado.**\n"
        "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
        f"👑 **Desarrollado por:** {OWNER_USER}"
    )
    foto = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
    try:
        await update.message.reply_photo(photo=foto, caption=texto, parse_mode="Markdown")
    except:
        await update.message.reply_text(texto, parse_mode="Markdown")

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key(update.message.from_user.id): return
    if not context.args: return
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (context.args[0],))
        d = cursor.fetchone()
        conn.close()
        if d:
            res = f"🪪 **CC:** `{d['ANINuip']}`\n👤 **Nombre:** `{d['ANINombre1']} {d['ANIApellido1']}`\n📅 **Nace:** `{d['ANIFchNacimiento']}`"
            await update.message.reply_text(res, parse_mode="Markdown")
    except: pass

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key(update.message.from_user.id): return
    if not context.args: return
    try:
        r = requests.post("https://extract.nequialpha.com/consultar", 
                          json={"telefono": context.args[0]}, 
                          headers={"X-Api-Key": "M43289032FH23B"}).json()
        await update.message.reply_text(f"📱 **NEQUI**\n👤 `{r.get('nombre_completo')}`\n🆔 `{r.get('cedula')}`", parse_mode="Markdown")
    except: pass

async def comando_nombres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key(update.message.from_user.id): return
    if len(context.args) < 2: return
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT ANINuip, ANINombre1, ANIApellido1 FROM ani WHERE ANINombre1 LIKE %s AND ANIApellido1 LIKE %s LIMIT 5", 
                       (f"%{context.args[0]}%", f"%{context.args[1]}%"))
        rows = cursor.fetchall()
        conn.close()
        for r in rows:
            await update.message.reply_text(f"🆔 `{r['ANINuip']}` - {r['ANINombre1']} {r['ANIApellido1']}", parse_mode="Markdown")
    except: pass

async def comando_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT expiration_date FROM user_keys WHERE user_id = %s", (user_id,))
        res = cursor.fetchone()
        conn.close()
        msg = f"⏳ Expira: `{res['expiration_date']}`" if res else "❌ Sin suscripción."
        await update.message.reply_text(msg, parse_mode="Markdown")
    except: pass

async def comando_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🆘 **Soporte:** Contacta a @Broquicalifoxx para ayuda técnica o comprar keys.", parse_mode="Markdown")

# [ El comando /c2 ya lo tienes en el mensaje anterior, agrégalo aquí ]

# ======== MAIN ========
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("nombres", comando_nombres))
    app.add_handler(CommandHandler("info", comando_info))
    app.add_handler(CommandHandler("help", comando_help))
    # Agrega el comando_c2, comando_placa y comando_llave aquí...

    app.run_polling()

if __name__ == "__main__":
    main()
