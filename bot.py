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

def parse(t):
    t = unbold(t)
    iss = re.search(r'第(\d+)期', t)
    if not iss:
        return None
    last = int(iss.group(1)[-1])
    sm = re.search(r'(\d)\+(\d)\+(\d)=', t)
    if not sm:
        return None
    return (last, int(sm.group(1)), int(sm.group(2)))

client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(chats=TARGET))
async def handler(ev):
    global history
    text = ev.message.text
    p = parse(text)
    if not p:
        return

    om = re.search(r'开(\d+)', text)
    opened = int(om.group(1)) if om else None
    tail = opened % 10 if opened is not None else None

    cur_period = re.search(r'第(\d+)期', text).group(1)

    # 判断上期挂没挂
    hit = True
    if history:
        last_kill = history[-1].get('kill')
        if last_kill and tail is not None:
            o_big = tail >= 5
            o_odd = tail % 2 == 1
            opened_ss = ("大" if o_big else "小") + ("单" if o_odd else "双")
            if opened_ss == last_kill:
                hit = False  # 挂了

    # 挂了 → 清空重发
    if not hit:
        history.clear()

    # 记录本期
    history.append({'period': cur_period, 'a': p[0], 'b': p[1], 'c': p[2]})

    # 不足3期补位
    while len(history) < 3:
        history.insert(0, {'period': '0', 'a': 0, 'b': 0, 'c': 0})

    # 算法：第3期a + 第2期b + 最新期末位 = value
    a3 = history[-3]['a']
    b2 = history[-2]['b']
    cur = history[-1]['c']
    val = (a3 + b2 + cur) % 10

    big = val >= 5
    odd = val % 2 == 1
    kill_ss = ("小" if big else "大") + ("双" if odd else "单")

    history[-1]['kill'] = kill_ss

    # 发消息
    if tail is not None and opened is not None:
        emoji = "🀄" if hit else "🍉"
        msg = f"第{cur_period}期杀{kill_ss}{emoji}{opened}"
    else:
        msg = f"第{cur_period}期杀{kill_ss}"

    await client.send_message(TARGET, msg)

print("启动中...")
client.start()
client.run_until_disconnected()
