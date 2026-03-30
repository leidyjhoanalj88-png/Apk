
import logging
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ======== CONFIGURACIÓN ========
TOKEN = "8110478941:AAE2k8t6tScXViG9DX7nBviqcVocWbpWbmU"
# URLs de APIs
API_URL_C2 = "https://extract.nequialpha.com/doxing"
API_NEQUI = "https://extract.nequialpha.com/consultar"
START_IMAGE_URL = "https://i.postimg.cc/xTbPbYFN/photo-2026-01-29-18-20-26.jpg"

# Logging (para ver errores en la terminal)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ======== COMANDO /START (EL QUE FALLABA) ========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = (
        "乄 **𝐈𝐍𝐅𝐄𝐑𝐍𝐎 𝐒𝐘𝐒𝐓𝐄𝐌** ⚔️\n"
        "═════════════════════════\n"
        "𝐁𝐢𝐞𝐧𝐯𝐞𝐧𝐢𝐝𝐨 𝐚𝐥 𝐢𝐧𝐟𝐢𝐞𝐫𝐧𝐨 𝐝𝐢𝐠𝐢𝐭𝐚𝐥... 𝐚𝐜𝐚 𝐧𝐨 𝐡𝐚𝐲 𝐫𝐞𝐠𝐥𝐚𝐬.\n"
        "═════════════════════════\n"
        "👤 `/cc` ➛ 𝐂𝐄𝐃𝐔𝐋𝐀 (𝐃𝐁)\n"
        "📄 `/c2` ➛ 𝐃𝐎𝐗𝐈𝐍𝐆 𝐂𝟐\n"
        "📱 `/nequi` ➛ 𝐍𝐄𝐐𝐔𝐈\n"
        "═════════════════════════\n"
        "👑 **Owner:** @Broquicalifoxx"
    )
    # Primero intentamos enviar la imagen, si falla enviamos solo el texto
    try:
        await update.message.reply_photo(photo=START_IMAGE_URL, caption=texto, parse_mode="Markdown")
    except Exception:
        await update.message.reply_text(texto, parse_mode="Markdown")

# ======== COMANDO /C2 (CON TU JSON ADAPTADO) ========
async def comando_c2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("📌 Uso: `/c2 <documento>`")
        return
    
    doc = context.args[0]
    wait = await update.message.reply_text(f"🔍 Investigando: `{doc}`...")

    try:
        r = requests.post(API_URL_C2, json={"cedula": str(doc)}, timeout=15)
        data = r.json()
        
        # Entramos a la estructura IDENTIDAD del JSON que me pasaste
        ide = data.get("IDENTIDAD", {})
        
        res = (
            "📄 **𝐑𝐄𝐒𝐔𝐋𝐓𝐀𝐃𝐎 𝐂𝟐**\n"
            "═════════════════════════\n"
            f"👤 **Nombre:** `{ide.get('Primer Nombre')} {ide.get('Segundo Nombre', '')}`\n"
            f"👤 **Apellidos:** `{ide.get('Primer Apellido')} {ide.get('Segundo Apellido', '')}`\n"
            f"🆔 **DOC:** `{data.get('Documento')}`\n"
            f"📅 **Nacimiento:** `{ide.get('Fecha Nacimiento')}`\n"
            "═════════════════════════"
        )
        await wait.edit_text(res, parse_mode="Markdown")
    except Exception as e:
        await wait.edit_text(f"❌ Error en API C2: `{e}`")

# ======== ENCENDIDO DEL BOT ========
def main():
    # Iniciamos la app con tu token
    application = Application.builder().token(TOKEN).build()

    # REGISTRAMOS LOS COMANDOS
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("c2", comando_c2))

    print("--- BOT ENCENDIDO ---")
    application.run_polling()

if __name__ == "__main__":
    main()
