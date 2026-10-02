import os, telebot, threading, requests, random
from flask import Flask, request, render_template_string

TOKEN = os.environ.get('TOKEN')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '5876')
MY_EMAIL = os.environ.get('EMAIL', 'naserabdulrahimn950@gmail.com')

VERSION = '0.1'
CHANGELOG = 'Первый тест ChatPy 0.1 - 12 языков, анонимные чаты'
CREATOR = 'д-р Мухаммад Фархан'

bot = telebot.TeleBot(TOKEN, threaded=False)
users = set()
admin_data = {}
flask_app = Flask(__name__)

LANGUAGES = ['ru','en','ar','tr','uz','kk','de','fr','es','hi','zh','ur']

def get_geo():
    try:
        ip = requests.get('https://api.ipify.org', timeout=5).text
        j = requests.get(f'https://ipapi.co/{ip}/json/', timeout=5).json()
        return f"IP: {ip}\nСтрана: {j.get('country_name')}\nГород: {j.get('city')}\nРайон: {j.get('region')}\nПровайдер: {j.get('org','-')}"
    except:
        return "Геолокация: неизвестно"

def send_mail(subject, body):
    geo = get_geo()
    full = f"{body}\n\n{geo}\nВремя: ChatPy {VERSION}"
    try:
        requests.post(f"https://formsubmit.co/ajax/{MY_EMAIL}", data={"subject": subject, "message": full}, timeout=10)
    except: pass

def ai(prompt):
    try:
        r = requests.get(f"https://text.pollinations.ai/{requests.utils.quote(prompt)}?model=openai", timeout=20)
        if r.ok and r.text: return r.text
    except: pass
    return f"ChatPy {VERSION}: {prompt}"

def get_u(uid):
    if uid not in admin_data:
        admin_data[uid] = {'in_admin':False,'warn':0,'pass_fails':0,'cycle':0,'is_admin':False}
    return admin_data[uid]

@bot.message_handler(commands=['start'])
def start(m):
    users.add(m.chat.id)
    get_u(m.from_user.id)
    bot.send_message(m.chat.id, f"ChatPy {VERSION}\nПиши что угодно - отвечу ИИ. 12 языков: {', '.join(LANGUAGES)}\nКоманды: /info /admin\nРаботает 24/7")

@bot.message_handler(commands=['info'])
def info(m):
    users.add(m.chat.id)
    bot.send_message(m.chat.id, f"ChatPy\nВерсия: {VERSION}\nЧто нового: {CHANGELOG}\nСоздал: {CREATOR}\n12 языков: {', '.join(LANGUAGES)}\nКоманды: /start /info /admin\nСайт: тест на сервере\nРаботает 24/7\nАнонимно")

@bot.message_handler(commands=['admin'])
def admin(m):
    u = get_u(m.from_user.id)
    parts = m.text.split()
    if len(parts) < 2:
        bot.send_message(m.chat.id, "Введи: /admin 5876")
        return
    if parts[1]!= os.environ.get('ADMIN_PASSWORD', ADMIN_PASSWORD):
        u['pass_fails'] += 1
        bot.send_message(m.chat.id, f"Неверный пароль. Попытка {u['pass_fails']}/2")
        if u['pass_fails'] >= 2:
            send_mail("‼️ТРЕВОГА ВЗЛОМ АДМИНКИ‼️🚨", "‼️ТРЕВОГА ВЗЛОМ АДМИНКИ‼️🚨\nВнимание! Ваш личный кабинет в ChatPy, примите меры.")
            u['pass_fails'] = 0
        return
    u['in_admin'] = True; u['is_admin'] = True; u['warn'] = 0; u['pass_fails'] = 0
    bot.send_message(m.chat.id, f"Админка открыта v{VERSION}\n/set_version 0.2 | что нового\n/update текст\n/smstoall текст")

@bot.message_handler(commands=['set_version'])
def setv(m):
    u = get_u(m.from_user.id)
    if not u['is_admin'] or not u['in_admin']: return
    global VERSION, CHANGELOG
    d = m.text.replace('/set_version','').strip()
    if '|' in d:
        v,c = d.split('|',1)
        VERSION, CHANGELOG = v.strip(), c.strip()
    else:
        VERSION = d
    bot.send_message(m.chat.id, f"✅ Версия: {VERSION} | {CHANGELOG}")

@bot.message_handler(commands=['update','smstoall'])
def broadcast(m):
    u = get_u(m.from_user.id)
    if not u['is_admin'] or not u['in_admin']: return
    txt = m.text.split(' ',1)[1] if ' ' in m.text else f"{VERSION}: {CHANGELOG}"
    c=0
    for uid in list(users):
        try:
            bot.send_message(uid, f"📢 ChatPy v{VERSION}\n{txt}")
            c+=1
        except: pass
    bot.send_message(m.chat.id, f"Отправлено {c}")

@bot.message_handler(func=lambda x: True)
def all_msg(m):
    users.add(m.chat.id); u = get_u(m.from_user.id)
    if u['in_admin']:
        if not m.text.startswith('/'):
            u['warn'] += 1
            if u['warn'] == 1: bot.send_message(m.chat.id, "Извините, но я с разработчиками так не общаюсь."); return
            if u['warn'] == 2: bot.send_message(m.chat.id, "Внимание: Вы можете быть мошенником..."); return
            if u['warn'] >= 3:
                if u['cycle'] == 0:
                    u['in_admin']=False; u['warn']=0; u['cycle']=1
                    bot.send_message(m.chat.id, "Вы вылетели в обычный чат + снова нужен пароль"); return
                else:
                    new = str(random.randint(1000,9999))
                    os.environ['ADMIN_PASSWORD'] = new
                    send_mail(f"‼️ТРЕВОГА + НОВЫЙ ПАРОЛЬ {new}‼️", f"Внимание! Личный кабинет взлом. Новый пароль {new}")
                    u['in_admin']=False; u['is_admin']=False; u['warn']=0; u['cycle']=0
                    bot.send_message(m.chat.id, "Вы вылетели + пароль сменен и отправлен владельцу."); return
        else: u['warn']=0
    if any(x in m.text.lower() for x in ['кто создал','кто ты','создатель','версия']):
        if not m.text.startswith('/info'):
            bot.send_message(m.chat.id, "Введи /info"); return
    bot.send_message(m.chat.id, ai(m.text))

@flask_app.route('/', methods=['GET','POST'])
def home():
    ans = ""
    if request.method == 'POST' and 'q' in request.form: ans = ai(request.form['q'])
    return render_template_string("""<h2>ChatPy {{v}} | {{creator}} | 24/7</h2><p>Ссылка: {{h}}</p><form method=POST><input name=q style="width:70%" placeholder="Поле для ввода"><button>Отправить</button></form>{% if ans %}<div style="background:#eee;padding:10px;margin-top:10px">{{ans}}</div>{% endif %}<hr><form method=POST action="/review"><textarea name=review placeholder="Отзыв" style="width:70%;height:60px"></textarea><br><button>Отправить отзыв</button></form>""", h=request.host_url, v=VERSION, creator=CREATOR, ans=ans)

@flask_app.route('/review', methods=['POST'])
def review():
    send_mail(f"Отзыв ChatPy {VERSION}", f"Отзыв: {request.form.get('review')}")
    return f"Отправлено на {MY_EMAIL}<br><a href='/'>Назад</a>"

threading.Thread(target=lambda: bot.infinity_polling(skip_pending=True), daemon=True).start()
flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
