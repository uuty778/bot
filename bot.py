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

@client.on(events.NewMessage(pattern='/start'))
async def start(ev):
    await ev.respond('自动报数已启动！')

@client.on(events.NewMessage(chats=TARGET))
async def handler(ev):
    global history
    text = ev.message.text
    p = parse(text)
    if not p:
        return

    # 当期开奖号码
    om = re.search(r'开(\d+)', text)
    opened = int(om.group(1)) if om else None
    tail = opened % 10 if opened is not None else None

    # 上期杀的
    last_kill = history[-1][3] if (history and len(history[-1]) > 3) else None

    # 判断上期挂没挂：上期杀的 = 本期开的大小单双 → 挂
    chain_broken = False
    if last_kill and tail is not None:
        o_big = tail >= 5
        o_odd = tail % 2 == 1
        opened_ss = ("大" if o_big else "小") + ("单" if o_odd else "双")
        if opened_ss == last_kill:
            chain_broken = True

    # 记录本期
    history.append((p[0], p[1], p[2]))

    # 挂了 → 只留最近3期重算（断链）
    if chain_broken:
        history = history[-3:]

    # 不足3期补位
    while len(history) < 3:
        history.insert(0, (0, 0, 0))

    # 算法：第3期a + 第2期b + 最新期末位 = value
    a3 = history[-3][1]
    b2 = history[-2][2]
    cur = history[-1][0]
    val = (a3 + b2 + cur) % 10

    # value → 大小单双 → 杀相反
    big = val >= 5
    odd = val % 2 == 1
    kill_size = "小" if big else "大"
    kill_parity = "双" if odd else "单"
    kill_ss = kill_size + kill_parity

    history[-1] = (history[-1][0], history[-1][1], history[-1][2], kill_ss)

    # 发下一期预测
    cur_period = re.search(r'第(\d+)期', text).group(1)
    next_period = str(int(cur_period) + 1)
    prefix = "🔄" if chain_broken else ""
    await client.send_message(TARGET, f"{prefix}第{next_period}期杀{kill_ss}")

client.start()
client.run_until_disconnected()
