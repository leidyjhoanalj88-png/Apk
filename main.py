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
import tempfile
import subprocess
import time
import asyncio
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ======== CONFIGURACIÓN LOGGING ========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ======== CONFIGURACIÓN RAILWAY / DB ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")

OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# Pool de conexiones para evitar caídas
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=15,
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    port=int(DB_PORT),
    charset="utf8"
)

# ======== CONFIG APIs & PRECIOS ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
COLZIA_BASE_URL = "https://ios.colzia.cc"
COLZIA_BEARER_TOKEN = os.getenv("COLZIA_BEARER_TOKEN", "") # RECUERDA CONFIGURAR EN RAILWAY

START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
TIMEOUT = 120

# Precios del script anterior (puedes ajustarlos)
PRECIOS_COMANDOS = {
    "cc": 10, "c1": 5, "c2": 15, "nequi": 10, 
    "placa": 20, "sisben": 5, "nombres": 10
}

# ======== UTILIDADES DE LIMPIEZA (FUSIONADAS) ========

def clean(value):
    """Limpieza básica para visualización"""
    if value is None or value == "" or value == "null":
        return "No registra"
    return str(value)

def c2_clean(text):
    """Lógica de limpieza de caracteres del primer script"""
    if not text: return "No registra"
    try:
        return text.encode("latin-1").decode("utf-8")
    except:
        return text

# ======== FUNCIONES DE CONSULTA (APIS VIVAS) ========

def consultar_salud_total(cedula):
    """API SaludTotal (del script 1)"""
    url = f"https://prestadores.saludtotal.com.co/api/afiliado/consultar/{cedula}"
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        return r.json() if r.status_code == 200 else None
    except:
        return None

def consultar_nequi(telefono):
    """Consulta Nequi con Fallback (Colzia + Alpha)"""
    # Intento 1: Colzia
    if COLZIA_BEARER_TOKEN:
        try:
            h = {"Authorization": f"Bearer {COLZIA_BEARER_TOKEN}", "Content-Type": "application/json"}
            r = requests.post(f"{COLZIA_BASE_URL}/api/consultar", json={"telefono": str(telefono)}, headers=h, timeout=15)
            if r.status_code == 200: return r.json()
        except: pass

    # Intento 2: NequiAlpha
    try:
        h = {"X-Api-Key": "Z5k4Y1n4n0vS", "Content-Type": "application/json"}
        r = requests.post("https://extract.nequialpha.com/consultar", json={"telefono": str(telefono)}, headers=h, timeout=15)
        return r.json() if r.status_code == 200 else None
    except:
        return None

# ======== LOGICA DE BD ========

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

def buscar_cedula_local(cedula):
    """Consulta en la tabla 'ani' local de MySQL"""
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        return cursor.fetchone()
    except: return None
    finally:
        if conn: conn.close()

