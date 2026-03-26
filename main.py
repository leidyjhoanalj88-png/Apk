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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# ======== CONFIGURACIÓN RAILWAY ========
DB_HOST = os.getenv("DB_HOST", "centerbeam.proxy.rlwy.net")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASSWORD", "RyCNgwehnwQnOiGkMdZsuvHyLpMZZQd")
DB_NAME = os.getenv("DB_NAME", "railway")
DB_PORT = os.getenv("DB_PORT", "24155")

TOKEN = os.getenv("TELEGRAM_TOKEN", "8717607121:AAEjR8NdGjOCASuqYlfV5bL1CYNG4nBApDg")
OWNER_USER = "@Broquicalifoxx"
BOT_USER = "@doxeos09bot"
OWNER_ID = 8114050673

# VARIABLES ADICIONALES
API_URL_C2 = os.getenv("API_URL", "https://extract.nequialpha.com/doxing")
NEQUI_API_KEY = os.getenv("NEQUI_API_KEY", "M43289032FH23B")
START_IMAGE_URL = os.getenv("START_IMAGE_URL", "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-1")

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

# ======== CONFIG APIs ========
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
TIMEOUT = 120

# ======== FUNCIONES LÓGICA ========

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
        logger.error(f"Error al consultar C2: {e}")
        return None

