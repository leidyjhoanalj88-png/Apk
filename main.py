require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');

// =========================================================
// 𝕮𝖔𝖓𝖋𝖎𝖌𝖚𝖗𝖆𝖈𝖎𝖔𝖓 𝕰𝖑𝖎𝖙𝖊 - 𝖇𝖗𝖔ｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝
// =========================================================
const token = '8463258539:AAHUvSMIDRP4mnlNmPED-Q3EHnAaIrKMWiE';
const ABSTRACT_KEY = process.env.ABSTRACT_KEY; // Asegúrate de tenerla en tu .env
const OWNER_ID = 8114050673; // 𝖇ｒｏｑｕ𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝

const bot = new TelegramBot(token, { polling: true });

// URLs de tus APIs de Cloudflare
const API_PLACA = "https://funny-minimize-construction-monday.trycloudflare.com/api.php";
const API_C1 = "https://prints-causes-britannica-washington.trycloudflare.com/?doc=";

const BANNER = "https://i.postimg.cc/PxTk8Wzs/goku-dox.jpg";

// =========================================================
// 𝕸𝖊𝖓𝖘𝖆𝖏𝖊 𝖉𝖊 𝕴𝖓𝖎𝖈𝖎𝖔
// =========================================================
bot.onText(/\/start/, (msg) => {
    const welcome = `
꧁☬ **𝖇𝖗ｏｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝 𝕾𝖞𝖘𝖙𝖊𝖒** ☬꧂

👤 **𝕬𝖌𝖊𝖓𝖙𝖊:** \`${msg.from.first_name}\`
🆔 **𝕴𝕯:** \`${msg.from.id}\`

꧁☬ 𝖇𝖗ｏｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝: 𝕰𝖑 𝖔𝖏𝖔 𝖖𝖚𝖊 𝖙𝖔𝖉𝖔 𝖑𝖔 𝖛𝖊 ☬꧂

Usa /menu para desplegar el arsenal.`;
    
    bot.sendPhoto(msg.chat.id, BANNER, { caption: welcome, parse_mode: "Markdown" });
});

// =========================================================
// 𝕸𝖊𝖓𝖚 𝖉𝖊 𝕬𝖗𝖘𝖊𝖓𝖆𝖑
// =========================================================
bot.onText(/\/menu/, (msg) => {
    const menuText = `
꧁⚔ **𝕬𝖗𝖘𝖊𝖓𝖆𝖑 𝖇𝖗ｏｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝** ⚔꧂
════════════════════════
🔴 **𝕴𝖓𝖙𝖊𝖑𝖎𝖌𝖊𝖓𝖈𝖎𝖆:**
• \`/placa [ABC123]\` - Info Vehicular
• \`/c1 [DOC]\` - Antecedentes
• \`/nequi [NUM]\` - Consulta Nequi
• \`/numero [NUM]\` - Info Operador

🔵 **𝕽𝖊𝖉𝖊𝖘 𝖞 𝕾𝖊𝖌𝖚𝖗𝖎𝖉𝖆𝖉:**
• \`/ip [8.8.8.8]\` - Geolocalización
• \`/email [MAIL]\` - Validación
• \`/me\` - Mi Perfil
════════════════════════`;
    bot.sendMessage(msg.chat.id, menuText, { parse_mode: "Markdown" });
});

// =========================================================
// 𝕮𝖔𝖓𝖘𝖚𝖑𝖙𝖆𝖘 𝖉𝖊 𝕻𝖔𝖉𝖊𝖗 (𝕬𝕻𝕴𝖘 𝕻𝖗𝖔𝖕𝖎𝖆𝖘)
// =========================================================

// COMANDO PLACA
bot.onText(/\/placa (.+)/, async (msg, match) => {
    const placa = match[1].toUpperCase();
    bot.sendMessage(msg.chat.id, `⏳ **𝖇ｒｏｑｕｉｃａｌｉｆａｘ** consultando placa \`${placa}\`...`, { parse_mode: "Markdown" });

    try {
        const res = await axios.get(`${API_PLACA}?placa=${placa}`);
        bot.sendMessage(msg.chat.id, `꧁☬ **𝕽𝖊𝖘𝖚𝖑𝖙𝖆𝖉𝖔 𝖇𝖗ｏｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝** ☬꧂\n\n\`${res.data}\``, { parse_mode: "Markdown" });
    } catch (e) {
        bot.sendMessage(msg.chat.id, "❌ Error en el servidor de placas.");
    }
});

