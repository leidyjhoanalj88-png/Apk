import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# ============== LÓGICA ===================
class NequiConsultor:
    def consultar(self, numero):
        return f"Consulta simulada para {numero}"

# ============== BOT ===================
bot_nequi = NequiConsultor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot Nequi activo\n\nUsa:\n/nequi 3001234567"
    )

async def nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ No tienes acceso")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usa: /nequi 3001234567")
        return

    numero = context.args[0]

    await update.message.reply_text(f"🔍 Consultando {numero}...")

    resultado = bot_nequi.consultar(numero)

    await update.message.reply_text(f"👤 Titular:\n{resultado}")

# ============== MAIN ===================
if __name__ == "__main__":
    print("🚀 Bot corriendo...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nequi", nequi))

    app.run_polling()