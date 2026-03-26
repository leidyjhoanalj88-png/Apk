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

# ======== CONFIGURACIÓN DE BASE DE DATOS (RAILWAY SAFE) ========
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
    print(f"⚠️ Error en Pool de DB: {e}")

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
        "┃ ⚔️ /info ➛ MI SUSCRIPCIÓN\n"
        "┃ ⚔️ /help ➛ SOPORTE TÉCNICO\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id == OWNER_ID:
        await update.message.reply_text("👑 **Suscripción:** Ilimitada (Administrador)")
        return
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT expiration_date FROM user_keys WHERE user_id = %s AND redeemed = TRUE"
        cursor.execute(query, (user_id,))
        res = cursor.fetchone()
        if res:
            await update.message.reply_text(f"⏳ **Expiración:** `{res['expiration_date']}`", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Sin suscripción activa.")
    except:
        await update.message.reply_text("❌ Error al consultar base de datos.")
    finally:
        if conn: conn.close()

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🛠 **SOPORTE**\nAdmin: {OWNER_USER}\nID: `{OWNER_ID}`", parse_mode="Markdown")

# ======== MAIN (CON TOKEN NUEVO) ========
def main():
    # TOKEN ACTUALIZADO
    TOKEN = "8717607121:AAEjR8NdGjOCASuqYlfV5bLlCYNG4nBApDg"
    
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("help", help_command))
    
    # Registra aquí tus otros comandos (cc, c2, nequi, etc.)
    
    print("🚀 Bot en línea con el nuevo token.")
    app.run_polling()

if __name__ == "__main__":
    main()
