import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mysql.connector import pooling
import logging
import os
import requests

# ======== CONFIGURACIÓN DE IDENTIDAD ========
OWNER_USER = "@Broquicalifoxx" #
OWNER_ID = 8114050673
BOT_USER = "@doxeos09bot"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"

# ======== CONFIGURACIÓN DE BASE DE DATOS (RAILWAY) ========
# En Railway usamos os.getenv para que lea las variables del panel de control
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
    print(f"Error configurando el Pool: {e}")

# ======== FUNCIONES DE APOYO ========
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

# ======== COMANDOS ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄  𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐯2 ⚔️\n"
        "═════════════════════════\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ /start - Menú\n"
        "┃ /cc - Consulta v1\n"
        "┃ /c2 - Consulta v2\n"
        "┃ /help - Soporte Técnico\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 **SOPORTE TÉCNICO** 🛠\n"
        "═════════════════════════\n"
        "Si tienes problemas con una API o tu suscripción:\n\n"
        f"👤 **Admin:** {OWNER_USER}\n"
        "🤖 **Bot:** @doxeos09bot\n"
        "📌 **ID:** `8114050673`"
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin acceso.")
        return
    # Aquí iría tu lógica de requests.post a la API v2...
    await update.message.reply_text("🔎 Buscando en base de datos v2...")

# ======== REGISTRO DE HANDLERS ========
def main():
    # Usa el token que ya tienes configurado
    token = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("c2", comando_c2))
    # Añade aquí tus otros comandos (cc, nequi, etc)

    app.run_polling()

if __name__ == "__main__":
    main()
