import os
import logging
from datetime import datetime, timedelta

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ================= LOG =================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ================= DB SIMPLE (TEMPORAL) =================
usuarios_vip = {}

def es_vip(user_id):
    if user_id in usuarios_vip:
        if usuarios_vip[user_id] > datetime.now():
            return True
    return False

def activar_vip(user_id, dias):
    expira = datetime.now() + timedelta(days=dias)
    usuarios_vip[user_id] = expira

# ================= NEQUI (BASE) =================
def consultar_nequi(numero):
    # 🔥 Aquí luego metemos API real
    return {
        "numero": numero,
        "titular": "DATOS NO DISPONIBLES (API OFF)",
        "estado": "Simulado"
    }

# ================= COMANDOS =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "╔════════════════════════════╗\n"
        "      ⚔️ SOMBRA DIGITAL ⚔️\n"
        "╚════════════════════════════╝\n\n"
        "👁 Sistema privado de consultas\n"
        "⚡ Acceso restringido\n\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "⚙️ COMANDOS\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "🔎 /nequi 300XXXXXXX\n"
        "🔑 /vip\n\n"
        "👑 Owner: @broquicalifaxx"
    )
    await update.message.reply_text(texto)

# 🔍 NEQUI
async def nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not es_vip(user_id):
        await update.message.reply_text("❌ Acceso denegado (Solo VIP)")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Uso: /nequi 3001234567")
        return

    numero = context.args[0]

    msg = await update.message.reply_text("🔍 Consultando...")

    data = consultar_nequi(numero)

    await msg.edit_text(
        f"""
✅ RESULTADO

📱 Número: {data['numero']}
👤 Titular: {data['titular']}
📊 Estado: {data['estado']}

━━━━━━━━━━━━━━━
👑 @broquicalifaxx
"""
    )

# 🔑 ACTIVAR VIP (ADMIN)
async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Solo admin")
        return

    if len(context.args) != 2:
        await update.message.reply_text("⚠️ Uso: /vip ID DIAS")
        return

    try:
        target = int(context.args[0])
        dias = int(context.args[1])
    except:
        await update.message.reply_text("❌ Datos inválidos")
        return

    activar_vip(target, dias)

    await update.message.reply_text(
        f"✅ VIP activado\n👤 {target}\n⏳ {dias} días"
    )

# ================= MAIN =================

if __name__ == "__main__":
    print("🚀 BOT CORRIENDO...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nequi", nequi))
    app.add_handler(CommandHandler("vip", vip))

    app.run_polling()