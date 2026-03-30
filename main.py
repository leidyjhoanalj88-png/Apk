import mysql.connector
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from mysql.connector import pooling
import os, requests, json, random, string, logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

# ======== CONFIGURACIÓN MAESTRA ========
TOKEN = os.getenv("TELEGRAM_TOKEN", "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU")
OWNER_ID = 8114050673
OWNER_USER = "@Broquicalifoxx"

# Configuración de Base de Datos
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "mysql.railway.internal"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "nabo94nabo94"),
    "database": os.getenv("DB_NAME", "ani"),
    "port": int(os.getenv("DB_PORT", "3306"))
}

# APIs y Túneles JSON
API_HEXN = "https://par-bottles-straight-bernard.trycloudflare.com/hexn-dox-api"
API_NEQUI = "https://extract.nequialpha.com/consultar"
API_C2 = "https://extract.nequialpha.com/doxing"
API_PLACA = "https://alex-bookmark-univ-survival.trycloudflare.com/index.php"

# ======== CONEXIÓN POOLING ========
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="infierno_pool", pool_size=20, **DB_CONFIG
)

# ======== FUNCIONES DE SEGURIDAD Y DB ========

def check_access(user_id):
    if user_id == OWNER_ID: return True
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM user_keys WHERE user_id = %s AND redeemed = TRUE AND expiration_date > NOW()", (user_id,))
        return cursor.fetchone() is not None
    finally: conn.close()

def get_ani_data(cedula):
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM ani WHERE ANINuip = %s", (cedula,))
        return cursor.fetchone()
    finally: conn.close()

# ======== COMANDOS DE ADMINISTRACIÓN (ADMIN ONLY) ========

async def gen_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != OWNER_ID: return
    if not context.args: return
    dias = int(context.args[0])
    key = "BROQUI-" + "".join(random.choices(string.ascii_upper + string.digits, k=10))
    conn = pool.get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO user_keys (key_value, duration_days, redeemed) VALUES (%s, %s, FALSE)", (key, dias))
        conn.commit()
        await update.message.reply_text(f"🔑 **KEY GENERADA:** `{key}`\n⏳ **Días:** `{dias}`")
    finally: conn.close()

# ======== COMANDOS DE USUARIO (EL MENÚ) ========

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = (
        "⚔️ **𝐈𝐍𝐅𝐄𝐑𝐍𝐎 𝐃𝐎𝐗 𝐕𝐈𝐏** ⚔️\n"
        "═════════════════════════\n"
        "👤 /cc `<num>` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝐄𝐃𝐔𝐋𝐀 (𝐃𝐁+𝐀𝐏𝐈)\n"
        "📱 /nequi `<tel>` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐍𝐄𝐐𝐔𝐈 𝐉𝐒𝐎𝐍\n"
        "📄 /c2 `<num>` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐂𝟐 𝐄𝐗𝐓𝐑𝐀𝐂𝐓\n"
        "🚗 /placa `<placa>` ➛ 𝐂𝐎𝐍𝐒𝐔𝐋𝐓𝐀 𝐑𝐔𝐍𝐓\n"
        "📊 /sisben `<tipo> <num>` ➛ 𝐒𝐈𝐒𝐁𝐄𝐍 𝐈𝐕\n"
        "🔑 /redeem `<key>` ➛ 𝐀𝐂𝐓𝐈𝐕𝐀𝐑 𝐒𝐔𝐒𝐂𝐑𝐈𝐏𝐂𝐈Ó𝐍\n"
        "ℹ️ /info ➛ 𝐄𝐒𝐓𝐀𝐃𝐎 𝐃𝐄 𝐌𝐈 𝐊𝐄𝐘\n"
        "═════════════════════════\n"
        f"👑 **Owner:** {OWNER_USER}"
    )
    await update.message.reply_text(menu, parse_mode="Markdown")

async def comando_cc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.message.from_user.id):
        await update.message.reply_text("❌ Sin Key activa.")
        return
    if not context.args: return
    cc = context.args[0]
    m = await update.message.reply_text(f"🔎 **Buscando:** `{cc}`...")

    db = get_ani_data(cc)
    try: api = requests.get(f"{API_HEXN}?cc={cc}", timeout=12).json()
    except: api = None

    if db or api:
        nombre = (db.get('ANINombre1') if db else None) or (api.get('nombre') if api else "No registra")
        res = (
            "⚔️ **DATOS ENCONTRADOS** ⚔️\n"
            f"👤 **Nombre:** `{nombre} {db.get('ANINombre2','') if db else ''}`\n"
            f"👤 **Apellidos:** `{db.get('ANIApellido1','') if db else ''} {db.get('ANIApellido2','') if db else ''}`\n"
            f"🆔 **CC:** `{cc}`\n"
            f"📅 **Nacimiento:** `{db.get('ANIFchNacimiento','N/A') if db else 'N/A'}`\n"
            f"🏠 **Dirección:** `{db.get('ANIDireccion','No registra') if db else 'No registra'}`\n"
            "═════════════════════════"
        )
        await m.edit_text(res, parse_mode="Markdown")
    else: await m.edit_text("💀 Sin registros.")

async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update.message.from_user.id): return
    if not context.args: return
    tel = context.args[0]
    m = await update.message.reply_text(f"📱 **Nequi Check:** `{tel}`...")
    try:
        r = requests.post(API_NEQUI, json={"telefono": tel}, headers={"X-Api-Key": "Z5k4Y1n4n0vS"}, timeout=12).json()
        res = (
            "📱 **RESULTADO NEQUI**\n"
            f"👤 **Nombre:** `{r.get('nombre_completo', 'N/A')}`\n"
            f"🆔 **CC:** `{r.get('cedula', 'N/A')}`\n"
            "═════════════════════════"
        )
        await m.edit_text(res, parse_mode="Markdown")
    except: await m.edit_text("❌ Error API Nequi.")

async def comando_redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args: return
    key, uid = context.args[0], update.message.from_user.id
    conn = pool.get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_keys WHERE key_value = %s AND redeemed = FALSE", (key,))
        res = cursor.fetchone()
        if res:
            exp = datetime.now() + timedelta(days=res['duration_days'])
            cursor.execute("UPDATE user_keys SET redeemed=TRUE, user_id=%s, expiration_date=%s WHERE key_value=%s", (uid, exp, key))
            conn.commit()
            await update.message.reply_text(f"✅ **KEY ACTIVADA**\n📅 Expira: `{exp.date()}`")
        else: await update.message.reply_text("❌ Key inválida.")
    finally: conn.close()

# ======== INICIO DE LA APLICACIÓN ========

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Registro de todos los comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen_key))
    app.add_handler(CommandHandler("cc", comando_cc))
    app.add_handler(CommandHandler("nequi", comando_nequi))
    app.add_handler(CommandHandler("redeem", comando_redeem))
    app.add_handler(CommandHandler("info", lambda u, c: u.message.reply_text("Usa /redeem para activar.")))

    print("🔥 INFERNO-BOT ONLINE EN RENDER")
    app.run_polling()

if __name__ == "__main__":
    main()
