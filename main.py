import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from mysql.connector import pooling
import logging
import requests
import json
import os

# ======== CONFIGURACIÓN ========
TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
OWNER_ID = 8114050673 
OWNER_USER = "@Broquicalifoxx"

# APIs
API_URL_C2 = "https://extract.nequialpha.com/doxing"
API_NEQUI = "https://extract.nequialpha.com/consultar"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"

# Logging para ver errores en consola
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== FUNCIONES DE APOYO ========

def tiene_key_valida(user_id):
    # Si eres el dueño, siempre tienes acceso
    if user_id == OWNER_ID: return True
    # Aquí puedes añadir tu lógica de base de datos para otros usuarios
    return True 

# ======== COMANDOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Este es el comando que no te respondía. Ahora está activo."""
    texto = (
        "乄 **𝐈𝐍𝐅𝐄𝐑𝐍𝐎 𝐒𝐘𝐒𝐓𝐄𝐌** ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬.\n"
        "═════════════════════════\n"
        "👤 `/cc` ➛ 𝐂𝐄𝐃𝐔𝐋𝐀 (𝐃𝐁)\n"
        "📄 `/c2` ➛ 𝐃𝐎𝐗𝐈𝐍𝐆 𝐂𝟐\n"
        "📱 `/nequi` ➛ 𝐍𝐄𝐐𝐔𝐈\n"
        "═════════════════════════\n"
        f"👑 **Owner:** {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(texto, parse_mode="Markdown")
        logger.error(f"Error en start: {e}")

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📌 Uso: `/c2 <documento>`")
        return
    
    doc = context.args[0]
    wait = await update.message.reply_text("🔍 Buscando...")

    try:
        r = requests.post(API_URL_C2, json={"cedula": str(doc)}, timeout=20)
        data = r.json()

        # Mapeo según el JSON que me pasaste
        ide = data.get("IDENTIDAD", {})
        res = (
            "📄 **𝐑𝐄𝐒𝐔𝐋𝐓𝐀𝐃𝐎 𝐂𝟐**\n"
            "═════════════════════════\n"
            f"👤 **Nombre:** `{ide.get('Primer Nombre')} {ide.get('Segundo Nombre', '')}`\n"
            f"👤 **Apellidos:** `{ide.get('Primer Apellido')} {ide.get('Segundo Apellido', '')}`\n"
            f"🆔 **DOC:** `{data.get('Documento')}`\n"
            "═════════════════════════"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except Exception as e:
        await wait.edit_text(f"❌ Error: `{str(e)}`")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📌 Uso: `/nequi <telefono>`")
        return
    tel = context.args[0]
    wait = await update.message.reply_text("📱 Consultando...")
    try:
        h = {"X-Api-Key": "M43289032FH23B", "Content-Type": "application/json"}
        r = requests.post(API_NEQUI, json={"telefono": str(tel)}, headers=h, timeout=20)
        d = r.json()
        res = (
            "📱 **𝐃𝐀𝐓𝐎𝐒 𝐍𝐄𝐐𝐔𝐈**\n"
            "═════════════════════════\n"
            f"👤 **TITULAR:** `{d.get('nombre_completo', 'No registra')}`\n"
            f"🆔 **CÉDULA:** `{d.get('cedula', 'No registra')}`\n"
            "═════════════════════════"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except Exception as e:
        await wait.edit_text("❌ Error en Nequi.")

# ======== MAIN (ENCENDIDO) ========

def main():
    # Creamos la aplicación con tu Token
    app = Application.builder().token(TOKEN).build()

    # REGISTRO DE COMANDOS (Si no están aquí, el bot no responde)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("c2", comando_c2))
    app.add_handler(CommandHandler("nequi", comando_nequi))

    print("🔥 BOT INICIADO CORRECTAMENTE 🔥")
    app.run_polling()

if __name__ == "__main__":
    main()
