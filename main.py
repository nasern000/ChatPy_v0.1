import os, random, string, urllib.parse, requests, openai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get('TOKEN')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '5876')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

VERSION = '0.2'
CREATOR = 'д-р Мухаммад Фархан'
MY_EMAIL = 'creatorofchatpy.anonim456@gmail.com'

client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

LANGS = {
    'ru': '🇷🇺 Русский', 'en': '🇺🇸 English', 'ar': '🇸🇦 العربية', 'tr': '🇹🇷 Türkçe',
    'uz': '🇺🇿 Oʻzbek', 'kk': '🇰🇿 Қазақ', 'de': '🇩🇪 Deutsch', 'fr': '🇫🇷 Français',
    'es': '🇪🇸 Español', 'hi': '🇮🇳 हिन्दी', 'zh': '🇨🇳 中文', 'ur': '🇵🇰 اردو'
}

TRANSLATE = {
    'ru': "ChatPi 0.2\nПиши что угодно - отвечу ИИ.\nИзображения с текста генерировать могу\nВсе команды смотреть в меню",
    'en': "ChatPi 0.2\nWrite anything - I will answer with AI.\nI can generate images from text\nSee all commands in menu",
    'ar': "ChatPi 0.2\nاكتب أي شيء - سأجيب بالذكاء الاصطناعي.\nيمكنني توليد الصور من النص\nشاهد كل الأوامر في القائمة",
    'tr': "ChatPi 0.2\nNe istersen yaz - YZ ile cevaplayacağım.\nMetinden görsel oluşturabilirim\nTüm komutlar menüde",
    'uz': "ChatPi 0.2\nXohlagan narsani yoz - AI bilan javob beraman.\nMatndan rasm yarataman\nBarcha buyruqlar menyuda",
    'kk': "ChatPi 0.2\nКез келген нәрсе жаз - ЖИ жауап береді.\nМәтіннен сурет жасай аламын\nБарлық командалар мәзірде",
    'de': "ChatPi 0.2\nSchreib was du willst - KI antwortet.\nIch kann Bilder aus Text erstellen\nAlle Befehle im Menü",
    'fr': "ChatPi 0.2\nÉcris ce que tu veux - je réponds avec l'IA.\nJe peux générer des images depuis le texte\nToutes les commandes dans le menu",
    'es': "ChatPi 0.2\nEscribe lo que quieras - respondo con IA.\nPuedo generar imágenes desde texto\nTodos los comandos en el menú",
    'hi': "ChatPi 0.2\nकुछ भी लिखो - AI जवाब देगा।\nमैं टेक्स्ट से इमेज बना सकता हूँ\nसभी कमांड मेनू में",
    'zh': "ChatPi 0.2\n随便写什么 - 我用AI回答。\n我可以根据文字生成图片\n所有命令在菜单中",
    'ur': "ChatPi 0.2\nکچھ بھی لکھیں - میں AI سے جواب دوں گا۔\nمیں متن سے تصویر بنا سکتا ہوں\nتمام کمانڈز مینو میں"
}

user_lang = {}
admin_users = set()
no_slash_warn = {}
admin_fail = {}
current_admin_pass = ADMIN_PASSWORD

def lang_keyboard():
    buttons = []
    row = []
    for code, name in LANGS.items():
        row.append(InlineKeyboardButton(name, callback_data=f"lang_{code}"))
        if len(row) == 2:
            buttons.append(row)
            row = []
    return InlineKeyboardMarkup(buttons)

def ai(prompt, lang='ru'):
    p = f"Отвечай на {lang}. {prompt}" if lang!='ru' else prompt
    try:
        r = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p)}?model=openai-large", timeout=25)
        if r.ok and r.text: return r.text.strip()
    except: pass
    return f"ChatPi: {prompt}"

# /start - СНАЧАЛА ВЫБОР ЯЗЫКА
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hey, another user. Please continue with setting your language, before we will start",
        reply_markup=lang_keyboard()
    )

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Выберите язык / Choose language:", reply_markup=lang_keyboard())

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    code = query.data.replace("lang_", "")
    user_lang[query.from_user.id] = code
    text = TRANSLATE.get(code, TRANSLATE['en'])
    await query.edit_message_text(text)

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"ChatPi {VERSION}\nСоздал: {CREATOR}\nСпасибо: Pollinations + OpenAI\nВерсия: {VERSION}")

async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args)
    if not prompt:
        await update.message.reply_text("Напиши так: /image кот в сапогах")
        return
    if not client:
        await update.message.reply_text("Добавь OPENAI_API_KEY в Secrets!")
        return
    await update.message.reply_text(f"Рисую: {prompt}... ⏳")
    try:
        resp = client.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024")
        await update.message.reply_photo(photo=resp.data[0].url, caption=f"Готово: {prompt}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = " ".join(context.args)
    if not q:
        await update.message.reply_text("Пиши: /search запрос")
        return
    lang = user_lang.get(update.effective_user.id, 'ru')
    await update.message.reply_text(ai(f"Поиск: {q}", lang))

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global current_admin_pass
    uid = update.effective_user.id
    # ТВОЕ НОВОЕ ПРАВИЛО ПУНКТ 10
    if not context.args or len(context.args)!= 1:
        await update.message.reply_text("A message with this command without going from the administrator's chat and/or if there is anything else in this message, the message with the command cannot be confirmed. Please try again.")
        return
    if context.args[0] == current_admin_pass:
        admin_users.add(uid)
        no_slash_warn[uid]=0
        admin_fail[uid]=0
        await update.message.reply_text("Админка открыта ✅")
    else:
        c = admin_fail.get(uid,0)+1
        admin_fail[uid]=c
        if c>=2:
            print(f"‼️ТРЕВОГА ВЗЛОМ АДМИНКИ‼️ User {uid}")
            admin_fail[uid]=0
        await update.message.reply_text("Неверный пароль")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    text = update.message.text
    if text.startswith('/'): return
    if uid in admin_users:
        cnt = no_slash_warn.get(uid,0)+1
        no_slash_warn[uid]=cnt
        if cnt==1:
            await update.message.reply_text("Извините, но я с разработчиками так не общаюсь.")
            return
        if cnt==2:
            await update.message.reply_text("Внимание: Вы можете быть мошенником...")
            return
        if cnt>=3:
            admin_users.discard(uid)
            no_slash_warn[uid]=0
            if cnt==3:
                await update.message.reply_text("Вылет в обычный чат. Нужен /admin")
                return
            else:
                current_admin_pass = ''.join(random.choices(string.digits, k=6))
                print(f"‼️ТРЕВОГА ВЗЛОМ АДМИНКИ‼️ Новый пароль {current_admin_pass} -> {MY_EMAIL}")
                await update.message.reply_text("Вылет + смена пароля. Смотри лог.")
                return
    lang = user_lang.get(uid, 'ru')
    await update.message.reply_text(ai(text, lang))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lang", lang_command))
    app.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("image", image_command))
    app.add_handler(CommandHandler("search", search_command))
    app.add_handler(CommandHandler("admin", admin_command))
    app.add_handler(CommandHandler("help", lang_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == "__main__":
    main()
