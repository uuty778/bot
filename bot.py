from telethon import TelegramClient, events, sync
from telethon.sessions import StringSession
import re
import sys

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"
session_str = "1BVtsOHoBu8T_MNT_EsBNs7bOarzmzCMnD_VPpKf-l_mF6WQxRMsslksrbEZr1DyI2sYPpdVeoux_TcC1KbJU5vAgWBpeRaDbEGm5UFf8U4ddvS_Qt4RHvO_28EXG8ZxZJ8eDKVI5esk9nWrFq-WLQA_OvwTCywxMZG5KqJOfWn05vxuhYndHXG3xyNAMNoXm3YvweAvVRg2OovCdISPrZtMLM1qdIA2CtgdS7LzCbf2iLJ5ehhvB9wrmUA69dkpfNtLwVqHNegncApPFIkTE9scB0aE-nAADWSoR4uVy3YJ3DumQ-Y7iXS3j1lSeInFrXd8-4M4XV2NZtEMdcJHydOaY_mkVULw="

TARGET = "@dd28"
history = []
results = []

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
    sm = re.search(r'(\d)\s*[+＋]\s*(\d)\s*[+＋]\s*(\d)\s*=', text)
    if not sm:
        return None
    a = int(sm.group(1))
    b = int(sm.group(2))
    c = int(sm.group(3))
    open_sm = re.search(r'=\s*(\d+)', text)
    open_num = int(open_sm.group(1)) if open_sm else None
    return (num, a, b, c, open_num)

def getCombination(total):
    if total in (1, 3, 5, 7, 9, 11, 13):
        return '小单'
    elif total in (0, 2, 4, 6, 8, 10, 12):
        return '小双'
    elif total in (14, 16, 18, 20, 22, 24, 26):
        return '大双'
    elif total in (15, 17, 19, 21, 23, 25, 27):
        return '大单'
    return '小单'

def predict(history):
    if len(history) < 1:
        return None
    latest = history[-1]
    a, c, open_num = latest[1], latest[3], latest[4]
    if open_num is None:
        return None

    val = a + c + (open_num % 10)

    if val in (1, 3, 5, 7, 9, 11, 13):
        kill_type = '大双'
        double_group = ['小双', '大单']
    elif val in (0, 2, 4, 6, 8, 10, 12):
        kill_type = '大单'
        double_group = ['小单', '大双']
    elif val in (14, 16, 18, 20, 22, 24, 26):
        kill_type = '小单'
        double_group = ['小双', '大单']
    elif val in (15, 17, 19, 21, 23, 25, 27):
        kill_type = '小双'
        double_group = ['小单', '大双']
    else:
        kill_type = '大双'
        double_group = ['小双', '大单']

    return kill_type, double_group

def build_line(pred_num, pred_type, double_group, history):
    short_num = str(pred_num)[-2:]
    open_result = None
    for rec in history:
        if rec[0] == pred_num and rec[4] is not None:
            open_result = rec[4]
            break
    if open_result is None:
        return short_num + "期杀" + pred_type
    combo = getCombination(open_result)
    if combo == pred_type:
        tail = "🍉" + str(open_result)
    else:
        if combo in double_group:
            tail = "🀄" + str(open_result)
        else:
            tail = "🀄" + str(open_result)
    return short_num + "期杀" + pred_type + tail

client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('自动报数已启动！')

@client.on(events.NewMessage(chats=TARGET))
@client.on(events.MessageEdited(chats=TARGET))
async def handler(event):
    global history, results
    text = event.message.text or ""
    p = parse(text)
    if not p:
        return
    if history:
        last = history[-1]
        if last[0] == p[0] and last[4] == p[4]:
            return
    history.append(p)
    if len(history) > 30:
        history = history[-30:]

    pred_num = p[0] + 1
    res = predict(history)
    if res is None:
        return
    pred_type, double_group = res

    results.append((pred_num, pred_type, double_group))

    # 叠到10层就清空，只发最新这一条
    if len(results) >= 10:
        results = [(pred_num, pred_type, double_group)]
        await client.send_message(TARGET, build_line(pred_num, pred_type, double_group, history))
    else:
        lines = [build_line(pred_num_i, pred_type_i, double_i, history) for (pred_num_i, pred_type_i, double_i) in results]
        await client.send_message(TARGET, "\n".join(lines))

print("启动中...")

with client:
    try:
        client.connect()
        if not client.is_user_authorized():
            print("session 未授权！")
            sys.exit(1)
        me = client.get_me()
        print("登录成功: " + me.first_name + " @" + me.username)
    except Exception as e:
        print("失败: " + str(e))
        sys.exit(1)
    client.run_until_disconnected()
