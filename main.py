import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. CARGA DE CONFIGURACIÓN
load_dotenv()

TOKEN = os.getenv('TELEGRAM_TOKEN')
DB_CONFIG = {
    'host': os.getenv('MYSQLHOST'),
    'user': os.getenv('MYSQLUSER'),
    'password': os.getenv('MYSQLPASSWORD'),
    'database': os.getenv('MYSQLDATABASE'),
    'port': os.getenv('MYSQLPORT', 3306)
}

# 2. FUNCIÓN PARA CONECTAR A LA BASE DE DATOS
def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return None

# 3. COMANDO DE INICIO (/start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"¡Hola {user.mention_html()}! 👋"
        "\nEste es tu sistema de información educativa."
        "\nUsa /login para acceder (si ya lo tienes configurado)."
    )

# 4. FUNCIÓN PRINCIPAL PARA ARRANCAR EL BOT
def main():
    if not TOKEN:
        print("❌ ERROR: No se encontró TELEGRAM_TOKEN en las variables.")
        return

    print("🚀 Bot en marcha... Revisando conexión a DB.")
    
    # Prueba rápida de conexión al iniciar
    test_conn = get_db_connection()
    if test_conn:
        print("✅ Conexión a la base de datos exitosa.")
        test_conn.close()
    else:
        print("⚠️ Advertencia: No se pudo conectar a la DB. Revisa las variables en Railway.")

    # Configurar el Bot
    application = Application.builder().token(TOKEN).build()

    # Añadir comandos
    application.add_handler(CommandHandler("start", start))

    # Lanzar el bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
