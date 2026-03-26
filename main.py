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
from datetime import datetime, timedelta

# ======== CONFIGURACIÓN INICIAL ========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# DATOS DEL DUEÑO Y BOT
OWNER_USER = "@Broquicalifoxx" 
OWNER_ID = 8114050673 
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"

# ======== CONFIGURACIÓN DE BASE DE DATOS (ADAPTADO A RAILWAY) ========
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

# ======== CONFIGURACIÓN DE APIS ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
NEQUI_API_URL = "https://extract.nequialpha.com/consultar"
TIMEOUT = 60

# ======== FUNCIONES DE APOYO Y LIMPIEZA ========
def clean(value):
    if value is None or value == "" or value == "null": return "No registra"
    return "Sí" if value is True else "No" if value is False else str(value)

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

# ======== LÓGICA DE CONSULTAS (APIS) ========

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes suscripción activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: `/nequi 300xxxx`", parse_mode="Markdown")
        return
    
    try:
        r = requests.post(NEQUI_API_URL, json={"telefono": context.args[0]}, headers={"X-Api-Key": "M43289032FH23B"}, timeout=TIMEOUT)
        res = r.json()
        msg = (f"🔎 **RESULTADO NEQUI**\n\n"
               f"📱 Teléfono: `{res.get('telefono')}`\n"
               f"🆔 Cédula: `{res.get('cedula')}`\n"
               f"👤 Nombre: `{res.get('nombre_completo')}`\n"
               f"📍 Municipio: `{res.get('municipio')}`\n"
               f"🛡 Creditos: {OWNER_USER}")
        await update.message.reply_text(msg, parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Error en API Nequi.")

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    try:
        res = requests.post(API_URL_C2, json={"cedula": context.args[0]}, timeout=TIMEOUT).json()
        if res.get("success"):
            d = res["data"]
            mensaje = f"📄 **RESULTADO V2**\n\n🆔 ID: `{d.get('cedula')}`\n👤 Nombre: `{d.get('primer_nombre')} {d.get('primer_apellido')}`\n🏥 EPS: `{d.get('eps')}`\n📍 Ubicación: `{d.get('municipio_residencia')}`"
            await update.message.reply_text(mensaje, parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Error en consulta C2.")

async def mostrar_datos_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Lógica de base de datos local (ANI)
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id): return
    if not context.args: return
    
    cedula = context.args[0]
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        datos = cursor.fetchone()
        if datos:
            msg = (f"🪪 **DATOS CEDULA (V1)**\n\n"
                   f"👤 Nombres: `{datos['ANINombre1']} {datos['ANINombre2']}`\n"
                   f"👤 Apellidos: `{datos['ANIApellido1']} {datos['ANIApellido2']}`\n"
                   f"🏠 Dirección: `{datos['ANIDireccion']}`\n"
                   f"📱 Teléfono: `{datos['ANITelefono']}`")
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No encontrado en DB Local.")
    finally:
        if conn: conn.close()

# ======== COMANDOS DE MENÚ ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄  𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐯2 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥...\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚔️ /cc ➛ CONSULTA V1\n"
        "┃ ⚔️ /c2 ➛ CONSULTA V2\n"
        "┃ ⚔️ /nequi ➛ CONSULTA NEQUI\n"
        "┃ ⚔️ /placa ➛ CONSULTA PLACA\n"
        "┃ ⚔️ /redeem ➛ ACTIVAR KEY\n"
        "┃ ⚔️ /info ➛ MI ESTADO\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚rer: {OWNER_USER}"
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
            await update.message.reply_text("✅ Key activada con éxito.")
        else:
            await update.message.reply_text("❌ Key inválida o ya usada.")
    finally:
        if conn: conn.close()

# ======== MAIN (EJECUCIÓN) ========
def main():
    # TOKEN ACTUALIZADO PARA RAILWAY
    TOKEN = "8717607121:AAEjR8NdGjOCASuqYlfV5bLlCYNG4nBApDg"
    
    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", mostrar_datos_cedula))
    app.add_handler(CommandHandler("c2", comando_c2))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("redeem", redeem))
    # Puedes agregar los demás del código viejo siguiendo este patrón...

    print("🚀 Bot Activo con Nuevo Token y APIs integradas.")
    app.run_polling()

if __name__ == "__main__":
    main()
