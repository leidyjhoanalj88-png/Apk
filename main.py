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
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

# ======== CONFIGURACIÓN LOGGING ========
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# ======== CONFIGURACIÓN RAILWAY (DB) ========
DB_HOST = os.getenv("DB_HOST", "mysql.railway.internal")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "nabo94nabo94")
DB_NAME = os.getenv("DB_NAME", "ani")
DB_PORT = os.getenv("DB_PORT", "3306")
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=10,
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
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
TIMEOUT = 120

# APIS NEQUI (Colzia + Alpha Fallback)
COLZIA_BASE_URL = "https://ios.colzia.cc"
COLZIA_BEARER_TOKEN = os.getenv("COLZIA_BEARER_TOKEN", "")
NEQUI_ALPHA_URL = "https://extract.nequialpha.com/consultar"
NEQUI_ALPHA_KEY = os.getenv("NEQUI_ALPHA_KEY", "Z5k4Y1n4n0vS")

# ======== UTILS ========

def clean(value):
    if value is None or value == "" or value == "null": return "No registra"
    if isinstance(value, bool): return "Sí" if value else "No"
    return str(value)

# ======== LÓGICA NEQUI DUAL ========

def consultar_nequi_colzia(telefono):
    if not COLZIA_BEARER_TOKEN: return "TOKEN_VACIO"
    try:
        headers = {"Authorization": f"Bearer {COLZIA_BEARER_TOKEN}", "Content-Type": "application/json"}
        r = requests.post(f"{COLZIA_BASE_URL}/api/consultar", json={"telefono": str(telefono)}, headers=headers, timeout=15)
        if r.status_code == 401: return "TOKEN_INVALIDO"
        if r.status_code == 404: return None
        r.raise_for_status()
        return r.json()
    except: return None

def consultar_nequi_alpha(telefono):
    try:
        headers = {"X-Api-Key": NEQUI_ALPHA_KEY, "User-Agent": "ScanbotSDK/1.0", "Content-Type": "application/json"}
        r = requests.post(NEQUI_ALPHA_URL, json={"telefono": str(telefono)}, headers=headers, timeout=20)
        if r.status_code in (401, 403): return "KEY_INVALIDA"
        r.raise_for_status()
        return r.json()
    except: return None

def consultar_nequi(telefono):
    # 1. Intentar Colzia
    res_colzia = consultar_nequi_colzia(telefono)
    if isinstance(res_colzia, dict): return (res_colzia, "colzia")
    
    # 2. Fallback Alpha
    res_alpha = consultar_nequi_alpha(telefono)
    if isinstance(res_alpha, dict): return (res_alpha, "nequialpha")
    
    return (None, "❌ Error: Ambas APIs de Nequi están fuera de servicio.")

# ======== LÓGICA SISBEN IV (Web Scraping) ========

def consultar_sisben(tipo, numero):
    url_sisben = "https://reportes.sisben.gov.co/dnp_sisbenconsulta"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    session = requests.Session()
    try:
        r = session.get(url_sisben, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "__RequestVerificationToken"})['value']
        data = {"TipoID": tipo, "documento": numero, "__RequestVerificationToken": token}
        r_post = session.post(url_sisben, data=data, headers=headers, timeout=15)
        
        if "no se encontr" in r_post.text.lower(): return None
        
        soup_res = BeautifulSoup(r_post.text, "html.parser")
        resultado = {}
        # Extraer Grupo
        g = soup_res.find("p", class_=lambda x: x and "text-uppercase" in x and "text-white" in x)
        if g: resultado["grupo"] = g.get_text(strip=True)
        # Extraer Clasificación
        d = soup_res.find("div", class_="imagenpuntaje")
        if d: 
            c = d.find("p", style=lambda x: x and "18px" in str(x))
            if c: resultado["clasificacion"] = c.get_text(strip=True)
            
        # Mapear otros campos
        mapeo = {"Nombres": "nombres", "Apellidos": "apellidos", "Municipio": "municipio", "Departamento": "departamento"}
        for texto, clave in mapeo.items():
            e = soup_res.find("p", string=lambda x: texto in str(x) if x else False)
            if e:
                s = e.find_next_sibling("p")
                if s: resultado[clave] = s.get_text(strip=True)
        return resultado
    except Exception as e:
        logger.error(f"Error Sisben: {e}")
        return {"error": "Fallo en la conexión con el portal Sisben."}

# ======== FUNCIONES BD (Sin cambios) ========

def tiene_key_valida(user_id):
    if user_id == OWNER_ID: return True
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if connection and connection.is_connected(): connection.close()

def es_admin(user_id):
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        return cursor.fetchone() is not None
    except: return False
    finally:
        if connection and connection.is_connected(): connection.close()

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

