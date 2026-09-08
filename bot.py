from telethon import TelegramClient, events
from telethon.sessions import StringSession
import re

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"
session_str = "1BVtsOIQBuw7QWchMeY2sYsPhrP9oLEDQRinT871ThXkDyT5A9LcTV0k_cecG3sgfRsZxvayvp3A_oKD6bR_y-NeztrsHi_frwp_HcTUFLcGuvC4QLqDpZel-R9FM_QabSGzfw_8n25m2MY0MWiq5ZgD-LQB5qRV8TeFxwCR3TVJY1acjSsttUq-tYq7B-JidWQxX0HdrEUEBGYJOTNlxgVgetV8jA2LreEX-FNacsvfPKfIDpCgLTCOcV_k8x5wiFDtrVynvR2ldqydjlXP68fGGrVZOg3mc1NbpH6lmxHDiQsIPXKAtIYSXI4ObF7J8XY8QgM0ku18zG5TTpcktDnOU8N3KjAo="

TARGET = "@dd28"
history = []
results = []
WINDOW = 10

bold_map = {
    '𝟬': '0', '𝟭': '1', '𝟮': '2', '𝟯': '3', '𝟰': '4',
    '𝟱': '5', '𝟲': '6', '𝟳': '7', '𝟴': '8', '𝟵': '9'
}

def unbold(text):
    for k, v in bold_map.items():
        text = text.replace(k, v)
    return text

def parse(text):
    text = unbold(text)
    iss = re.search(r'第(\d+)期', text)
    if not iss:
        return None
    num = int(iss.group(1))
    last = int(str(num)[-1])
    open_sm = re.search(r'=(\d+)', text)
    open_num = int(open_sm.group(1)) if open_sm else None
    sm = re.search(r'(\d)\+(\d)\+(\d)=', text)
    if not sm:
        return None
    return (num, last, int(sm.group(1)), int(sm.group(2)), open_num)

def get_type(n):
    if n <= 4:
        size = '小'
    else:
        size = '大'
    if n % 2 == 0:
        parity = '双'
    else:
        parity = '单'
    return size + parity

def calc(h):
    a3 = h[-3][2]
    b2 = h[-2][3]
    curr_num = h[-1][0]
    curr_last = h[-1][1]
    val = (a3 + b2 + curr_last) % 10
    杀号 = (10 - val) % 10
    return get_type(杀号)

client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('自动报数已启动！')

@client.on(events.NewMessage(chats=TARGET))
async def handler(event):
    global history, results
    p = parse(event.message.text)
    if not p:
        return
    if history and history[-1][0] == p[0]:
        return

    history.append(p)
    if len(history) < 4:
        return

    # 算本期预测（预测下一期）
    pred_num = p[0] + 1
    pred_type = calc(history)
    results.append((pred_num, pred_type))

    # 满了WINDOW就断开，从下一期重新开始
    if len(results) >= WINDOW:
        send_results = results[:WINDOW]
        results = []   # 清空，下一期重新叠
        history = history[-3:]  # 保留最近3期数据，供下次计算用
    else:
        send_results = results

    # 组装带开奖结果
    lines = []
    for pred_num_i, pred_type_i in send_results:
        open_result = None
        for rec in history:
            if rec[0] == pred_num_i and rec[4] is not None:
                open_result = rec[4]
                break
        if open_result is not None:
            lines.append(f"第{pred_num_i}期：杀{pred_type_i}🀄开{open_result}")
        else:
            lines.append(f"第{pred_num_i}期：杀{pred_type_i}")

    msg = "\n".join(lines)
    await client.send_message(TARGET, msg)

print("启动中...")
client.start()
client.run_until_disconnected()
