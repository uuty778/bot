from telethon import TelegramClient, events
from telethon.sessions import StringSession
import re

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"
session_str = "1BVtsOIQBuw7QWchMeY2sYsPhrP9oLEDQRinT871ThXkDyT5A9LcTV0k_cecG3sgfRsZxvayvp3A_oKD6bR_y-NeztrsHi_frwp_HcTUFLcGuvC4QLqDpZel-R9FM_QabSGzfw_8n25m2MY0MWiq5ZgD-LQB5qRV8TeFxwCR3TVJY1acjSsttUq-tYq7B-JidWQxX0HdrEUEBGYJOTNlxgVgetV8jA2LreEX-FNacsvfPKfIDpCgLTCOcV_k8x5wiFDtrVynvR2ldqydjlXP68fGGrVZOg3mc1NbpH6lmxHDiQsIPXKAtIYSXI4ObF7J8XY8QgM0ku18zG5TTpcktDnOU8N3KjAo="

TARGET = "@dd28"
history = []

bold_map = {'𝟬':'0','𝟭':'1','𝟮':'2','𝟯':'3','𝟰':'4','𝟱':'5','𝟲':'6','𝟳':'7','𝟴':'8','𝟵':'9'}

def unbold(text):
    for k, v in bold_map.items():
        text = text.replace(k, v)
    return text

def parse(text):
    text = unbold(text)
    iss = re.search(r'第(\d+)期', text)
    if not iss:
        return None
    last = int(iss.group(1)[-1])
    sm = re.search(r'(\d)\+(\d)\+(\d)=', text)
    if not sm:
        return None
    return (last, int(sm.group(1)), int(sm.group(2)))

client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('自动报数已启动！')

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
    msg = "📊 自动报数\nvalue=" + str(val) + "\n🔪 杀=" + str(kill)
    await client.send_message(TARGET, msg)

print("启动中...")
client.start()
client.run_until_disconnected()