def obtener_lugar(codigo):
    if not codigo: return None
    connection = None
    try:
        codigo_extraido = str(codigo)[3:8]
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT lug FROM lug_ori WHERE cod_lug LIKE %s", (f"%{codigo_extraido}%",))
        res = cursor.fetchone()
        return res['lug'] if res else None
    except: return None
    finally:
        if connection and connection.is_connected(): connection.close()

# ======== COMANDOS DE CONSULTA ========

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /nequi <telefono>")
        return

    tel = context.args[0]
    msg = await update.message.reply_text("🔍 Consultando Nequi (Sistema Dual)...")
    datos, fuente = consultar_nequi(tel)

    if datos is None:
        await msg.edit_text(fuente)
        return

    f_label = "🔵 Colzia" if fuente == "colzia" else "🟡 NequiAlpha"
    nombre = datos.get("nombre_completo") or datos.get("nombre") or "No registra"
    cedula = datos.get("cedula") or datos.get("documento") or "No registra"
    
    resp = (
        f"📱 *Consulta Nequi* {f_label}\n"
        f"══════════════════════\n"
        f"📞 Teléfono: `{tel}`\n"
        f"👤 Nombre: `{nombre}`\n"
        f"🆔 Cédula: `{cedula}`\n"
        f"📍 Municipio: `{datos.get('municipio', 'No registra')}`\n"
        f"══════════════════════\n"
        f"💻 {OWNER_USER}"
    )
    await msg.edit_text(resp, parse_mode="Markdown")

async def comando_sisben(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Uso: /sisben <tipo> <documento>\nEj: `/sisben 3 1000...` (3=Cédula)")
        return
    
    msg = await update.message.reply_text("🔍 Consultando SISBEN IV...")
    res = consultar_sisben(context.args[0], context.args[1])
    
    if not res:
        await msg.edit_text("❌ No se encontró registro en Sisben.")
        return
    if "error" in res:
        await msg.edit_text(f"⚠️ {res['error']}")
        return

    texto = (
        "📊 *RESULTADO SISBEN IV*\n\n"
        f"📊 *Grupo:* {res.get('grupo', 'N/A')}\n"
        f"📋 *Clasificación:* {res.get('clasificacion', 'N/A')}\n\n"
        f"👤 *Nombre:* {res.get('nombres')} {res.get('apellidos')}\n"
        f"📍 *Ubicación:* {res.get('municipio')}, {res.get('departamento')}\n\n"
        f"💻 {OWNER_USER}"
    )
    await msg.edit_text(texto, parse_mode="Markdown")

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <cedula>")
        return
    
    datos = buscar_cedula(context.args[0])
    if datos:
        l_nac = obtener_lugar(datos.get('LUGIdNacimiento'))
        l_res = obtener_lugar(datos.get('LUGIdResidencia'))
        msg = (
            f"🪪 CC: `{datos.get('ANINuip')}`\n\n"
            f"👤 Nombre: `{datos.get('ANINombre1')} {datos.get('ANINombre2') or ''}`\n"
            f"👤 Apellido: `{datos.get('ANIApellido1')} {datos.get('ANIApellido2') or ''}`\n"
            f"📅 Nacimiento: `{datos.get('ANIFchNacimiento')}`\n"
            f"🏠 Residencia: `{l_res or 'No registra'}`\n"
            f"🌎 Origen: `{l_nac or 'No registra'}`\n\n"
            f"💻 {OWNER_USER}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No encontrado en base de datos local.")

# ======== COMANDOS ADMINISTRATIVOS (Igual a tu bot) ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚔️ /cc      ➛ CÉDULA V1 (Local)\n"
        "┃ ⚔️ /c2      ➛ CÉDULA V2 (API)\n"
        "┃ ⚔️ /nequi   ➛ NEQUI (Dual API)\n"
        "┃ ⚔️ /sisben  ➛ SISBEN IV\n"
        "┃ ⚔️ /placa   ➛ CONSULTA PLACA\n"
        "┃ ⚔️ /redeem  ➛ ACTIVAR KEY\n"
        "┃ ⚔️ /info    ➛ MI ESTADO\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"👑 Dueño: {OWNER_USER}"
    )
    await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)

async def registrar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    uname = update.message.from_user.username
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT IGNORE INTO users (user_id, telegram_username, date_registered) VALUES (%s, %s, NOW())", (uid, uname))
        conn.commit()
    except: pass
    finally:
        if conn: conn.close()

# ======== MAIN ========

def main():
    application = Application.builder().token(TOKEN).build()

    # Handlers Base
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("cc", comando_cc))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("sisben", comando_sisben))
    
    # Comandos que ya tenías (se mantienen igual)
    application.add_handler(CommandHandler("redeem", lambda u, c: None)) # Aquí va tu función original
    # ... agregar el resto de tus handlers ...

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_usuario))
    
    logger.info("Bot Broquicali Fusionado Online")
    application.run_polling()

if __name__ == "__main__":
    main()
