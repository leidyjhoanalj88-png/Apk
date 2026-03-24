import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

# 👉 Lista dinámica en memoria
usuarios_permitidos = {ADMIN_ID}

# ============== LÓGICA ===================
class NequiConsultor:
    def consultar(self, numero):
        return f"Consulta simulada para {numero}"

bot_nequi = NequiConsultor()

# ============== COMANDOS ===================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 Bot activo\n\n"
        "Comandos:\n"
        "/nequi 3001234567\n"
        "/adduser ID\n"
        "/deluser ID\n"
        "/listusers"
    )

async def nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in usuarios_permitidos:
        await update.message.reply_text("❌ No tienes acceso")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usa: /nequi 3001234567")
        return

    numero = context.args[0]

    await update.message.reply_text(f"🔍 Consultando {numero}...")
    resultado = bot_nequi.consultar(numero)
    await update.message.reply_text(f"👤 Titular:\n{resultado}")

# 👉 AGREGAR USUARIO
async def adduser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Solo admin")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usa: /adduser 123456789")
        return

    new_id = int(context.args[0])
    usuarios_permitidos.add(new_id)

    await update.message.reply_text(f"✅ Usuario {new_id} agregado")

# 👉 ELIMINAR USUARIO
async def deluser(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Solo admin")
        return

    if not context.args:
        await update.message.reply_text("⚠️ Usa: /deluser 123456789")
        return

    rem_id = int(context.args[0])
    usuarios_permitidos.discard(rem_id)

    await update.message.reply_text(f"🗑 Usuario {rem_id} eliminado")

# 👉 LISTAR USUARIOS
async def listusers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ Solo admin")
        return

    lista = "\n".join(str(u) for u in usuarios_permitidos)
    await update.message.reply_text(f"👥 Usuarios:\n{lista}")

# ============== MAIN ===================
if __name__ == "__main__":
    print("🚀 Bot corriendo...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nequi", nequi))
    app.add_handler(CommandHandler("adduser", adduser))
    app.add_handler(CommandHandler("deluser", deluser))
    app.add_handler(CommandHandler("listusers", listusers))

    app.run_polling()