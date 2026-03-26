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

# ======== CONFIGURACIÓN DE IDENTIDAD ========
OWNER_USER = "@Broquicalifoxx" 
OWNER_ID = 8114050673 
BOT_USER = "@doxeos09bot"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"
TIMEOUT = 60

# ======== CONFIGURACIÓN DE LOGGING ========
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== CONEXIÓN A BASE DE DATOS (FIX PARA RAILWAY) ========
# Se usan os.getenv para que Railway inyecte las credenciales automáticamente
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="pool_db",
        pool_size=20,
        host=os.getenv('MYSQLHOST', 'localhost'),
        user=os.getenv('MYSQLUSER', 'root'),
        password=os.getenv('MYSQLPASSWORD', 'nabo94nabo94'),
        database=os.getenv('MYSQLDATABASE', 'ani'),
        port=int(os.getenv('MYSQLPORT', 3306)),
        charset="utf8",
        connection_timeout=30
    )
    logger.info("✅ Pool de conexiones configurado correctamente.")
except Exception as e:
    logger.error(f"❌ Error crítico en DB: {e}")

# ======== FUNCIONES DE APOYO ========
def clean(value):
    if value is None or value == "" or value == "null": return "No registra"
    return str(value)

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

# ======== COMANDOS DE CONSULTA (APIS INTEGRADAS) ========

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin suscripción activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: `/nequi 3001234567`", parse_mode="Markdown")
        return
    
    try:
        url = "https://extract.nequialpha.com/consultar"
        headers = {"X-Api-Key": "M43289032FH23B", "Content-Type": "application/json"}
        r = requests.post(url, json={"telefono": context.args[0]}, headers=headers, timeout=TIMEOUT)
        res = r.json()
        
        msg = (f"🔎 **RESULTADO NEQUI**\n\n"
               f"📱 Teléfono: `{res.get('telefono', 'N/A')}`\n"
               f"🆔 Cédula: `{res.get('cedula', 'N/A')}`\n"
               f"👤 Nombre: `{res.get('nombre_completo', 'N/A')}`\n"
               f"📍 Municipio: `{res.get('municipio', 'N/A')}`\n\n"
               f"🛡 By {OWNER_USER}")
        await update.message.reply_text(msg, parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Error en la API de Nequi.")

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    
    try:
        url = "https://extract.nequialpha.com/doxing"
        r = requests.post(url, json={"cedula": context.args[0]}, timeout=TIMEOUT)
        res = r.json()
        if res.get("success"):
            d = res["data"]
            mensaje = (f"📄 **RESULTADO V2**\n\n"
                       f"🆔 ID: `{d.get('cedula')}`\n"
                       f"👤 Nombre: `{d.get('primer_nombre')} {d.get('primer_apellido')}`\n"
                       f"🏥 EPS: `{d.get('eps')}`\n"
                       f"📍 Residencia: `{d.get('municipio_residencia')}`\n"
                       f"✅ Estado: OK")
            await update.message.reply_text(mensaje, parse_mode="Markdown")
    except:
        await update.message.reply_text("❌ Error en consulta C2.")

async def mostrar_datos_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Consulta a la base de datos ANI (V1)
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args: return
    
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (context.args[0],))
        datos = cursor.fetchone()
        if datos:
            msg = (f"🪪 **DATOS CEDULA (V1)**\n\n"
                   f"👤 Nombres: `{datos['ANINombre1']} {datos['ANINombre2'] or ''}`\n"
                   f"👤 Apellidos: `{datos['ANIApellido1']} {datos['ANIApellido2']}`\n"
                   f"🏠 Dirección: `{datos['ANIDireccion']}`\n"
                   f"📱 Teléfono: `{datos['ANITelefono']}`")
            await update.message.reply_text(msg, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No encontrado en DB Local.")
    finally:
        if conn: conn.close()

# ======== GESTIÓN DE USUARIOS Y KEYS ========

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
        "┃ ⚔️ /llave ➛ CONSULTA ALIAS\n"
        "┃ ⚔️ /redeem ➛ ACTIVAR KEY\n"
        "┃ ⚔️ /info ➛ MI ESTADO\n"
        "┃ ⚔️ /help ➛ SOPORTE\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == OWNER_ID:
        await update.message.reply_text("👑 **Admin:** Acceso Ilimitado.")
        return
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT expiration_date FROM user_keys WHERE user_id = %s AND redeemed = TRUE", (user_id,))
        res = cursor.fetchone()
        if res:
            await update.message.reply_text(f"⏳ **Expira el:** `{res['expiration_date']}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Sin suscripción activa.")
    finally:
        if conn: conn.close()

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

# ======== MAIN ========
def main():
    # TOKEN ACTUALIZADO
    TOKEN = "8717607121:AAEjR8NdGjOCASuqYlfV5bLlCYNG4nBApDg"
    
    app = Application.builder().token(TOKEN).build()

    # Registro de Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", mostrar_datos_cedula))
    app.add_handler(CommandHandler("c2", comando_c2))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("redeem", redeem))
    app.add_handler(CommandHandler("info", info_command))
    
    print(f"🚀 Bot iniciado como {OWNER_USER} en Railway.")
    app.run_polling()

if __name__ == "__main__":
    main()
