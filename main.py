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

# ================= CONFIGURACIÓN DE LOGGING =================
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ================ CONFIGURACIÓN DE IDENTIDAD (BROQUICALIFOXX) ================
OWNER_ID = 8114050673 
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"

# ================ CONFIGURACIÓN DE APIS =====================
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
NEQUI_API_URL = "https://extract.nequialpha.com/consultar"
TIMEOUT = 120

# ================ POOL DE CONEXIONES MYSQL =================
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=15,
    host="localhost", # O mysql.railway.internal si usas Railway
    user="root",
    password="nabo94nabo94",
    database="ani",
    charset="utf8"
)

# ================== NÚCLEO DE FUNCIONES ===================

def db_query(query, params=(), fetchone=False, commit=False):
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        if commit:
            conn.commit()
            return True
        return cursor.fetchone() if fetchone else cursor.fetchall()
    except Exception as e:
        logger.error(f"Error SQL: {e}")
        return None
    finally:
        if conn: conn.close()

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    query = "SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()"
    return db_query(query, (user_id,), fetchone=True) is not None

def clean(value):
    if value is None or value == "" or value == "null": return "No registra"
    return str(value)

# ================== COMANDOS DEL BOT ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚔️ /cc      ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯1\n"
        "┃ ⚔️ /c2      ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯2\n"
        "┃ ⚔️ /nequi   ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯3\n"
        "┃ ⚔️ /llave   ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐀𝐋𝐈𝐀𝐒\n"
        "┃ ⚔️ /placa   ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        "┃ ⚔️ /redeem  ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐊𝐄𝐘\n"
        "┃ ⚔️ /info    ➛ 𝐌𝐈 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text(f"❌ Sin suscripción activa. Contacta a {OWNER_USER}")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <cedula>")
        return

    cedula = context.args[0]
    res = db_query("SELECT * FROM ani WHERE ANINuip = %s LIMIT 1", (cedula,), fetchone=True)
    
    if res:
        msg = (f"🪪 **DATOS ENCONTRADOS**\n\n🆔 CC: `{res['ANINuip']}`\n"
               f"👤 Nombre: `{res['ANINombre1']} {res.get('ANINombre2','')}`\n"
               f"👤 Apellidos: `{res['ANIApellido1']} {res['ANIApellido2']}`\n"
               f"🏠 Dirección: `{res.get('ANIDireccion','No registra')}`\n"
               f"📱 Teléfono: `{res.get('ANITelefono','No registra')}`\n\n"
               f"🛡 Creditos: {OWNER_USER}")
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No se encontraron datos en la DB local.")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    
    tel = context.args[0]
    try:
        r = requests.post(NEQUI_API_URL, json={"telefono": tel}, headers={"X-Api-Key": "M43289032FH23B"}, timeout=TIMEOUT)
        d = r.json()
        msg = (f"🔎 **RESULTADO NEQUI**\n\n"
               f"📱 Teléfono: {d.get('telefono')}\n"
               f"🆔 Cédula: {d.get('cedula')}\n"
               f"👤 Nombre: {d.get('nombre_completo')}\n\n"
               f"🔖 by {OWNER_USER}")
        await update.message.reply_text(msg)
    except:
        await update.message.reply_text("❌ Error en API Nequi.")

# ================== COMANDOS ADMIN (KEYS) ===================

async def generar_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Uso: /generar_key <ID_User> <Dias>")
        return

    target_id = context.args[0]
    dias = int(context.args[1])
    key = "KEY-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    expira = datetime.now() + timedelta(days=dias)

    db_query("INSERT INTO user_keys (key_value, user_id, expiration_date, redeemed) VALUES (%s, %s, %s, FALSE)", 
             (key, target_id, expira), commit=True)
    
    await update.message.reply_text(f"🔑 **KEY GENERADA:** `{key}`\n📅 Expira en: {dias} días", parse_mode="Markdown")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    key = context.args[0]
    user_id = update.message.from_user.id

    check = db_query("SELECT key_id FROM user_keys WHERE key_value = %s AND redeemed = FALSE", (key,), fetchone=True)
    if check:
        db_query("UPDATE user_keys SET redeemed = TRUE, user_id = %s WHERE key_value = %s", (user_id, key), commit=True)
        await update.message.reply_text("✅ ¡Suscripción activada con éxito!")
    else:
        await update.message.reply_text("❌ Key inválida, usada o expirada.")

# ======================== MAIN ============================

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("generar_key", generar_key))
    app.add_handler(CommandHandler("redeem", redeem))
    # Para comandos como /c2, /placa y /llave, sigue la misma estructura de llamadas API

    print(f"🚀 Bot BROQUI activo con ID {OWNER_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()