// COMANDO NEQUI (TU ORIGINAL MEJORADO)
bot.onText(/\/nequi (.+)/, (msg, match) => {
    if (msg.from.id !== OWNER_ID) return bot.sendMessage(msg.chat.id, "❌ Acceso denegado a `𝖇ｒｏｑｕｉｃａｌｉｆａｘ`.");
    const numero = match[1];
    bot.sendMessage(msg.chat.id, `✅ **𝖇ｒｏｑｕｉｃａｌｉｆａｘ** ha validado el número: \`${numero}\``, { parse_mode: "Markdown" });
});

// =========================================================
// 𝕮𝖔𝖓𝖘𝖚𝖑𝖙𝖆𝖘 𝕬𝖇𝖘𝖙𝖗𝖆𝖈𝖙 (𝕴𝖓𝖋𝖔 𝕰𝖝𝖙𝖊𝖗𝖓𝖆)
// =========================================================

// CONSULTA NÚMERO
bot.onText(/\/numero (.+)/, async (msg, match) => {
    const numero = match[1];
    bot.sendMessage(msg.chat.id, "🔎 **𝖇ｒｏｑｕｉｃａｌｉｆａｘ** rastreando operador...", { parse_mode: "Markdown" });

    try {
        const url = `https://phonevalidation.abstractapi.com/v1/?api_key=${ABSTRACT_KEY}&phone=${numero}`;
        const res = await axios.get(url);
        const d = res.data;

        bot.sendMessage(msg.chat.id, `
꧁📞 **𝕴𝖓𝖋𝖔 𝖇𝖗ｏｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝** ꧂
════════════════════════
📱 **Número:** \`${numero}\`
🌍 **País:** \`${d.country.name}\`
📡 **Operador:** \`${d.carrier}\`
✔️ **Válido:** \`${d.valid}\`
════════════════════════`, { parse_mode: "Markdown" });
    } catch {
        bot.sendMessage(msg.chat.id, "❌ Error consultando número.");
    }
});

// CONSULTA IP
bot.onText(/\/ip (.+)/, async (msg, match) => {
    const ip = match[1];
    try {
        const url = `https://ipgeolocation.abstractapi.com/v1/?api_key=${ABSTRACT_KEY}&ip_address=${ip}`;
        const res = await axios.get(url);
        const d = res.data;

        bot.sendMessage(msg.chat.id, `
꧁🌐 **𝕴𝕻 𝖇𝖗ｏｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝** ꧂
════════════════════════
🌍 **País:** \`${d.country}\`
🏙️ **Ciudad:** \`${d.city}\`
🔒 **VPN:** \`${d.security.is_vpn ? "SÍ ⚠️" : "NO ✅"}\`
════════════════════════`, { parse_mode: "Markdown" });
    } catch {
        bot.sendMessage(msg.chat.id, "❌ Error localizando IP.");
    }
});

// COMANDO PERFIL
bot.onText(/\/me/, (msg) => {
    const status = (msg.from.id === OWNER_ID) ? "👑 𝕺𝖜𝖓𝖊𝖗 𝕾𝖚𝖕𝖗𝖊𝖒𝖔" : "👤 𝕬𝖌𝖊𝖓𝖙𝖊";
    bot.sendMessage(msg.chat.id, `
꧁👤 **𝕻𝖊𝖗𝖋𝖎𝖑 𝖇𝖗ｏｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝** ꧂
🆔 **𝕴𝕯:** \`${msg.from.id}\`
⚡ **𝕽𝖆𝖓𝖌𝖔:** \`${status}\`
⚔ **𝕰𝖘𝖙𝖆𝖉𝖔:** \`Activo\``, { parse_mode: "Markdown" });
});

// MANEJO DE ERRORES
bot.on("polling_error", (err) => console.log("❌ ERROR 𝖇𝖗ｏｑｕｉｃａｌｉｆａｘ:", err.message));

console.log("꧁☬ 𝖇𝖗ｏｑ𝖚𝖎𝖈𝖆𝖑𝖎𝖋𝖆𝖝 𝕭𝖔𝖙 𝕺𝖓𝖑𝖎𝖓𝖊 (𝕹𝖔𝖉𝖊.𝖏𝖘) ☬꧂");
