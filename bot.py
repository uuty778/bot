from telethon import TelegramClient, events
from telethon.sessions import StringSession
import re

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"

client = TelegramClient(StringSession("1BVtsOJwBu49t0kwYRsMp3tbGg1Ulu0Vyxox-C5bMS0vkEZOZmhwI9YSlHsXWgpyHwlLECg36zd_yiITwUkMjaDsI7wR6NtyfIRVQLy5KT9HqTMfUXkmKmcGiaDpdIwR8i79oCIi-U4K0ynrTJPsuZOx9xOYXrFBvdKceeD2FYStw1q3CkQouCc2jsPVntT2r_DvbsFARjCrcHlKJaqMI5G02i9JtDIpVtqEATjw0BvfX3c0ouDja2eYkHFCflqi04qg65ZRbtDTX4lOgQ-ZGrX4RCGY7LLNwCWRpqWBpjpvTGDi-1t5YWDz1X9lNpbucYCj7_bfUqsFvRK3whir1l7-Zs9_xi1A="), api_id, api_hash)

TARGET = "@dd28"
history = []
current_streak = []
MAX_RECORDS = 20

def unbold(text):
    bold_map = {
        '𝟬':'0','𝟭':'1','𝟮':'2','𝟯':'3','𝟰':'4','𝟱':'5',
        '𝟲':'6','𝟳':'7','𝟴':'8','𝟵':'9'
    }
    for k, v in bold_map.items():
        text = text.replace(k, v)
    return text

def parse_result(text):
    try:
        text = unbold(text)
        issue_match = re.search(r'第(\d+)期', text)
        if not issue_match:
            return None
        issue_num = issue_match.group(1)
        issue_last = int(issue_num[-1])
        sum_match = re.search(r'(\d)\+(\d)\+(\d)=(\d+)', text)
        if not sum_match:
            return None
        a_ball = int(sum_match.group(1))
        b_ball = int(sum_match.group(2))
        return (issue_last, a_ball, b_ball)
    except:
        return None

def calc_value(history_list):
    if len(history_list) < 3:
        return None, "等够3期数据"
    entry_3 = history_list[-3]
    entry_2 = history_list[-2]
    entry_1 = history_list[-1]
    a_3 = entry_3[1]
    b_2 = entry_2[2]
    issue_last = entry_1[0]
    value = (a_3 + b_2 + issue_last) % 10
    kill = (value + 5) % 10
    return value, kill

@client.on(events.NewMessage(chats=TARGET))
async def on_new_result(event):
    global history, current_streak
    parsed = parse_result(event.message.text)
    if not parsed:
        return
    issue_last, a_ball, b_ball = parsed
    history.append((issue_last, a_ball, b_ball))
    if len(history) >= MAX_RECORDS:
        history = history[-3:]

    value, kill = calc_value(history)
    if value is None:
        return

    latest_a = history[-1][1]
    if latest_a == kill:
        history = []
        current_streak = []
        result = "🍉 杀错！清空重来"
    else:
        current_streak.append(1)
        result = f"🀄 命中！连中 {len(current_streak)}"

    msg = (
        f"📊 自动报数\n"
        f"期号末位: {issue_last} | 开奖: {a_ball}+{b_ball}\n"
        f"计算: 第3期a({history[-3][1]}) + 第2期b({history[-2][2]}) + 期号末位({issue_last}) = {history[-3][1]+history[-2][2]+issue_last} → value={value}\n"
        f"🔪 杀: {kill}（反组合）\n"
        f"{result}"
    )
    await client.send_message(TARGET, msg)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('✅ 自动报数已启动，监听 @dd28 中...')

@client.on(events.NewMessage(pattern='/status'))
async def status(event):
    await event.respond(f'📊 已记录 {len(history)} 期，连中 {len(current_streak)} 条')

print("启动中...")
client.start()
client.run_until_disconnected()
