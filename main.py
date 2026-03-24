import os
import time
import subprocess
import cv2
import pytesseract
import numpy as np
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ================= CONFIG =================
BOT_TOKEN = "AQUI_TU_TOKEN"
ADMIN_ID = 123456789  # tu ID

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ============== SCRAPER ===================
class NequiConsultor:
    def __init__(self):
        self.temp_img = "screen.png"
        if not self.check_adb():
            raise Exception("ADB no conectado")

    def _adb(self, cmd):
        return subprocess.run(f"adb {cmd}", shell=True, capture_output=True, text=True).stdout

    def check_adb(self):
        return "device\t" in self._adb("devices")

    def consultar(self, numero):
        try:
            # limpiar
            self._adb("shell input tap 900 450")
            time.sleep(0.5)

            # escribir número
            self._adb(f"shell input text {numero}")
            self._adb("shell input keyevent 66")

            time.sleep(4)

            # screenshot
            self._adb(f"shell screencap -p /sdcard/{self.temp_img}")
            self._adb(f"pull /sdcard/{self.temp_img} .")

            img = cv2.imread(self.temp_img)
            if img is None:
                return "❌ Error captura"

            h, w = img.shape[:2]
            roi = img[int(h*0.2):int(h*0.4), int(w*0.05):int(w*0.95)]

            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (5,5), 0)

            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )

            texto = pytesseract.image_to_string(
                thresh,
                lang='spa',
                config='--psm 6'
            )

            texto = texto.lower()
            texto = texto.replace("¿le vas a enviar a", "")
            texto = texto.replace("le vas a enviar a", "")
            texto = texto.replace("?", "")
            texto = texto.replace("\n", " ").strip()

            palabras = texto.split()
            nombre = " ".join(p for p in palabras if not p.isdigit())

            return nombre if len(nombre) > 3 else "❌ No encontrado"

        except Exception as e:
            return f"Error: {str(e)}"


# ============== BOT ===================
bot_nequi = NequiConsultor()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Bot Nequi activo\nUsa: /nequi 3001234567")

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
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("nequi", nequi))

    print("🚀 Bot corriendo...")
    app.run_polling()