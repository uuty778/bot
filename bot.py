from telethon import TelegramClient, events
from telethon.sessions import StringSession
import re

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"

client = TelegramClient(StringSession("1BVtsOJwBu49t0kwYRsMp3tbGg1Ulu0Vyxox-C5bMS0vkEZOZmhwI9YSlHsXWgpyHwlLECg36zd_yiITwUkMjaDsI7wR6NtyfIRVQLy5KT9HqTMfUXkmKmcGiaDpdIwR8i79oCIi-U4K0ynrTJPsuZOx9xOYXrFBvdKceeD2FYStw1q3CkQouCc2jsPVntT2r_DvbsFARjCrcHlKJaqMI5G02i9JtDIpVtqEATjw0BvfX3c0ouDja2eYkHFCflqi04qg65ZRbtDTX4lOgQ-ZGrX4RCGY7LLNwCWRpqWBpjpvTGDi-1t5YWDz1X9lNpbucYCj7_bfUqsFvRK3whir1l7-Zs9_xi1A="), api_id, api_hash)

TARGET = "@dd28"
history = []

def unbold(text):
    m = {'𝟬':'0','𝟭':'1','𝟮':'2','𝟯':'3','𝟰':'4','𝟱':'5','𝟲':'6','𝟳':'7','𝟴':'8','𝟵':'9'}
    for k, v in m.items():
        text = text.replace(k, v)
    return text

def parse(text):
    try:
        text = unbold(text)
        iss = re.search(r'第(\d+)期', text)
        if not iss:
            return None
        last = int(iss.group(1)[-1])
        sm = re.search(r'(\d)\+(\d)\+(\d)=', text)
        if not sm:
            return None
        return (last, int(sm.group(1)), int(sm.group(2)))
    except:
        return None

@client.on(events.NewMessage(chats=TARGET))
async def handler(event):
    global history
    p = parse(event.message.text)
    if not p:
        return
    history.append(p)
    if len(history) < 3:
        return
    if len(history) > 20:
        history = history[-3:]

    a3 = history[-3][1]
    b2 = history[-2][2]
    last = history[-1][0]
    val = (a3 + b2 + last) % 10
    kill = (val + 5) % 10

    msg = f"📊 自动报数\nvalue={val}\n🔪 杀={kill}"
    await client.send_message(TARGET, msg)

print("启动中...")
client.start()
client.run_until_disconnected()
