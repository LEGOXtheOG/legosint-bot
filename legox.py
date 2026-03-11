import telebot
import requests
import json
import time
from datetime import datetime,timedelta
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton

TOKEN="8690768879:AAGLxs7WMK782qzJsns7382H0aRzY38ArrQ"

NUM_API="https://cyber-osint-num-infos.vercel.app/api/numinfo"
COSMO_API="http://api.subhxcosmo.in/api"

NUM_KEY="legox"
COSMO_KEY="LEGOX"

OWNER_ID=7352668628

bot=telebot.TeleBot(TOKEN,parse_mode="Markdown")

FOOTER="\n\nSupport :- @povLegox\nDeveloped by :- Legox"

try:
    with open("users.json","r") as f:
        db=json.load(f)
except:
    db={"users":{},"admins":[]}

users = db.get("users", {})
admins = db.get("admins", [])

def save():
    with open("users.json","w") as f:
        json.dump({"users":users,"admins":admins},f)

def is_admin(uid):
    return uid==OWNER_ID or uid in admins

def is_premium(uid):

    user=users.get(str(uid))
    if not user:
        return False

    exp=user.get("premium")

    if not exp:
        return False

    if datetime.now()>datetime.fromisoformat(exp):
        users[str(uid)]["premium"]=None
        save()
        return False

    return True

def get_user(uid,username):

    if str(uid) not in users:

        users[str(uid)]={
        "credit":4,
        "username":username,
        "premium":None
        }

        save()

def loading(msg):

    bars=[
    "[█□□□□□□□□□] 10%",
    "[████□□□□□□] 40%",
    "[████████□□] 80%",
    "[██████████] 100%"
    ]

    for b in bars:
        bot.edit_message_text(f"🔎 Searching Database...\n\n{b}",msg.chat.id,msg.message_id)
        time.sleep(1)

def users_page(page):

    per_page=10
    ids=list(users.keys())

    start=(page-1)*per_page
    end=start+per_page

    selected=ids[start:end]

    text="👥 *BOT USERS*\n\n"

    for uid in selected:

        uname=users[uid]["username"]

        if uname:
            uname="@"+uname
        else:
            uname="No username"

        text+=f"{uname}\n`{uid}`\n\n"

    text+=f"\nTotal Users : {len(ids)}"

    markup=InlineKeyboardMarkup()

    if start>0:
        markup.add(InlineKeyboardButton("⬅ Prev",callback_data=f"users_{page-1}"))

    if end<len(ids):
        markup.add(InlineKeyboardButton("➡ Next",callback_data=f"users_{page+1}"))

    return text,markup

@bot.message_handler(commands=['start'])
def start(message):

    uid=message.from_user.id
    username=message.from_user.username

    get_user(uid,username)

    markup=InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📖 Commands",callback_data="commands"))

    if is_admin(uid):
        markup.add(InlineKeyboardButton("👥 Users Monitor",callback_data="users_1"))

    if uid==OWNER_ID:
        markup.add(InlineKeyboardButton("🛡 Admins",callback_data="admins"))

    bot.send_message(message.chat.id,f"""
👾 *LEGOSINT OSINT BOT*

This bot provides access to publicly available OSINT data sources.

• No private databases are hosted by this bot
• All information comes from public sources
• Intended for research and educational use
• Users are responsible for how data is used
• Must comply with Telegram Terms of Service

━━━━━━━━━━━━━━━━━━

💳 Credits : `{users[str(uid)]['credit']}`
⭐ Premium : `{is_premium(uid)}`

━━━━━━━━━━━━━━━━━━

Built by : @povLegox
"""+FOOTER,reply_markup=markup,protect_content=True)

