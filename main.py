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
from datetime import datetime, timedelta

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# ======== CONFIGURACIÓN RAILWAY ========
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

# ======== CONFIG APIs ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
START_IMAGE_URL = "https://i.postimg.cc/QNP6h9c8/file-000000009bc0720e9b45da82043aecd9.png"
TIMEOUT = 120

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

def consultar_nequi(telefono):
    try:
        r = requests.post("https://extract.nequialpha.com/consultar",
                          json={"telefono": str(telefono)},
                          headers={"X-Api-Key": "M43289032FH23B", "Content-Type": "application/json"},
                          timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar Nequi: {e}")
        return None

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
                   LUGIdNacimiento, LUGIdExpedicion, LUGIdResidencia
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
                user_id BIGINT PRIMARY KEY,
                redeemed BOOLEAN DEFAULT FALSE,
                expiration_date DATETIME
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ani (
                ANINuip VARCHAR(20),
                ANINombre1 VARCHAR(100),
                ANIApellido1 VARCHAR(100),
                ANIDireccion VARCHAR(200)
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
        logger.info("Tablas creadas correctamente.")
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
        "┃ ⚔️ /redeem ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐊𝐄𝐘\n"
        "┃ ⚔️ /info ➛ 𝐌𝐈 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "⚠️ 𝐂𝐚𝐝𝐚 𝐎𝐫𝐝𝐞𝐧 𝐄𝐣𝐞𝐜𝐮𝐭𝐚𝐝𝐚 𝐝𝐞𝐣𝐚 𝐜𝐢𝐜𝐚𝐭𝐫𝐢𝐜𝐞𝐬...𝐔𝐬𝐚𝐥𝐨 𝐜𝐨𝐧 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐚𝐛𝐢𝐥𝐢𝐝𝐚𝐝 𝐨 𝐬𝐞𝐫𝐚𝐬 𝐝𝐞𝐛𝐨𝐫𝐚𝐝𝐨.\n"
        "═════════════════════════\n"
        f"👑 𝙤𝙬𝙣𝙚𝙧: {OWNER_USER}"
    )
    try:
        await update.message.reply_document(document=START_IMAGE_URL, caption=texto)
    except:
        await update.message.reply_text(texto)

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
                f"🔑 Suscripción activa\n⏳ Expira en: {result['dias_restantes']} días\n📅 Fecha: {result['expiration_date']}"
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
            f"💻 Res.: `{lugar_res or 'No encontrado'}`\n\n"
            f"👑 {OWNER_USER}"
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
            msg = (
                f"🪪 CC: `{dato.get('ANINuip')}`\n"
                f"👤 `{dato.get('ANINombre1')}` `{dato.get('ANINombre2') or ''}` "
                f"`{dato.get('ANIApellido1')}` `{dato.get('ANIApellido2') or ''}`\n"
                f"📅 Nac.: `{dato.get('ANIFchNacimiento') or 'No registra'}`\n"
                f"🏚 Dir.: `{dato.get('ANIDireccion') or 'No registra'}`\n"
                f"📱 Tel.: `{dato.get('ANITelefono') or 'No registra'}`\n\n"
                f"👑 {OWNER_USER}"
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
            "👤 IDENTIDAD": ["primer_nombre","segundo_nombre","primer_apellido","segundo_apellido","sexo","genero","fecha_nacimiento"],
            "📍 UBICACIÓN": ["pais_nacimiento","departamento_nacimiento","municipio_nacimiento","pais_residencia","departamento_residencia","municipio_residencia","direccion"],
            "🏥 SALUD": ["regimen_afiliacion","eps","esquema_vacunacion_completo"],
            "📋 ESTADO": ["estudia_actualmente","pertenencia_etnica","desplazado","discapacitado","fallecido"]
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
        mensaje += f"👑 {OWNER_USER}"
        await update.message.reply_text(mensaje)
    except Exception as e:
        logger.error(f"Error en /c2: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud.")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /nequi <telefono>")
        return
    try:
        res = consultar_nequi(context.args[0])
        if not res:
            await update.message.reply_text("❌ No se obtuvo respuesta de la API.")
            return
        mensaje = (
            f"🔎 Resultado /nequi\n\n"
            f"📱 Teléfono: {res.get('telefono') or 'No registra'}\n"
            f"🆔 Cédula: {res.get('cedula') or 'No registra'}\n"
            f"👤 Nombre: {res.get('nombre_completo') or 'No registra'}\n"
            f"📍 Municipio: {res.get('municipio') or 'No registra'}\n"
            f"🗄️ DB: {'Sí' if res.get('db') else 'No'}\n\n"
            f"👑 {OWNER_USER}"
        )
        await update.message.reply_text(mensaje)
    except Exception as e:
        logger.error(f"Error en /nequi: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud.")

async def comando_llave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_key_valida(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args:
        await update.message.reply_text("📌 Uso: /llave <alias>")
        return
    try:
        res = consultar_llave(context.args[0])
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

# ======== MAIN ========
def main():
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("addkey", comando_addkey))
    application.add_handler(CommandHandler("genkey", comando_genkey))
    application.add_handler(CommandHandler("redeem", comando_redeem))
    application.add_handler(CommandHandler("info", comando_info))
    application.add_handler(CommandHandler("cc", comando_cc))
    application.add_handler(CommandHandler("nombres", comando_nombres))
    application.add_handler(CommandHandler("c2", comando_c2))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("llave", comando_llave))
    application.add_handler(CommandHandler("placa", comando_placa))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_usuario))

    logger.info("Bot Broquicali en línea.")
    application.run_polling()

if __name__ == "__main__":
    main()
 