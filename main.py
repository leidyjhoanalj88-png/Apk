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

# Configuración del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN DE BASE DE DATOS (ADAPTADO A RAILWAY) ========
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="pool_db",
        pool_size=15,
        host=os.getenv('MYSQLHOST', 'localhost'),
        user=os.getenv('MYSQLUSER', 'root'),
        password=os.getenv('MYSQLPASSWORD', 'nabo94nabo94'),
        database=os.getenv('MYSQLDATABASE', 'ani'),
        port=int(os.getenv('MYSQLPORT', 3306)),
        charset="utf8"
    )
except Exception as e:
    logger.error(f"Error de conexión DB: {e}")

# ======== CONFIG APIs ORIGINALES ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
OWNER_USER = "@Broquicalifoxx"
OWNER_ID = 8114050673
TIMEOUT = 120

# ======== FUNCIONES DE CONSULTA (EL MOTOR DEL BOT) ========

def consultar_nequi(telefono):
    try:
        url = "https://extract.nequialpha.com/consultar"
        headers = {"X-Api-Key": "M43289032FH23B", "Content-Type": "application/json"}
        r = requests.post(url, json={"telefono": str(telefono)}, headers=headers, timeout=TIMEOUT)
        return r.json()
    except: return None

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin suscripción.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /nequi <telefono>")
        return
    
    res = consultar_nequi(context.args[0])
    if res:
        msg = (f"🔎 **RESULTADO NEQUI**\n\n"
               f"📱 Teléfono: {res.get('telefono')}\n"
               f"🆔 Cédula: {res.get('cedula')}\n"
               f"👤 Nombre: {res.get('nombre_completo')}\n"
               f"📍 Municipio: {res.get('municipio')}\n"
               f"🛡 By {OWNER_USER}")
        await update.message.reply_text(msg)
    else:
        await update.message.reply_text("❌ Error en API.")

# Función para verificar suscripción
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

# ======== COMANDOS DEL MENÚ ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄  𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐯2 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚙️ Bot: @doxeos09bot\n"
        "┃ ⚔️ /start ➛ MENU\n"
        "┃ ⚔️ /cc ➛ CONSULTA V1\n"
        "┃ ⚔️ /c2 ➛ CONSULTA V2\n"
        "┃ ⚔️ /nequi ➛ CONSULTA NEQUI\n"
        "┃ ⚔️ /llave ➛ CONSULTA ALIAS\n"
        "┃ ⚔️ /placa ➛ CONSULTA PLACA\n"
        "┃ ⚔️ /redeem ➛ ACTIVAR KEY\n"
        "┃ ⚔️ /info ➛ SUSCRIPCIÓN\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    key = context.args[0]
    user_id = update.message.from_user.id
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user_keys SET redeemed = TRUE, user_id = %s WHERE key_value = %s AND redeemed = FALSE", (user_id, key))
        conn.commit()
        if cursor.rowcount > 0:
            await update.message.reply_text("✅ Key activada.")
        else:
            await update.message.reply_text("❌ Key inválida.")
    finally:
        if conn: conn.close()

# ======== EJECUCIÓN PRINCIPAL ========

def main():
    # TOKEN QUE ME PASASTE (8717607121...)
    TOKEN = "8717607121:AAEjR8NdGjOCASuqYlfV5bLlCYNG4nBApDg"
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("redeem", redeem))
    # Para que /cc y /c2 funcionen, debes pegar aquí las funciones de búsqueda del código viejo
    
    print("🚀 Bot Activo con el código original ajustado.")
    app.run_polling()

if __name__ == "__main__":
    main()
