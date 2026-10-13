# ===== КУДА ВСТАВЛЯТЬ - ТОЛЬКО 2 ШТУКИ =====
# В Secrets добавляешь только:
# TOKEN = токен от @BotFather
# ADMIN_PASSWORD = 5876
# Все! Никаких OPENAI ключей

TOKEN = os.environ.get('TOKEN')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '5876')

MY_EMAIL = 'naserabdulrahimn950@gmail.com'
VERSION = '0.2'
CHANGELOG = 'ChatPi 0.2 - GPT-4o бесплатно без ключей + /image + /lang'
CREATOR = 'д-р Мухаммад Фархан'

# ИИ - БЕСПЛАТНЫЙ GPT-4o ПРЕДПОСЛЕДНЯЯ ВЕРСИЯ БЕЗ КЛЮЧЕЙ
def ai(prompt, lang='ru'):
    p = f"Отвечай на языке {lang}. {prompt}" if lang!='ru' else prompt
    try:
        # openai-large = GPT-4o
        r = requests.get(f"https://text.pollinations.ai/{urllib.parse.quote(p)}?model=openai-large", timeout=20)
        if r.ok and r.text: return r.text
    except: pass
    return f"ChatPi: {prompt}"
