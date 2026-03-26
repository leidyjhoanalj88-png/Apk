import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mysql.connector import pooling
import logging
import os
import requests

# ======== CONFIGURACIÓN DE IDENTIDAD ========
OWNER_USER = "@Broquicalifoxx" 
OWNER_ID = 8114050673 
BOT_USER = "@doxeos09bot"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"

# ======== CONFIGURACIÓN DE BASE DE DATOS (RAILWAY) ========
# Se usan variables de entorno para evitar el error de conexión (111) en Railway.
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="pool_db",
        pool_size=10,
        host=os.getenv('MYSQLHOST', 'localhost'),
        user=os.getenv('MYSQLUSER', 'root'),
        password=os.getenv('MYSQLPASSWORD', 'nabo94nabo94'),
        database=os.getenv('MYSQLDATABASE', 'ani'),
        port=int(os.getenv('MYSQLPORT', 3306)),
        charset="utf8"
    )
except Exception as e:
    print(f"Error en Pool: {e}")

# ======== FUNCIONES DE VALIDACIÓN ========
def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        query = "SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()"
        cursor.execute(query, (user_id,))
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
        f"┃ ⚙️ Bot: {BOT_USER}\n"
        "┃ ⚔️ /start ➛ MENU PRINCIPAL\n"
        "┃ ⚔️ /cc ➛ CONSULTA CEDULA v1\n"
        "┃ ⚔️ /c2 ➛ CONSULTA CEDULA v2\n"
        "┃ ⚔️ /nequi ➛ CONSULTA NEQUI\n"
        "┃ ⚔️ /llave ➛ CONSULTA ALIAS\n"
        "┃ ⚔️ /placa ➛ CONSULTA PLACA\n"
        "┃ ⚔️ /redeem ➛ ACTIVAR KEY\n"
        "┃ ⚔️ /help ➛ SOPORTE TÉCNICO\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 **SOPORTE TÉCNICO**\n"
        "═════════════════════════\n"
        f"Cualquier duda contacta al Admin: {OWNER_USER}\n"
        "ID Soporte: `8114050673`"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

# Comandos de consulta (Integrando la lógica del segundo código)
async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin suscripción activa.")
        return
    # Lógica de API C2 aquí...
    await update.message.reply_text("🔎 Consultando base de datos v2...")

# ======== REGISTRO TOTAL DE COMANDOS ========
def main():
    # REVISIÓN: Asegúrate de que este token no tenga espacios al inicio o final
    TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
    
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("c2", comando_c2))
    # Aquí puedes seguir añadiendo el resto de comandos (cc, nequi, etc.)

    print(f"Bot iniciado como {OWNER_USER}")
    application.run_polling()

if __name__ == "__main__":
    main()
