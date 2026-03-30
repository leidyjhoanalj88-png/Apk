import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mysql.connector import pooling
import logging
import os
import requests
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

# Configuración de Logs para Render
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ======== VARIABLES DEL .ENV ========
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "8114050673"))
OWNER_USER = os.getenv("OWNER_USER", "@Broquicalifoxx")
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = os.getenv("DB_PORT", "3306")
START_IMG = os.getenv("START_IMAGE_URL")
# Cambia esta Key si sigue saliendo "No registra"
NEQUI_KEY = os.getenv("NEQUI_API_KEY", "Z5k4Y1n4n0vS") 

# ======== POOL DE BASE DE DATOS ========
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="califoxx_pool", pool_size=15, host=DB_HOST,
        user=DB_USER, password=DB_PASS, database=DB_NAME,
        port=int(DB_PORT), charset="utf8", connect_timeout=10
    )
    logger.info("✅ DB CALIFOXX CONECTADA")
except Exception as e:
    logger.error(f"❌ ERROR DB: {e}")
    pool = None

# ======== SEGURIDAD ========
def check_access(user_id):
    if user_id == OWNER_ID: return True
    if not pool: return False
    try:
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        res = cursor.fetchone()
        conn.close()
        return res is not None
    except: return False

# ======== COMANDOS REPLICADOS ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "⚔️ **COLOMBIA ELITE BOT** ⚔️\n"
        "═════════════════════════\n"
        "⚡️ `/cc` ➛ Consulta Cédula V1\n"
        "⚡️ `/c2` ➛ Consulta Cédula V2\n"
        "⚡️ `/ext` ➛ Consulta Extranjero\n"
        "⚡️ `/nequi` ➛ Consulta Nequi\n"
        "⚡️ `/placa` ➛ Consulta Vehicular\n"
        "⚡️ `/llave` ➛ Consulta Alias\n"
        "⚡️ `/sisben` ➛ Consulta Sisben IV\n"
        "⚡️ `/info` ➛ Estado de suscripción\n"
        "═════════════════════════\n"
        f"👤 **ADMIN:** {OWNER_USER}\n"
        "📍 **ESTADO:** `ACTIVO 🟢`"
    )
    if START_IMG:
        await update.message.reply_photo(photo=START_IMG, caption=msg, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg, parse_mode="Markdown")

async def nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.message.from_user.id):
        await update.message.reply_text("❌ **ACCESO DENEGADO**", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("📌 ` /nequi <número>`", parse_mode="Markdown")
        return
    
    num = context.args[0]
    wait = await update.message.reply_text(f"⏳ **Buscando en Nequi:** `{num}`...")
    
    try:
        # API de Nequi
        r = requests.post("https://extract.nequialpha.com/consultar", 
                          json={"telefono": num}, 
                          headers={"X-Api-Key": NEQUI_KEY}, 
                          timeout=15).json()
        
        nombre = r.get('nombre_completo') or r.get('nombre') or "No registra"
        cedula = r.get('cedula') or "No registra"
        
        res = (
            "📱 **RESULTADO NEQUI**\n"
            "═════════════════════════\n"
            f"👤 **NOMBRE:** `{nombre.upper()}`\n"
            f"🆔 **CÉDULA:** `{cedula}`\n"
            f"📞 **TEL:** `{num}`\n"
            "═════════════════════════\n"
            f"💻 By {OWNER_USER}"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except:
        await wait.edit_text("❌ Error: API Nequi caída o Key vencida.")

async def placa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.message.from_user.id): return
    if not context.args: return
    p = context.args[0].upper()
    wait = await update.message.reply_text(f"🚗 **Buscando Placa:** `{p}`...")
    try:
        r = requests.get(f"https://alex-bookmark-univ-survival.trycloudflare.com/index.php?placa={p}", timeout=15).json()
        res = (
            f"🚗 **RESULTADO PLACA [{p}]**\n"
            "═════════════════════════\n"
            f"👤 **DUEÑO:** `{r.get('propietario', 'No registra')}`\n"
            f"🆔 **DOC:** `{r.get('documento', 'No registra')}`\n"
            f"🚙 **MARCA:** `{r.get('marca', 'No registra')}`\n"
            "═════════════════════════"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except: await wait.edit_text("❌ Error API Placas.")

# ======== REGISTRO DE TODOS LOS COMANDOS ========
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nequi", nequi))
    app.add_handler(CommandHandler("placa", placa))
    # Aquí puedes añadir los de /cc, /c2, /ext con la misma lógica
    
    print("🚀 BOT DE BROQUICALIFOXX OPERATIVO")
    app.run_polling()

if __name__ == "__main__":
    main()
