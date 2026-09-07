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
    print("收到消息:", event.message.text[:50] if event.message.text else "无文本")
    text = event.message.text
    if not text:
        return

    text = unbold(text)

    pm = re.search(r'第(\d+)期', text)
    if not pm:
        print("没匹配到期号")
        return
    cur_period = pm.group(1)
    print(f"期号: {cur_period}")

    om = re.search(r'开(\d+)', text)
    if not om:
        print("没匹配到开奖")
        return
    opened = int(om.group(1))
    tail = opened % 10
    print(f"开奖: {opened} 尾数: {tail}")

    sm = re.search(r'(\d)\+(\d)\+(\d)=', text)
    if not sm:
        print("没匹配到a+b+c")
        return
    a = int(sm.group(1))
    b = int(sm.group(2))
    c = int(sm.group(3))
    print(f"a={a} b={b} c={c}")

    # 判断上期
    hit = True
    if len(history) >= 2 and len(history[-2]) >= 5:
        prev_kill = history[-2][4]
        o_big = tail >= 5
        o_odd = tail % 2 == 1
        opened_ss = ("大" if o_big else "小") + ("单" if o_odd else "双")
        if opened_ss == prev_kill:
            hit = False
        print(f"上期杀{prev_kill} 本期开{opened_ss} {'挂' if not hit else '中'}")

    # 挂了清空
    if not hit:
        history.clear()
        print("挂了，清空")

    # 记录
    history.append([c, a, b])
    if len(history) > 3:
        history = history[-3:]

    while len(history) < 3:
        history.insert(0, [0, 0, 0])

    # 算法
    a3 = history[-3][1]
    b2 = history[-2][2]
    cur = history[-1][0]
    val = (a3 + b2 + cur) % 10

    kill_ss = ("小" if val >= 5 else "大") + ("双" if val % 2 == 1 else "单")
    print(f"算法: a3={a3} b2={b2} cur={cur} val={val} 杀{kill_ss}")

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
    msg = f"第{cur_period}期杀{kill_ss} {shuangzu}{emoji}{opened}"
    print(f"准备发送: {msg}")
    await client.send_message(TARGET, msg)
    print("发送完成")

print("启动中...")
client.start()
client.run_until_disconnected()