@bot.callback_query_handler(func=lambda call:True)
def callback(call):

    uid=call.from_user.id

    if call.data=="commands":

        bot.send_message(call.message.chat.id,"""
📖 COMMAND GUIDE

/num xxxxxxxxxx
Mobile lookup

/aadhar xxxxxxxxxxxx
Aadhaar lookup

/telegram xxxxxxxxx
Telegram ID lookup

/profile
Profile info

/referrals
Referral link
"""+FOOTER)

    elif call.data.startswith("users_"):

        if not is_admin(uid):
            return

        try:
            page=int(call.data.split("_")[1])
        except:
            page=1

        text,markup=users_page(page)

        bot.edit_message_text(
            text+FOOTER,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

    elif call.data=="admins":

        if uid!=OWNER_ID:
            return

        text="🛡 *ADMINS*\n\n"

        if not admins:
            text+="No admins yet"
        else:
            for a in admins:
                text+=f"`{a}`\n"

        bot.send_message(call.message.chat.id,text+FOOTER)

@bot.message_handler(commands=['profile'])
def profile(message):

    uid=message.from_user.id
    username=message.from_user.username

    get_user(uid,username)

    bot.reply_to(message,f"""
👤 *USER PROFILE*

🆔 ID : `{uid}`
👤 Username : `{username}`

💳 Credits : `{users[str(uid)]['credit']}`
⭐ Premium : `{is_premium(uid)}`
"""+FOOTER)

@bot.message_handler(commands=['referrals'])
def referrals(message):

    uid=message.from_user.id

    bot.reply_to(message,f"""
🎁 *REFERRAL SYSTEM*

Invite friends:

https://t.me/{bot.get_me().username}?start={uid}
"""+FOOTER)

@bot.message_handler(commands=['addadmin'])
def addadmin(message):

    if message.from_user.id!=OWNER_ID:
        return

    uid=int(message.text.split()[1])

    if uid not in admins:
        admins.append(uid)
        save()

    bot.reply_to(message,"Admin added"+FOOTER)

@bot.message_handler(commands=['removeadmin'])
def removeadmin(message):

    if message.from_user.id!=OWNER_ID:
        return

    uid=int(message.text.split()[1])

    if uid in admins:
        admins.remove(uid)
        save()

    bot.reply_to(message,"Admin removed"+FOOTER)

@bot.message_handler(commands=['addcredit'])
def addcredit(message):

    if not is_admin(message.from_user.id):
        return

    parts=message.text.split()

    uid=int(parts[1])
    amount=int(parts[2])

    users[str(uid)]["credit"]+=amount
    save()

    bot.reply_to(message,"Credits added"+FOOTER)

@bot.message_handler(commands=['prem'])
def prem(message):

    if not is_admin(message.from_user.id):
        return

    parts=message.text.split()

    uid=int(parts[1])
    days=int(parts[2].replace("days","").replace("day",""))

    exp=datetime.now()+timedelta(days=days)

    users[str(uid)]["premium"]=exp.isoformat()
    save()

    bot.reply_to(message,"Premium activated"+FOOTER)

@bot.message_handler(commands=['num'])
def num_lookup(message):

    uid=message.from_user.id
    username=message.from_user.username
    get_user(uid,username)

    term=message.text.split()[1]

    if not is_admin(uid) and not is_premium(uid):

        if users[str(uid)]["credit"]<=0:
            bot.reply_to(message,"❌ No credits"+FOOTER)
            return

        users[str(uid)]["credit"]-=1
        save()

    loading_msg=bot.reply_to(message,"🔎 Searching...")

    loading(loading_msg)

    r=requests.get(f"{NUM_API}?key={NUM_KEY}&num={term}").json()

    text=f"""
👾 *LEGOSINT RESULT*

📱 Number : `{term}`
"""

    for i,res in enumerate(r.get("results",[]),1):

        text+=f"""

━━━━━━━━━━━━━━━━━━
📂 Record {i}

👤 Name : `{res.get("NAME")}`
🧔 Father : `{res.get("fname")}`
📶 Circle : `{res.get("circle")}`
📞 Mobile : `{res.get("MOBILE")}`
📞 Alt : `{res.get("alt")}`
🆔 ID : `{res.get("id")}`
📧 Email : `{res.get("EMAIL")}`

🏠 Address
`{res.get("ADDRESS")}`
"""

    bot.edit_message_text(text+FOOTER,message.chat.id,loading_msg.message_id)

@bot.message_handler(commands=['aadhar'])
def aadhar_lookup(message):

    uid=message.from_user.id
    username=message.from_user.username
    get_user(uid,username)

    term=message.text.split()[1]

    loading_msg=bot.reply_to(message,"🔎 Searching...")
    loading(loading_msg)

    r=requests.get(f"{COSMO_API}?key={COSMO_KEY}&type=id_number&term={term}").json()

    text=f"🪪 *AADHAAR RESULT*\n\nAadhaar : `{term}`\n"

    for i,res in enumerate(r.get("result",[]),1):

        text+=f"""

━━━━━━━━━━━━━━━━━━
📂 Record {i}

👤 Name : `{res.get("name")}`
🧔 Father : `{res.get("fname")}`
📞 Mobile : `{res.get("mobile")}`
📞 Alt : `{res.get("alt")}`
📧 Email : `{res.get("email")}`

🏠 Address
`{res.get("address")}`
"""

    bot.edit_message_text(text+FOOTER,message.chat.id,loading_msg.message_id)

@bot.message_handler(commands=['telegram'])
def telegram_lookup(message):

    uid=message.from_user.id
    username=message.from_user.username
    get_user(uid,username)

    term=message.text.split()[1]

    loading_msg=bot.reply_to(message,"🔎 Searching...")
    loading(loading_msg)

    r=requests.get(f"{COSMO_API}?key={COSMO_KEY}&type=tg&term={term}").json()

    data=r.get("result",{})

    text=f"""
🆔 *TELEGRAM RESULT*

TG ID : `{term}`
Country : `{data.get("country")}`
Phone : `{data.get("country_code")}{data.get("number")}`
"""

    bot.edit_message_text(text+FOOTER,message.chat.id,loading_msg.message_id)

print("Bot running")

bot.infinity_polling()
