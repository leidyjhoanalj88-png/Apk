import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mysql.connector import pooling
import os, requests, logging, random
from datetime import datetime

# Configuración de Logs para ver errores en Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURACIÓN ---
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql.railway.internal"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "nabo94nabo94"),
    "database": os.getenv("DB_NAME", "ani"),
    "port": int(os.getenv("DB_PORT", "3306"))
}

# Pool de conexiones (mantiene el bot rápido)
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=10, **DB_CONFIG)
except Exception as e:
    logger.error(f"Error inicializando Pool de DB: {e}")

# --- UTILIDADES DE LIMPIEZA ---
def limpiar_texto(t):
    if not t: return "No registra"
    try:
        return str(t).encode("latin-1").decode("utf-8")
    except:
        return str(t)

# --- FUNCIONES DE API ---
def api_salud_total(cedula):
    try:
        r = requests.get(f"https://prestadores.saludtotal.com.co/api/afiliado/consultar/{cedula}", timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

def api_nequi(celular):
    # Endpoint de NequiAlpha (el que estaba vivo en tu primer bot)
    headers = {"X-Api-Key": "Z5k4Y1n4n0vS", "Content-Type": "application/json"}
    try:
        r = requests.post("https://extract.nequialpha.com/consultar", json={"telefono": str(celular)}, headers=headers, timeout=10)
        return r.json() if r.status_code == 200 else None
    except: return None

# --- COMANDOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚔️ **BOT BROQUICALI ACTIVO** ⚔️\n\n/cc [cedula] - ANI Local\n/c1 [cedula] - SaludTotal\n/nequi [cel] - Nequi Info\n/info - Mi suscripción")

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return await update.message.reply_text("Uso: /cc 12345")
    cedula = context.args[0]
    
    conn = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        res = cursor.fetchone()
        if res:
            nombre = f"{limpiar_texto(res['ANINombre1'])} {limpiar_texto(res['ANINombre2'])}"
            apellido = f"{limpiar_texto(res['ANIApellido1'])} {limpiar_texto(res['ANIApellido2'])}"
            await update.message.reply_text(f"🪪 *ANI LOCAL*\n\n👤 {nombre} {apellido}\n📅 Nacimiento: {res['ANIFchNacimiento']}\n🏠 Dir: {res.get('ANIDireccion', 'N/A')}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ No encontrado en base local.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error de base de datos: {e}")
    finally:
        if conn: conn.close()

async def comando_c1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    cedula = context.args[0]
    await update.message.reply_chat_action("typing")
    data = api_salud_total(cedula)
    if data:
        nombre = limpiar_texto(data.get('nombreCompleto'))
        await update.message.reply_text(f"🏥 *SALUD TOTAL*\n\n👤 {nombre}\n✅ Estado: {data.get('estadoAfiliacion')}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Sin resultados en SaludTotal.")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    cel = context.args[0]
    data = api_nequi(cel)
    if data:
        await update.message.reply_text(f"📱 *NEQUI INFO*\n\n👤 {data.get('nombre_completo')}\n🆔 CC: {data.get('cedula')}\n📍 Ciudad: {data.get('municipio')}", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ No se encontró el número.")

# --- EJECUCIÓN ---
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("c1", comando_c1))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    
    print("Bot encendido. Revisa los logs en Railway.")
    app.run_polling()
