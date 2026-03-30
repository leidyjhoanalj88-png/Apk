import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mysql.connector import pooling
import logging
import os
import requests
import json
from dotenv import load_dotenv

# Cargar configuración
load_dotenv()

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
START_IMAGE = os.getenv("START_IMAGE_URL", "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg")

# APIs
API_NEQUI = "https://extract.nequialpha.com/consultar"
API_C2 = "https://extract.nequialpha.com/doxing"
API_EXT = "https://par-bottles-straight-bernard.trycloudflare.com/hexn-dox-api"
API_PLACA = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"

# ======== CONEXIÓN DB ========
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="califoxx_pool", pool_size=12, host=DB_HOST,
        user=DB_USER, password=DB_PASS, database=DB_NAME,
        port=int(DB_PORT), charset="utf8"
    )
    logger.info("✅ Conexión establecida con la base de datos de CALIFOXX")
except Exception as e:
    logger.error(f"❌ Error de DB (Revisa Railway): {e}")
    pool = None

# ======== SEGURIDAD DE ACCESO ========
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

# ======== COMANDOS ESTILO BROQUICALIFOXX ========

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
    await update.message.reply_photo(photo=START_IMAGE, caption=msg, parse_mode="Markdown")

async def nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.message.from_user.id):
        await update.message.reply_text("❌ **ACCESO DENEGADO**\nNecesitas una suscripción activa.", parse_mode="Markdown")
        return
    if not context.args:
        await update.message.reply_text("📌 **Uso:** `/nequi <número>`", parse_mode="Markdown")
        return
    
    num = context.args[0]
    wait = await update.message.reply_text(f"⏳ **Buscando:** `{num}`...", parse_mode="Markdown")
    
    try:
        r = requests.post(API_NEQUI, json={"telefono": num}, headers={"X-Api-Key": "Z5k4Y1n4n0vS"}, timeout=15).json()
        nombre = r.get('nombre_completo') or r.get('nombre') or "No registra"
        cedula = r.get('cedula') or "No registra"
        
        res = (
            "📱 **RESULTADO NEQUI**\n"
            "═════════════════════════\n"
            f"👤 **NOMBRE:** `{nombre}`\n"
            f"🆔 **CÉDULA:** `{cedula}`\n"
            f"📞 **TEL:** `{num}`\n"
            "═════════════════════════\n"
            f"💻 By {OWNER_USER}"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except:
        await wait.edit_text("❌ Error al conectar con el servidor de Nequi.")

async def ext(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.message.from_user.id): return
    if not context.args: return
    
    cc = context.args[0]
    wait = await update.message.reply_text(f"🔎 **Consultando Extranjero:** `{cc}`...", parse_mode="Markdown")
    
    try:
        r = requests.get(API_EXT, params={"cc": cc}, timeout=15).json()
        if r.get("Estado") == "OK":
            id_i = r.get('IDENTIDAD', {})
            salud = r.get('SALUD', {})
            res = (
                "🇻🇪 **DATOS MIGRACIÓN / EXTRANJERO**\n"
                "═════════════════════════\n"
                f"👤 **NOMBRE:** `{id_i.get('Primer Nombre')} {id_i.get('Primer Apellido')}`\n"
                f"🆔 **DOC:** `{r.get('Documento')}`\n"
                f"⚧ **SEXO:** `{id_i.get('Sexo')}`\n"
                f"🏥 **EPS:** `{salud.get('Regimen Afiliacion')}`\n"
                "═════════════════════════\n"
                f"💻 By {OWNER_USER}"
            )
            await wait.edit_text(res, parse_mode="Markdown")
        else:
            await wait.edit_text("❌ No se encontró información migratoria.")
    except:
        await wait.edit_text("❌ API Extranjero Offline.")

# ======== LANZAMIENTO ========
def main():
    if not TOKEN:
        print("❌ FALTA TELEGRAM_TOKEN EN .ENV")
        return

    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nequi", nequi))
    app.add_handler(CommandHandler("ext", ext))
    # Agregar aquí los demás comandos con la misma lógica...

    print(f"🚀 {OWNER_USER} BOT IS LIVE ON RENDER")
    app.run_polling()

if __name__ == "__main__":
    main()
