import os
import logging
import asyncio
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

# ================= DB SIMPLE =================
usuarios_vip = {}

def es_vip(user_id):
    if user_id == ADMIN_ID:
        return True
    if user_id in usuarios_vip:
        if usuarios_vip[user_id] > datetime.now():
            return True
    return False

def activar_vip(user_id, dias):
    expira = datetime.now() + timedelta(days=dias)
    usuarios_vip[user_id] = expira

# ================= MULTI API (NO BLOQUEANTE) =================
def consultar_nequi(numero):
    import requests

    apis = [
        {
            "url": "https://extract.nequialpha.com/consultar",
            "headers": {
                "X-Api-Key": "M43289032FH23B",
                "Content-Type": "application/json"
            },
            "payload": {"telefono": str(numero)},
        }
    ]

    for api in apis:
        try:
            r = requests.post(
                api["url"],
                json=api["payload"],
                headers=api["headers"],
                timeout=5  # 🔥 evita que se congele
            )

            if r.status_code == 200:
                try:
                    data = r.json()
                except:
                    continue

                nombre = data.get("nombre") or data.get("titular")

                if nombre:
                    return {
                        "numero": numero,
                        "titular": nombre,
                        "estado": "OK"
                    }

        except:
            continue

    return {
        "numero": numero,
        "titular": "No disponible",
        "estado": "Sistema protegido"
    }

# ================= COMANDOS =================

# 🔥 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nombre = update.effective_user.first_name

    texto = f"""
╔══════════════════════════════╗
      ⚔️ SISTEMA OSCURO ⚔️
╚══════════════════════════════╝

🧠 Inicializando núcleo…
📡 Conectando nodos ocultos…

━━━━━━━━━━━━━━━━━━━━━━━
👁 Usuario: {nombre}
🧬 Estado: MONITOREADO
💀 Modo: SIGILOSO
━━━━━━━━━━━━━━━━━━━━━━━

⚔️ COMANDOS

🔎 /nequi ➛ Extraer información
🔑 /vip ➛ Activar acceso
📊 /miacceso ➛ Estado VIP

━━━━━━━━━━━━━━━━━━━━━━━
⚠️ Sistema protegido
👁 Actividad registrada

👑 @Broquicalifoxx
"""
    await update.message.reply_text(texto)

# 🔍 NEQUI (ANTI FREEZE REAL)
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

    try:
        # 🔥 ejecuta sin bloquear el bot
        data = await asyncio.to_thread(consultar_nequi, numero)
    except:
        data = {
            "numero": numero,
            "titular": "No disponible",
            "estado": "Sistema protegido"
        }

    await msg.edit_text(
        f"""
╔══════════════════════════════╗
        🔎 RESULTADO 🔎
╚══════════════════════════════╝

📡 Consulta ejecutada
🧠 Datos procesados

━━━━━━━━━━━━━━━━━━━━━━━
📱 Número: {data['numero']}
👤 Titular: {data['titular']}
📊 Estado: {data['estado']}
━━━━━━━━━━━━━━━━━━━━━━━

⚠️ Información sensible
👁 Uso interno

━━━━━━━━━━━━━━━━━━━━━━━
👑 @Broquicalifoxx
"""
    )

# 🔑 VIP
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

# 📊 MI ACCESO
async def miacceso(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id == ADMIN_ID:
        await update.message.reply_text("👑 ADMIN - acceso total")
        return

    if user_id in usuarios_vip:
        expira = usuarios_vip[user_id]
        await update.message.reply_text(f"✅ Activo hasta:\n{expira}")
    else:
        await update.message.reply_text("❌ Sin acceso VIP")

# ================= MAIN =================

if __name__ == "__main__":
    print("🚀 BOT CORRIENDO...")

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nequi", nequi))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("miacceso", miacceso))

    app.run_polling()