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
from datetime import datetime, timedelta

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# ======== CONFIGURACIÓN RAILWAY (Variables de Entorno) ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")

# Información del Propietario
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673 

# Pool de conexiones a la DB
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

# ======== CONFIG APIs EXTERNAS ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
NEQUI_API_URL = "https://extract.nequialpha.com/consultar"
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
TIMEOUT = 120

# ======== FUNCIONES DE LIMPIEZA Y CONSULTA API ========

def clean(value):
    if value is None or value == "" or value == "null":
        return "No registra"
    if isinstance(value, bool):
        return "Sí" if value else "No"
    return str(value)

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(API_URL_C2, json={"cedula": str(cedula)},
                          headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error C2: {e}")
        return None

def consultar_placa(placa):
    try:
        r = requests.get(PLACA_API_URL, params={"placa": placa}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error Placa: {e}")
        return None

def consultar_llave(alias):
    try:
        r = requests.get(LLAVE_API_BASE, params={"hexn": alias}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error Llave: {e}")
        return None

def consultar_nequi(telefono):
    try:
        headers = {"X-Api-Key": "M43289032FH23B", "Content-Type": "application/json"}
        r = requests.post(NEQUI_API_URL, json={"telefono": str(telefono)}, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error Nequi: {e}")
        return None

# ======== LÓGICA DE BASE DE DATOS ========

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if connection and connection.is_connected(): connection.close()

def es_admin(user_id):
    if user_id == OWNER_ID: return True
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if connection and connection.is_connected(): connection.close()

def obtener_lugar(codigo):
    if not codigo: return "No registra"
    try:
        cod_str = str(codigo)
        if len(cod_str) >= 8:
            codigo_extraido = cod_str[3:8]
            connection = pool.get_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT lug FROM lug_ori WHERE cod_lug LIKE %s", (f"%{codigo_extraido}%",))
            res = cursor.fetchone()
            connection.close()
            return res['lug'] if res else "No encontrado"
        return "Formato inválido"
    except: return "Error DB"

def buscar_cedula(cedula):
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        return cursor.fetchone()
    except: return None
    finally:
        if connection and connection.is_connected(): connection.close()

# ======== COMANDOS DE USUARIO ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"┃ ⚙️ 𝐁𝐨𝐭: {BOT_USER}\n"
        "┃ ⚔️ /start ➛ 𝐌𝐄𝐍𝐔\n"
        "┃ ⚔️ /cc ➛ 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯1\n"
        "┃ ⚔️ /c2 ➛ 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯2\n"
        "┃ ⚔️ /nequi ➛ 𝐍𝐄𝐐𝐔𝐈\n"
        "┃ ⚔️ /llave ➛ 𝐀𝐋𝐈𝐀𝐒\n"
        "┃ ⚔️ /placa ➛ 𝐏𝐋𝐀𝐂𝐀\n"
        "┃ ⚔️ /nombres ➛ 𝐍𝐎𝐌𝐁𝐑𝐄𝐒\n"
        "┃ ⚔️ /redeem ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐊𝐄𝐘\n"
        "┃ ⚔️ /info ➛ 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "═════════════════════════\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes suscripción activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <cedula>")
        return
    
    cedula = context.args[0]
    datos = buscar_cedula(cedula)
    if datos:
        msg = (
            f"🪪 CC: `{datos.get('ANINuip')}`\n\n"
            f"👤 Nombres: `{datos.get('ANINombre1')} {datos.get('ANINombre2') or ''}`\n"
            f"👤 Apellidos: `{datos.get('ANIApellido1')} {datos.get('ANIApellido2') or ''}`\n"
            f"👨 Padre: `{datos.get('ANINombresPadre') or 'No registra'}`\n"
            f"👩 Madre: `{datos.get('ANINombresMadre') or 'No registra'}`\n"
            f"📅 Nacimiento: `{datos.get('ANIFchNacimiento')}`\n"
            f"📅 Expedición: `{datos.get('ANIFchExpedicion')}`\n"
            f"🖇 Sexo: `{datos.get('ANISexo')}` | Altura: `{datos.get('ANIEstatura')}`cm\n"
            f"🏚 Dirección: `{datos.get('ANIDireccion')}`\n"
            f"📱 Teléfono: `{datos.get('ANITelefono')}`\n"
            f"💻 Nac: `{obtener_lugar(datos.get('LUGIdNacimiento'))}`\n"
            f"💻 Exp: `{obtener_lugar(datos.get('LUGIdExpedicion'))}`\n"
            f"💻 Residencia: `{obtener_lugar(datos.get('LUGIdResidencia'))}`\n"
            f"🗳 Electoral: `{obtener_lugar(datos.get('LUGIdUbicacionElectoral'))}`\n"
            f"🎓 Preparación: `{obtener_lugar(datos.get('LUGIdPreparacion'))}`\n\n"
            f"🛡 Creditos: {OWNER_USER}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No se encontraron datos.")

async def comando_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Indica la clave: `/redeem KEY-123`", parse_mode="Markdown")
        return
    key = context.args[0]
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT key_id, expiration_date FROM user_keys WHERE key_value = %s AND redeemed = FALSE AND expiration_date > NOW()", (key,))
        result = cursor.fetchone()
        if not result:
            await update.message.reply_text("❌ Clave no válida o expirada.")
            return
        cursor.execute("UPDATE user_keys SET redeemed = TRUE, user_id = %s WHERE key_id = %s", (user_id, result["key_id"]))
        connection.commit()
        await update.message.reply_text("✅ Clave redimida con éxito. ¡Ya puedes usar los comandos!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error al redimir: {e}")
    finally:
        if connection: connection.close()

# ======== COMANDOS ADMINISTRATIVOS ========

async def comando_genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not es_admin(update.message.from_user.id): return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Uso: /genkey <user_id_destino> <dias>")
        return
    try:
        target_id = int(context.args[0])
        dias = int(context.args[1])
        new_key = "KEY-" + ''.join(random.choices(string.ascii_letters + string.digits, k=12)).upper()
        exp_date = datetime.now() + timedelta(days=dias)
        
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user_keys (key_value, user_id, expiration_date, redeemed) VALUES (%s, %s, %s, FALSE)", (new_key, target_id, exp_date))
        connection.commit()
        connection.close()
        
        await update.message.reply_text(f"🔑 Key Generada: `{new_key}`\n⏳ Expira en: {dias} días", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

# ======== INICIO DEL BOT ========

def main():
    application = Application.builder().token(TOKEN).build()

    # Handlers de Usuario
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cc", comando_cc))
    application.add_handler(CommandHandler("c2", comando_c2))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("llave", comando_llave))
    application.add_handler(CommandHandler("placa", comando_placa))
    application.add_handler(CommandHandler("redeem", comando_redeem))
    application.add_handler(CommandHandler("info", comando_info))
    
    # Handlers de Admin
    application.add_handler(CommandHandler("genkey", comando_genkey))
    application.add_handler(CommandHandler("addadmin", comando_addadmin))
    application.add_handler(CommandHandler("listkey", comando_listkey))
    application.add_handler(CommandHandler("heidysql", heidysql))

    logger.info("Bot Broquicali Fusionado y en Línea.")
    application.run_polling()

if __name__ == "__main__":
    main()
