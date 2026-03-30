import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mysql.connector import pooling
import os, requests, json, random, string, logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# ======== CONFIGURACIÓN CRÍTICA ========
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")
OWNER_ID = 8114050673
OWNER_USER = "@Broquicalifoxx"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql.railway.internal"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "nabo94nabo94"),
    "database": os.getenv("DB_NAME", "ani"),
    "port": int(os.getenv("DB_PORT", "3306"))
}

# APIs endpoints
API_HEXN = "https://par-bottles-straight-bernard.trycloudflare.com/hexn-dox-api"
API_NEQUI = "https://extract.nequialpha.com/consultar"
API_C2 = "https://extract.nequialpha.com/doxing"

# Pool de conexiones (Evita caídas en Render)
try:
    pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="broqui_pool", pool_size=10, **DB_CONFIG
    )
except Exception as e:
    print(f"❌ ERROR DE CONEXIÓN DB: {e}")

# ======== VALIDACIÓN DE ACCESO ========
def tiene_permiso(user_id):
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

# ======== COMANDOS DE FLUJO COMPLETO ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "⚔️ **𝐈𝐍𝐅𝐄𝐑𝐍𝐎 𝐃𝐎𝐗 𝐒𝐘𝐒𝐓𝐄𝐌** ⚔️\n"
        "═════════════════════════\n"
        "👤 /cc `<num>` ➛ 𝐂𝐄𝐃𝐔𝐋𝐀 (𝐃𝐁 + 𝐀𝐏𝐈)\n"
        "📱 /nequi `<tel>` ➛ 𝐍𝐄𝐐𝐔𝐈 𝐅𝐔𝐋𝐋 𝐃𝐀𝐓𝐀\n"
        "📄 /c2 `<num>` ➛ 𝐄𝐗𝐓𝐑𝐀𝐂𝐓 𝐂𝟐\n"
        "📊 /sisben `<tipo> <num>` ➛ 𝐒𝐈𝐒𝐁𝐄𝐍 𝐈𝐕\n"
        "🔑 /redeem `<key>` ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐀𝐂𝐂𝐄𝐒𝐎\n"
        "⚙️ /gen `<dias>` ➛ 𝐆𝐄𝐍𝐄𝐑𝐀𝐑 𝐊𝐄𝐘 (𝐀𝐃𝐌𝐈𝐍)\n"
        "═════════════════════════\n"
        f"👑 **Owner:** {OWNER_USER}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    if not tiene_permiso(uid):
        await update.message.reply_text("❌ **ACCESO DENEGADO.** Compra tu key con @Broquicalifoxx")
        return
    
    if not context.args:
        await update.message.reply_text("📌 Uso: `/cc <cedula>`")
        return

    cc = context.args[0]
    wait = await update.message.reply_text(f"📡 **Consultando registros para:** `{cc}`...")

    # 1. Búsqueda en DB Local (ANI)
    db_res = None
    try:
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cc,))
        db_res = cursor.fetchone()
        conn.close()
    except: pass

    # 2. Búsqueda en API Cloudflare (JSON)
    api_res = None
    try:
        r = requests.get(f"{API_HEXN}?cc={cc}", timeout=10)
        api_res = r.json()
    except: pass

    if db_res or api_res:
        # Lógica de mapeo inteligente para evitar el "N/A"
        nom1 = (db_res.get('ANINombre1') if db_res else None) or (api_res.get('nombre') if api_res else "No registra")
        ape1 = (db_res.get('ANIApellido1') if db_res else "") or (api_res.get('apellido') if api_res else "")
        
        res_msg = (
            "⚔️ **RESULTADO ENCONTRADO** ⚔️\n"
            "═════════════════════════\n"
            f"👤 **NOMBRES:** `{nom1} {db_res.get('ANINombre2','') if db_res else ''}`\n"
            f"👤 **APELLIDOS:** `{ape1} {db_res.get('ANIApellido2','') if db_res else ''}`\n"
            f"🆔 **DOCUMENTO:** `{cc}`\n"
            f"📅 **NACIMIENTO:** `{db_res.get('ANIFchNacimiento','N/A') if db_res else 'N/A'}`\n"
            f"🏠 **DIRECCIÓN:** `{db_res.get('ANIDireccion','No registra') if db_res else 'No registra'}`\n"
            "═════════════════════════\n"
            f"💻 **By:** {OWNER_USER}"
        )
        await wait.edit_text(res_msg, parse_mode="Markdown")
    else:
        await wait.edit_text("💀 **ERROR:** No se encontró rastro del objetivo.")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_permiso(update.message.from_user.id): return
    if not context.args: return
    
    tel = context.args[0]
    wait = await update.message.reply_text(f"📱 **Extrayendo Nequi:** `{tel}`...")

    try:
        # Corregido: Headers y método POST para evitar N/A
        headers = {"X-Api-Key": "Z5k4Y1n4n0vS", "Content-Type": "application/json"}
        r = requests.post(API_NEQUI, json={"telefono": tel}, headers=headers, timeout=12)
        data = r.json()

        # Mapeo de campos dinámico
        nombre = data.get('nombre_completo') or data.get('nombre') or "No registra"
        cedula = data.get('cedula') or data.get('documento') or "No registra"

        res = (
            "📱 **𝐃𝐀𝐓𝐎𝐒 𝐍𝐄𝐐𝐔𝐈**\n"
            "═════════════════════════\n"
            f"👤 **TITULAR:** `{nombre}`\n"
            f"🆔 **CÉDULA:** `{cedula}`\n"
            f"📍 **CIUDAD:** `{data.get('municipio', 'No registra')}`\n"
            "═════════════════════════"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except Exception as e:
        await wait.edit_text(f"❌ **ERROR API:** Los servidores de Nequi no responden.")

async def gen_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    if not context.args:
        await update.message.reply_text("🔑 `/gen <dias>`")
        return
    
    dias = int(context.args[0])
    key = "INFERNO-" + "".join(random.choices(string.ascii_upper + string.digits, k=8))
    
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_keys (key_value, duration_days, redeemed) VALUES (%s, %s, FALSE)", (key, dias))
        conn.commit()
        await update.message.reply_text(f"🔑 **NUEVA KEY:** `{key}`\n⏳ **VALIDEZ:** `{dias} DÍAS`")
    finally: conn.close()

async def comando_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    key = context.args[0]
    uid = update.message.from_user.id
    
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_keys WHERE key_value = %s AND redeemed = FALSE", (key,))
        res = cursor.fetchone()
        if res:
            exp = datetime.now() + timedelta(days=res['duration_days'])
            cursor.execute("UPDATE user_keys SET redeemed=TRUE, user_id=%s, expiration_date=%s WHERE key_value=%s", (uid, exp, key))
            conn.commit()
            await update.message.reply_text(f"✅ **Suscripción Activada.**\n📅 Vence: `{exp.date()}`")
        else:
            await update.message.reply_text("❌ Key inválida o ya usada.")
    finally: conn.close()

# ======== LANZAMIENTO ========

def main():
    app = Application.builder().token(TOKEN).build()

    # Registro de comandos con su flujo asignado
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("gen", gen_key))
    app.add_handler(CommandHandler("redeem", comando_redeem))

    print("🚀 INFERNO-BOT OPERATIVO")
    app.run_polling()

if __name__ == "__main__":
    main()
