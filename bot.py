import asyncio
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import re
import logging

# 抑制第三方库日志，避免乱码写入 stdout
logging.basicConfig(level=logging.WARNING)
logging.getLogger('telethon').setLevel(logging.ERROR)

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
    open_sm = re.search(r'\d\+\d\+\d=(\d+)', text)
    open_num = int(open_sm.group(1)) if open_sm else None
    sm = re.search(r'(\d)\+(\d)\+(\d)=', text)
    if not sm:
        return None
    last = int(str(num)[-1])
    a = int(sm.group(1))
    b = int(sm.group(2))
    return (num, last, a, b, open_num)

SMALL_ODD  = {1,3,5,7,9,11,13}
SMALL_EVEN = {0,2,4,6,8,10,12}
BIG_EVEN   = {14,16,18,20,22,24,26}
BIG_ODD    = {15,17,19,21,23,25,27}

def get_type(n):
    if n in SMALL_ODD:  return '小单'
    if n in SMALL_EVEN: return '小双'
    if n in BIG_EVEN:   return '大双'
    if n in BIG_ODD:    return '大单'
    return ('大' if n >= 14 else '小') + ('双' if n % 2 == 0 else '单')

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

    pred_num = p[0] + 1
    pred_type = calc(history)
    results.append((pred_num, pred_type))

    if len(results) >= WINDOW:
        send_results = results[:WINDOW]
        results = []
        history = history[-3:]
    else:
        send_results = results

    lines = []
    for pred_num_i, pred_type_i in send_results:
        open_result = None
        for rec in history:
            if rec[0] == pred_num_i and rec[4] is not None:
                open_result = rec[4]
                break
        line = f"第{pred_num_i}期：杀{pred_type_i}"
        if open_result is not None:
            if get_type(open_result) == pred_type_i:
                line += "🍉"
            else:
                line += f"🀄开{open_result}"
        lines.append(line)

    msg = "\n".join(lines)
    await client.send_message(TARGET, msg)

async def main():
    await client.start()
    print("已连接，等待消息...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