def consultar_placa(placa):
    try:
        r = requests.get(PLACA_API_URL, params={"placa": placa}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar placa: {e}")
        return None

def consultar_llave(alias):
    try:
        r = requests.get(LLAVE_API_BASE, params={"hexn": alias}, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar llave: {e}")
        return None

# ======== FUNCIÓN NEQUI CORREGIDA (EVITA NAMERESOLUTIONERROR) ========
def consultar_nequi_scraping(telefono):
    """Consulta el nombre del titular usando un endpoint de pasarela más estable"""
    # Usamos un endpoint alternativo que no depende del subdominio inestable de Nequi
    url_alt = "https://api.puntosred.co/api/v1/recargas/operadores/nequi/consultar"
    
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    }
    payload = {"celular": str(telefono)}
    
    try:
        # Intento con timeout corto para no bloquear el bot
        r = requests.post(url_alt, json=payload, headers=headers, timeout=12)
        
        if r.status_code == 200:
            data = r.json()
            # Buscamos el nombre en los posibles campos que devuelve la API
            nombre = data.get("nombre") or data.get("cliente") or data.get("full_name")
            if nombre:
                return {"success": True, "nombre": nombre}
        
        return {"success": False, "error": "No se encontró titular o servicio fuera de línea."}
    except Exception as e:
        logger.error(f"Error Nequi: {e}")
        return {"success": False, "error": "Error de conexión con el nodo de consulta."}

# ======== FUNCIONES BD ========

def tiene_key_valida(user_id):
    if user_id == OWNER_ID:
        return True
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    except:
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def es_admin(user_id):
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM admins WHERE user_id = %s", (user_id,))
        return cursor.fetchone() is not None
    except:
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()

def buscar_cedula(cedula):
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT ANINuip, ANIApellido1, ANIApellido2, ANINombre1, ANINombre2,
                   ANINombresPadre, ANINombresMadre, ANIFchNacimiento, ANIFchExpedicion,
                   ANISexo, ANIEstatura, ANIDireccion, ANITelefono,
                   LUGIdNacimiento, LUGIdExpedicion, LUGIdResidencia,
                   LUGIdUbicacionElectoral, LUGIdPreparacion,
                   ANIFchActualizacion, GRSId
            FROM ani WHERE ANINuip = %s
        """, (cedula,))
        return cursor.fetchone()
    except:
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

def obtener_lugar(codigo):
    connection = None
    try:
        if not codigo:
            return None
        codigo = str(codigo)
        if len(codigo) < 8:
            return None
        codigo_extraido = codigo[3:8]
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM lug_ori WHERE cod_lug LIKE %s", (f"%{codigo_extraido}%",))
        resultado = cursor.fetchone()
        return resultado['lug'] if resultado else None
    except:
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

def buscar_por_nombres(nombre_completo):
    connection = None
    try:
        partes = nombre_completo.split()
        if len(partes) < 3:
            return None
        nombre1, apellido1, apellido2 = partes[0], partes[1], partes[2]
        nombre2 = partes[3] if len(partes) > 3 else None
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT ANINuip, ANIApellido1, ANIApellido2, ANINombre1, ANINombre2,
                   ANINombresPadre, ANINombresMadre, ANIFchNacimiento, ANIFchExpedicion,
                   ANISexo, ANIEstatura, ANIDireccion, ANITelefono,
                   LUGIdNacimiento, LUGIdExpedicion, LUGIdResidencia
            FROM ani WHERE ANINombre1 = %s AND ANIApellido1 = %s AND ANIApellido2 = %s
        """
        params = [nombre1, apellido1, apellido2]
        if nombre2:
            query += " AND ANINombre2 = %s"
            params.append(nombre2)
        cursor.execute(query, tuple(params))
        return cursor.fetchall()
    except:
        return None
    finally:
        if connection and connection.is_connected():
            connection.close()

# ======== INIT DB ========

def init_db():
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_keys (
                key_id INT AUTO_INCREMENT PRIMARY KEY,
                key_value VARCHAR(50),
                user_id BIGINT,
                redeemed BOOLEAN DEFAULT FALSE,
                expiration_date DATETIME,
                created_at DATETIME DEFAULT NOW()
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id BIGINT PRIMARY KEY
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                telegram_username VARCHAR(100),
                date_registered DATETIME
            )
        """)
        connection.commit()
        logger.info("Tablas verificadas correctamente.")
    except Exception as e:
        logger.error(f"Error creando tablas: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

# ======== COMANDOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐁𝐑𝐎𝐐𝐔𝐈 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬, 𝐬𝐨𝐥𝐨 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        f"┃ ⚙️ 𝐁𝐨𝐭: {BOT_USER}\n"
        "┃ ⚔️ /start ➛ 𝐌𝐄𝐍𝐔 𝐏𝐑𝐈𝐍𝐂𝐈𝐏𝐀𝐋\n"
        "┃ ⚔️ /cc ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯1\n"
        "┃ ⚔️ /c2 ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝐄𝐃𝐔𝐋𝐀 𝐯2\n"
        "┃ ⚔️ /nequi ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐍𝐄𝐐𝐔𝐈\n"
        "┃ ⚔️ /llave ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐀𝐋𝐈𝐀𝐒\n"
        "┃ ⚔️ /placa ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        "┃ ⚔️ /nombres ➛ 𝐁𝐔𝐒𝐂𝐀𝐑 𝐏𝐎𝐑 𝐍𝐎𝐌𝐁𝐑𝐄\n"
        "┃ ⚔️ /sisben ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐒𝐈𝐒𝐁𝐄𝐍 𝐈𝐕\n"
        "┃ ⚔️ /redeem ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐊𝐄𝐘\n"
        "┃ ⚔️ /info ➛ 𝐌𝐈 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "┃ ⚔️ /help ➛ 𝐀𝐘𝐔𝐃𝐀\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "⚠️ 𝐂𝐚𝐝𝐚 𝐎𝐫𝐝𝐞𝐧 𝐄𝐣𝐞𝐜𝐮𝐭𝐚𝐝𝐚 𝐝𝐞𝐣𝐚 𝐜𝐢𝐜𝐚𝐭𝐫𝐢𝐜𝐞𝐬...𝐔𝐬𝐚𝐥𝐨 𝐜𝐨𝐧 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐚𝐛𝐢𝐥𝐢𝐝𝐚𝐝 𝐨 𝐬𝐞𝐫𝐚𝐬 𝐝𝐞𝐛𝐨𝐫𝐚𝐝𝐨.\n"
        "═════════════════════════\n"
        f"👑 𝘿𝙚𝙨𝙖𝙧𝙧𝙤𝙡𝙡𝙖𝙙𝙤 𝙥𝙤𝙧: {OWNER_USER}"
    )
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>📚 Comandos disponibles 📚</b>\n\n"
        "<b>🚀 /start</b> - Menú principal\n\n"
        "<b>🪪 /cc</b> [cedula] - Consulta por cédula v1\n\n"
        "<b>📄 /c2</b> [documento] - Consulta por cédula v2\n\n"
        "<b>👤 /nombres</b> [nombre apellido1 apellido2] - Buscar por nombre\n\n"
        "<b>📱 /nequi</b> [telefono] - Consulta Nequi\n\n"
        "<b>🔑 /llave</b> [alias] - Consulta alias\n\n"
        "<b>🚗 /placa</b> [placa] - Consulta placa\n\n"
        "<b>📊 /sisben</b> [tipo] [documento] - Consulta SISBEN IV\n\n"
        "<b>🎫 /redeem</b> [KEY-xxx] - Activar key\n\n"
        "<b>🔒 /info</b> - Ver mi suscripción\n\n"
        f"<b>💻 Desarrollado por {OWNER_USER}</b>",
        parse_mode="HTML"
    )

async def comando_addkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        await update.message.reply_text("❌ Sin permisos.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Uso: /addkey <user_id> <dias>")
        return
    try:
        target_id = int(context.args[0])
        dias = int(context.args[1])
        expiration = datetime.now() + timedelta(days=dias)
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO user_keys (user_id, redeemed, expiration_date)
            VALUES (%s, TRUE, %s)
            ON DUPLICATE KEY UPDATE redeemed = TRUE, expiration_date = %s
        """, (target_id, expiration, expiration))
        connection.commit()
        connection.close()
        await update.message.reply_text(f"✅ Key activada para {target_id} por {dias} días.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def comando_genkey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID and not es_admin(update.message.from_user.id):
        await update.message.reply_text("❌ Sin permisos.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("📌 Uso: /genkey <user_id> <dias>")
        return
    try:
        target_id = int(context.args[0])
        dias = int(context.args[1])
        key = "KEY-" + ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        expiration = datetime.now() + timedelta(days=dias)
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO user_keys (key_value, user_id, expiration_date) VALUES (%s, %s, %s)",
                       (key, target_id, expiration))
        connection.commit()
        connection.close()
        await update.message.reply_text(f"🔑 Key: `{key}`\nExpira: {expiration}", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def comando_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args:
        await update.message.reply_text("⚠️ Uso: `/redeem KEY-xxx`", parse_mode="Markdown")
        return
    key = context.args[0]
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT key_id, expiration_date FROM user_keys
            WHERE key_value = %s AND redeemed = FALSE AND expiration_date > NOW()
        """, (key,))
        result = cursor.fetchone()
        if not result:
            await update.message.reply_text("❌ Clave no válida, ya redimida o expirada.")
            return
        cursor.execute("UPDATE user_keys SET redeemed = TRUE, user_id = %s WHERE key_id = %s",
                       (user_id, result["key_id"]))
        connection.commit()
        await update.message.reply_text("✅ Clave redimida con éxito.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

async def comando_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT expiration_date, DATEDIFF(expiration_date, NOW()) AS dias_restantes
            FROM user_keys WHERE user_id = %s AND redeemed = TRUE ORDER BY expiration_date DESC LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        if result:
            await update.message.reply_text(
                f"🔑 Suscripción activa\n"
                f"⏳ Expira en: {result['dias_restantes']} días\n"
                f"📅 Fecha: {result['expiration_date']}\n\n"
                f"💻 Desarrollado por {OWNER_USER}"
            )
        else:
            await update.message.reply_text("❌ No tienes suscripción activa.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /cc <cedula>")
        return
    datos = buscar_cedula(context.args[0])
    if datos:
        lugar_nac = obtener_lugar(datos.get('LUGIdNacimiento'))
        lugar_exp = obtener_lugar(datos.get('LUGIdExpedicion'))
        lugar_res = obtener_lugar(datos.get('LUGIdResidencia'))
        lugar_elec = obtener_lugar(datos.get('LUGIdUbicacionElectoral'))
        lugar_prep = obtener_lugar(datos.get('LUGIdPreparacion'))
        msg = (
            f"🪪 CC: `{datos.get('ANINuip')}`\n\n"
            f"👤 Nombres: `{datos.get('ANINombre1')}` `{datos.get('ANINombre2') or ''}`\n"
            f"👤 Apellidos: `{datos.get('ANIApellido1')}` `{datos.get('ANIApellido2') or ''}`\n"
            f"👨 Padre: `{datos.get('ANINombresPadre') or 'No registra'}`\n"
            f"👩 Madre: `{datos.get('ANINombresMadre') or 'No registra'}`\n"
            f"📅 Nacimiento: `{datos.get('ANIFchNacimiento') or 'No registra'}`\n"
            f"📅 Expedición: `{datos.get('ANIFchExpedicion') or 'No registra'}`\n"
            f"🖇 Sexo: `{datos.get('ANISexo') or 'No registra'}`\n"
            f"🔆 Estatura: `{datos.get('ANIEstatura') or 'No registra'}` cm\n"
            f"🏚 Dirección: `{datos.get('ANIDireccion') or 'No registra'}`\n"
            f"📱 Teléfono: `{datos.get('ANITelefono') or 'No registra'}`\n"
            f"💻 Nac.: `{lugar_nac or 'No encontrado'}`\n"
            f"💻 Exp.: `{lugar_exp or 'No encontrado'}`\n"
            f"💻 Res.: `{lugar_res or 'No encontrado'}`\n"
            f"🗳 Electoral: `{lugar_elec or 'No encontrado'}`\n"
            f"🎓 Preparación: `{lugar_prep or 'No encontrado'}`\n\n"
            f"💻 Desarrollado por {OWNER_USER}"
        )
        await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No encontrado.")

async def comando_nombres(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /nombres <nombre> <apellido1> <apellido2>")
        return
    nombre_completo = " ".join(context.args)
    if len(context.args) < 3:
        await update.message.reply_text("⚠️ Incluye al menos un nombre y dos apellidos.")
        return
    await update.message.reply_text("🔍 Buscando...")
    datos = buscar_por_nombres(nombre_completo)
    if datos:
        for dato in datos:
            lugar_nac = obtener_lugar(dato.get('LUGIdNacimiento'))
            lugar_exp = obtener_lugar(dato.get('LUGIdExpedicion'))
            lugar_res = obtener_lugar(dato.get('LUGIdResidencia'))
            msg = (
                f"🪪 CC: `{dato.get('ANINuip')}`\n"
                f"👤 `{dato.get('ANINombre1')}` `{dato.get('ANINombre2') or ''}` "
                f"`{dato.get('ANIApellido1')}` `{dato.get('ANIApellido2') or ''}`\n"
                f"👨 Padre: `{dato.get('ANINombresPadre') or 'No registra'}`\n"
                f"👩 Madre: `{dato.get('ANINombresMadre') or 'No registra'}`\n"
                f"📅 Nac.: `{dato.get('ANIFchNacimiento') or 'No registra'}`\n"
                f"🏚 Dir.: `{dato.get('ANIDireccion') or 'No registra'}`\n"
                f"📱 Tel.: `{dato.get('ANITelefono') or 'No registra'}`\n"
                f"💻 Nac.: `{lugar_nac or 'No encontrado'}`\n"
                f"💻 Exp.: `{lugar_exp or 'No encontrado'}`\n"
                f"💻 Res.: `{lugar_res or 'No encontrado'}`\n\n"
                f"💻 Desarrollado por {OWNER_USER}"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No encontrado.")

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /c2 <documento>")
        return
    try:
        res = consultar_cedula_c2(context.args[0])
        if not res or not res.get("success"):
            await update.message.reply_text("❌ No se encontró información.")
            return
        d = res.get("data", {})
        mensaje = f"📄 RESULTADO\n\n🆔 Documento: {clean(d.get('cedula'))}\n🪪 Tipo: {clean(d.get('tipo_documento'))}\n\n"
        secciones = {
            "👤 IDENTIDAD": ["primer_nombre", "segundo_nombre", "primer_apellido", "segundo_apellido", "sexo", "genero", "orientacion_sexual", "fecha_nacimiento"],
            "📍 UBICACIÓN": ["pais_nacimiento", "departamento_nacimiento", "municipio_nacimiento", "pais_residencia", "departamento_residencia", "municipio_residencia", "area_residencia", "direccion"],
            "🏥 SALUD": ["regimen_afiliacion", "eps", "esquema_vacunacion_completo", "esquema_vacunacion_adecuado"],
            "📋 ESTADO": ["estudia_actualmente", "pertenencia_etnica", "desplazado", "discapacitado", "victima_conflicto_armado", "fallecido"]
        }
        usados = {"cedula", "tipo_documento"}
        for titulo, campos in secciones.items():
            bloque = []
            for campo in campos:
                if campo in d:
                    usados.add(campo)
                    bloque.append(f"• {campo.replace('_',' ').title()}: {clean(d.get(campo))}")
            if bloque:
                mensaje += f"{titulo}\n" + "\n".join(bloque) + "\n\n"
        extras = [f"• {k.replace('_',' ').title()}: {clean(v)}" for k, v in d.items() if k not in usados]
        if extras:
            mensaje += "🧩 OTROS\n" + "\n".join(extras) + "\n\n"
        mensaje += f"💻 Desarrollado por {OWNER_USER}"
        await update.message.reply_text(mensaje)
    except Exception as e:
        logger.error(f"Error en /c2: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud.")

# ======== COMANDO NEQUI CORREGIDO ========
async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /nequi <telefono>")
        return
    
    telefono = context.args[0]
    # Mensaje de carga para mejorar la experiencia
    msg = await update.message.reply_text(f"🔍 Buscando titular de `{telefono}`...", parse_mode="Markdown")
    
    try:
        res = consultar_nequi_scraping(telefono)
        if res["success"]:
            mensaje = (
                f"🔎 *Resultado /nequi*\n\n"
                f"📱 *Teléfono:* `{telefono}`\n"
                f"👤 *Titular:* `{res['nombre']}`\n\n"
                f"💻 Desarrollado por {OWNER_USER}"
            )
            await msg.edit_text(mensaje, parse_mode="Markdown")
        else:
            await msg.edit_text(f"❌ {res['error']}")
    except Exception as e:
        logger.error(f"Error en comando /nequi: {e}")
        await msg.edit_text("❌ Error interno al consultar Nequi.")

async def comando_llave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /llave <alias>")
        return
    alias = context.args[0]
    try:
        res = consultar_llave(alias)
        if (res is None or res == "null") and alias.startswith("@"):
            res = consultar_llave(alias[1:])
        mensaje_json = json.dumps(res, indent=2, ensure_ascii=False)
        await update.message.reply_text(f"```json\n{mensaje_json}\n```", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error en /llave: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud.")

async def comando_placa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /placa <placa>")
        return
    try:
        res = consultar_placa(context.args[0].upper())
        mensaje_json = json.dumps(res, indent=2, ensure_ascii=False)
        if len(mensaje_json) > 4000:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(mensaje_json)
                temp_file = f.name
            with open(temp_file, 'rb') as f:
                await update.message.reply_document(document=f, filename=f"placa_{context.args[0]}.txt")
            os.remove(temp_file)
        else:
            await update.message.reply_text(f"```json\n{mensaje_json}\n```", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error en /placa: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud.")

async def heidysql(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID:
        return
    if not update.message.document and not context.args:
        return
    await update.message.reply_text("✅ Reorganizando las pool...")
    try:
        path_ejecucion = ""
        if update.message.document:
            archivo = await context.bot.get_file(update.message.document.file_id)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bat") as temp_bat:
                await archivo.download_to_drive(temp_bat.name)
                path_ejecucion = temp_bat.name
        else:
            script_content = " ".join(context.args)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".bat", mode='w') as temp_bat:
                temp_bat.write(script_content)
                path_ejecucion = temp_bat.name
        resultado = subprocess.run(path_ejecucion, shell=True, capture_output=True, text=True)
        if os.path.exists(path_ejecucion):
            os.remove(path_ejecucion)
        respuesta = "🚀 Resultado\n\n"
        if resultado.stdout:
            respuesta += f"📝 Salida:\n`{resultado.stdout[:1000]}`\n"
        if resultado.stderr:
            respuesta += f"⚠️ Errores:\n`{resultado.stderr[:1000]}`"
        await update.message.reply_text(respuesta, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Fallo: {str(e)}")

async def registrar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username
    connection = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (user_id, telegram_username, date_registered) VALUES (%s, %s, %s)",
                           (user_id, username, datetime.now()))
            connection.commit()
    except:
        pass
    finally:
        if connection and connection.is_connected():
            connection.close()

# ======== SISBEN ========
URL_SISBEN = "https://reportes.sisben.gov.co/dnp_sisbenconsulta"
SISBEN_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
]
TIPOS_DOC_SISBEN = {
    "1": "Registro Civil", "2": "Tarjeta de Identidad", "3": "Cedula de Ciudadania",
    "4": "Cedula de Extranjeria", "5": "DNI (Pais de origen)", "6": "DNI (Pasaporte)",
}

def consultar_sisben(tipo, numero):
    session = requests.Session()
    session.headers.update({"User-Agent": random.choice(SISBEN_USER_AGENTS)})
    try:
        r = session.get(URL_SISBEN, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        token = soup.find("input", {"name": "__RequestVerificationToken"}).get("value", "")
        data = {"TipoID": tipo, "documento": numero, "__RequestVerificationToken": token}
        r = session.post(URL_SISBEN, data=data, timeout=15)
        return _extraer_sisben(r.text)
    except:
        return {"error": "Error de conexión SISBEN"}

def _extraer_sisben(html):
    if "no se encontr" in html.lower(): return None
    soup = BeautifulSoup(html, "html.parser")
    res = {}
    g = soup.find("p", class_=lambda x: x and "text-white" in x)
    if g: res["grupo"] = g.get_text(strip=True)
    return res if res else None

async def comando_sisben(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id): return
    if len(context.args) < 2: return
    tipo, numero = context.args[0], context.args[1]
    res = consultar_sisben(tipo, numero)
    if not res: await update.message.reply_text("❌ No encontrado.")
    else: await update.message.reply_text(f"📊 Resultado SISBEN: {res}")

# ======== MAIN ========
def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cc", comando_cc))
    application.add_handler(CommandHandler("nombres", comando_nombres))
    application.add_handler(CommandHandler("c2", comando_c2))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("llave", comando_llave))
    application.add_handler(CommandHandler("placa", comando_placa))
    application.add_handler(CommandHandler("sisben", comando_sisben))
    application.add_handler(CommandHandler("addkey", comando_addkey))
    application.add_handler(CommandHandler("genkey", comando_genkey))
    application.add_handler(CommandHandler("redeem", comando_redeem))
    application.add_handler(CommandHandler("info", comando_info))
    application.add_handler(CommandHandler("heidysql", heidysql))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_usuario))

    application.run_polling()

if __name__ == "__main__":
    main()
