async def comando_nequi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not tiene_permiso(update.message.from_user.id): return
    if not context.args:
        await update.message.reply_text("📌 Uso: `/nequi <telefono>`")
        return
    
    tel = context.args[0]
    wait = await update.message.reply_text(f"📱 **Consultando Nequi Alpha:** `{tel}`...")

    try:
        # Headers estrictos para evitar respuestas vacías
        headers = {
            "X-Api-Key": "Z5k4Y1n4n0vS",
            "Content-Type": "application/json",
            "User-Agent": "PostmanRuntime/7.32.3"
        }
        
        # Intentamos la petición
        response = requests.post(
            API_NEQUI, 
            json={"telefono": str(tel)}, 
            headers=headers, 
            timeout=15,
            verify=True # Cambiar a False si hay error de SSL
        )
        
        data = response.json()

        # --- MAPEADOR INTELIGENTE DE JSON ---
        # Buscamos todas las variantes posibles de nombres de llaves
        nombre = data.get('nombre_completo') or data.get('nombre') or data.get('full_name') or data.get('data', {}).get('nombre')
        cedula = data.get('cedula') or data.get('documento') or data.get('cc') or data.get('data', {}).get('cedula')
        ciudad = data.get('municipio') or data.get('ciudad') or data.get('city') or "No registra"

        if nombre or cedula:
            res = (
                "📱 **𝐃𝐀𝐓𝐎𝐒 𝐍𝐄𝐐𝐔𝐈**\n"
                "═════════════════════════\n"
                f"👤 **TITULAR:** `{nombre if nombre else 'No registra'}`\n"
                f"🆔 **CÉDULA:** `{cedula if cedula else 'No registra'}`\n"
                f"📍 **CIUDAD:** `{ciudad}`\n"
                "═════════════════════════\n"
                f"👑 **Admin:** {OWNER_USER}"
            )
            await wait.edit_text(res, parse_mode="Markdown")
        else:
            # Si no hay datos, mostramos lo que la API respondió para debuggear
            await wait.edit_text(f"⚠️ **API sin datos para este número.**\nRespuesta: `{json.dumps(data)}`", parse_mode="Markdown")

    except Exception as e:
        await wait.edit_text(f"❌ **Error de Conexión:** `{str(e)}`")
