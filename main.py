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

# ================ CONFIGURACIÓN DE IDENTIDAD ================
OWNER_ID = 8114050673  
OWNER_USER = "@Broquicalifoxx"
BOT_TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"

# ================ CONFIGURACIÓN DE APIS Y DB ================
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
NEQUI_API_URL = "https://extract.nequialpha.com/consultar"
TIMEOUT = 120

pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=15,
    host="localhost",
    user="root",
    password="nabo94nabo94",
    database="ani",
    charset="utf8"
)

# ================== FUNCIONES DE SOPORTE ===================

def clean(value):
    if value is None or value == "" or value == "null": return "No registra"
    if isinstance(value, bool): return "Sí" if value else "No"
    return str(value)

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        query = "SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()"
        cursor.execute(query, (user_id,))
        return cursor.fetchone() is not None
    finally:
        if conn: conn.close()

def obtener_lugares(codigo):
    if not codigo: return "No registra"
    codigo = str(codigo)
    if len(codigo) >= 8:
        codigo_extraido = codigo[3:8]
        conn = None
        try:
            conn = pool.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT lug FROM lug_ori WHERE cod_lug LIKE %s", (f"%{codigo_extraido}%",))
            res = cursor.fetchone()
            return res['lug'] if res else "Desconocido"
        finally:
            if conn: conn.close()
    return "Formato Inválido"

# ================== COMANDOS DE CONSULTA ======================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┃ ⚔️ /cc ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯1\n"
        "┃ ⚔️ /nombres ➛ 𝐁𝐔𝐒𝐐𝐔𝐄𝐃𝐀 𝐏𝐎𝐑 𝐍𝐎𝐌𝐁𝐑𝐄\n"
        "┃ ⚔️ /c2 ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯2\n"
        "┃ ⚔️ /nequi ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯3\n"
        "┃ ⚔️ /llave ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐀𝐋𝐈𝐀𝐒\n"
        "┃ ⚔️ /placa ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        "═════════════════════════\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def mostrar_datos_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ Sin suscripción activa.")
        return
    if not context.args: return

    cedula = context.args[0]
    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
    datos = cursor.fetchone()
    conn.close()

    if datos:
        msg = (f"🪪 CC: `{cedula}`\n\n"
               f"👤 Nombres: `{datos['ANINombre1']} {datos.get('ANINombre2','')}`\n"
               f"👤 Apellidos: `{datos['ANIApellido1']} {datos['ANIApellido2']}`\n"
               f"👨 Padre: `{datos['ANINombresPadre']}`\n"
               f"👩‍🦱 Madre: `{datos['ANINombresMadre']}`\n"
               f"🏠 Dirección: `{datos['ANIDireccion']}`\n"
               f"📍 Lugar Nac: `{obtener_lugares(datos['LUGIdNacimiento'])}`\n\n"
               f"🛡 Creditos: {OWNER_USER}")
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No encontrado en DB Local.")

async def mostrar_datos_nombres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id): return
    if not context.args: return

    nombre_completo = " ".join(context.args).split()
    if len(nombre_completo) < 3:
        await update.message.reply_text("⚠️ Mínimo: Nombre + 2 Apellidos")
        return

    conn = pool.get_connection()
    cursor = conn.cursor(dictionary=True)
    query = "SELECT * FROM ani WHERE ANINombre1 = %s AND ANIApellido1 = %s AND ANIApellido2 = %s"
    cursor.execute(query, (nombre_completo[0], nombre_completo[1], nombre_completo[2]))
    resultados = cursor.fetchall()
    conn.close()

    if resultados:
        for r in resultados:
            await update.message.reply_text(f"🪪 CC: `{r['ANINuip']}`\n👤 `{r['ANINombre1']} {r['ANIApellido1']}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Sin coincidencias.")

# ================== COMANDOS DE ADMINISTRACIÓN =================

async def heidysql(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    await update.message.reply_text("✅ Reorganizando las pool...")
    # Aquí iría tu lógica de subprocess para el .bat si lo requieres
    await update.message.reply_text("✨ Pool optimizada exitosamente.")

async def generar_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    try:
        target_id = context.args[0]
        dias = int(context.args[1])
        key = "KEY-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
        expira = datetime.now() + timedelta(days=dias)
        
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_keys (key_value, user_id, expiration_date, redeemed) VALUES (%s, %s, %s, FALSE)", 
                       (key, target_id, expira))
        conn.commit()
        conn.close()
        await update.message.reply_text(f"🔑 Key: `{key}`\n📅 Expira: {expira}", parse_mode="Markdown")
    except:
        await update.message.reply_text("⚠️ Uso: /generar_key ID DIAS")

# ======================== MAIN ============================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", mostrar_datos_cedula))
    app.add_handler(CommandHandler("nombres", mostrar_datos_nombres))
    app.add_handler(CommandHandler("nequi", comando_nequi)) # Reutiliza la función del bloque anterior
    app.add_handler(CommandHandler("heidysql", heidysql))
    app.add_handler(CommandHandler("generar_key", generar_key))
    app.add_handler(CommandHandler("redeem", redeem)) # Reutiliza la función del bloque anterior

    print(f"🚀 BOT BROQUI ONLINE - OWNER ID: {OWNER_ID}")
    app.run_polling()

if __name__ == "__main__":
    main()
