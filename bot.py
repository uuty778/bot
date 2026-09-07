from telethon import TelegramClient, events
from telethon.sessions import StringSession
import re

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"
session_str = "1BVtsOIQBuw7QWchMeY2sYsPhrP9oLEDQRinT871ThXkDyT5A9LcTV0k_cecG3sgfRsZxvayvp3A_oKD6bR_y-NeztrsHi_frwp_HcTUFLcGuvC4QLqDpZel-R9FM_QabSGzfw_8n25m2MY0MWiq5ZgD-LQB5qRV8TeFxwCR3TVJY1acjSsttUq-tYq7B-JidWQxX0HdrEUEBGYJOTNlxgVgetV8jA2LreEX-FNacsvfPKfIDpCgLTCOcV_k8x5wiFDtrVynvR2ldqydjlXP68fGGrVZOg3mc1NbpH6lmxHDiQsIPXKAtIYSXI4ObF7J8XY8QgM0ku18zG5TTpcktDnOU8N3KjAo="
TARGET = "@dd28"

history = []

bold_map = {'𝟬':'0','𝟭':'1','𝟮':'2','𝟯':'3','𝟰':'4','𝟱':'5','𝟲':'6','𝟳':'7','𝟴':'8','𝟵':'9'}

def unbold(t):
    for k, v in bold_map.items():
        t = t.replace(k, v)
    return t

client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(chats=TARGET))
async def handler(event):
    global history
    text = event.message.text
    if not text:
        return

    text = unbold(text)

    pm = re.search(r'第(\d+)期', text)
    if not pm:
        return
    cur_period = pm.group(1)

    om = re.search(r'开(\d+)', text)
    if not om:
        return
    opened = int(om.group(1))
    tail = opened % 10

    sm = re.search(r'(\d)\+(\d)\+(\d)=', text)
    if not sm:
        return
    a = int(sm.group(1))
    b = int(sm.group(2))
    c = int(sm.group(3))

    # 判断上期挂没挂（用上上期杀号 vs 本期开奖）
    hit = True
    if len(history) >= 2 and len(history[-2]) >= 5:
        prev_kill = history[-2][4]
        o_big = tail >= 5
        o_odd = tail % 2 == 1
        opened_ss = ("大" if o_big else "小") + ("单" if o_odd else "双")
        if opened_ss == prev_kill:
            hit = False

    # 挂了清空
    if not hit:
        history.clear()

    # 记录本期
    history.append([c, a, b])
    if len(history) > 3:
        history = history[-3:]

    while len(history) < 3:
        history.insert(0, [0, 0, 0])

    # 算法：第3期a + 第2期b + 最新期末位
    a3 = history[-3][1]
    b2 = history[-2][2]
    cur = history[-1][0]
    val = (a3 + b2 + cur) % 10

    kill_ss = ("小" if val >= 5 else "大") + ("双" if val % 2 == 1 else "单")

    history[-1].append(kill_ss)

    # 双组
    shuangzu_map = {
        "小单": "小双大单",
        "小双": "小单大双",
        "大单": "大双小单",
        "大双": "大单小双"
    }
    shuangzu = shuangzu_map.get(kill_ss, "")

    # 发
    emoji = "🀄" if hit else "🍉"
    await client.send_message(TARGET, f"第{cur_period}期杀{kill_ss} {shuangzu}{emoji}{opened}")

print("启动中...")
client.start()
client.run_until_disconnected()