# ======== COMANDOS FUSIONADOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬, 𝐬𝐨𝐥𝐨 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 ⚔️\n"
        "═════════════════════════\n"
        "┃ ⚔️ /cc [cedula] ➛ 𝐀𝐍𝐈 (Local)\n"
        "┃ ⚔️ /c1 [cedula] ➛ 𝐒𝐀𝐋𝐔𝐃 𝐓𝐎𝐓𝐀𝐋\n"
        "┃ ⚔️ /c2 [cedula] ➛ 𝐃𝐎𝐗𝐈𝐍𝐆 𝐄𝐗𝐓\n"
        "┃ ⚔️ /nequi [cel] ➛ 𝐍𝐄𝐐𝐔𝐈 𝐈𝐍𝐅𝐎\n"
        "┃ ⚔️ /sisben [t] [d] ➛ 𝐒𝐈𝐒𝐁𝐄𝐍 𝐈𝐕\n"
        "┃ ⚔️ /placa [placa] ➛ 𝐑𝐔𝐍𝐓/𝐒𝐈𝐌𝐈𝐓\n"
        "┃ ⚔️ /nombres [nom] ➛ 𝐁𝐔𝐒𝐐𝐔𝐄𝐃𝐀 𝐀𝐍𝐈\n"
        "┃ ⚔️ /info ➛ 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "═════════════════════════\n"
        f"👑 𝘿𝙚𝙨𝙖𝙧𝙧𝙤𝙡𝙡𝙖𝙙𝙤 𝙥𝙤𝙧: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def comando_c1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Nuevo comando SaludTotal"""
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /c1 <cedula>")
        return
    
    cedula = context.args[0]
    msg = await update.message.reply_text("🔍 Consultando SaludTotal...")
    res = consultar_salud_total(cedula)
    
    if res:
        # Ajustado a la estructura JSON de SaludTotal
        nombre = c2_clean(res.get('nombreCompleto', 'No registra'))
        estado = res.get('estadoAfiliacion', 'No registra')
        tipo = res.get('tipoAfiliado', 'No registra')
        texto = (
            f"🏥 *SALUD TOTAL EPS*\n\n"
            f"👤 *Nombre:* `{nombre}`\n"
            f"✅ *Estado:* `{estado}`\n"
            f"🧬 *Tipo:* `{tipo}`\n"
            f"🆔 *ID:* `{cedula}`\n\n"
            f"💻 By {OWNER_USER}"
        )
        await msg.edit_text(texto, parse_mode="Markdown")
    else:
        await msg.edit_text("❌ No se hallaron datos en SaludTotal.")

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Consulta ANI Local con Limpieza de caracteres"""
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin suscripción.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <cedula>")
        return
    
    datos = buscar_cedula_local(context.args[0])
    if datos:
        # Aplicamos limpieza c2_clean a los nombres
        n1 = c2_clean(datos.get('ANINombre1'))
        n2 = c2_clean(datos.get('ANINombre2'))
        a1 = c2_clean(datos.get('ANIApellido1'))
        a2 = c2_clean(datos.get('ANIApellido2'))
        
        msg = (
            f"🪪 *REGISTRO ANI*\n\n"
            f"👤 Nombres: `{n1} {n2 or ''}`\n"
            f"👤 Apellidos: `{a1} {a2 or ''}`\n"
            f"📅 Nacimiento: `{datos.get('ANIFchNacimiento')}`\n"
            f"🏚 Dirección: `{datos.get('ANIDireccion') or 'No registra'}`\n"
            f"📱 Teléfono: `{datos.get('ANITelefono') or 'No registra'}`\n\n"
            f"💻 By {OWNER_USER}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No encontrado en base local.")

# [Mantener el resto de comandos: /c2, /nequi, /sisben, /placa, /redeem tal cual los tienes]
# [Copiar aquí las funciones comando_c2, comando_nequi, comando_sisben del código actual]

async def comando_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT expiration_date FROM user_keys WHERE user_id = %s AND redeemed = TRUE", (user_id,))
        res = cursor.fetchone()
        if res:
            await update.message.reply_text(f"🔑 Suscripción Activa\n📅 Vence: {res['expiration_date']}")
        else:
            await update.message.reply_text("❌ No tienes suscripción activa.")
    finally:
        if conn: conn.close()

# ======== INICIALIZACIÓN (MAIN) ========

def main():
    # Inicialización de la aplicación
    application = Application.builder().token(TOKEN).build()

    # Handlers Fusionados
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cc", comando_cc))
    application.add_handler(CommandHandler("c1", comando_c1)) # API SaludTotal inyectada
    application.add_handler(CommandHandler("c2", comando_c2))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("sisben", comando_sisben))
    application.add_handler(CommandHandler("placa", comando_placa))
    application.add_handler(CommandHandler("redeem", comando_redeem))
    application.add_handler(CommandHandler("info", comando_info))
    
    # Comandos Administrativos
    application.add_handler(CommandHandler("genkey", comando_genkey))
    application.add_handler(CommandHandler("addadmin", comando_addadmin))

    print("🚀 Bot Fusión Broquicali iniciado correctamente.")
    application.run_polling()

if __name__ == "__main__":
    main()
