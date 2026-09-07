from telethon import TelegramClient, events
from telethon.sessions import StringSession
import json
import os

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"

client = TelegramClient(StringSession("1BVtsOJwBu49t0kwYRsMp3tbGg1Ulu0Vyxox-C5bMS0vkEZOZmhwI9YSlHsXWgpyHwlLECg36zd_yiITwUkMjaDsI7wR6NtyfIRVQLy5KT9HqTMfUXkmKmcGiaDpdIwR8i79oCIi-U4K0ynrTJPsuZOx9xOYXrFBvdKceeD2FYStw1q3CkQouCc2jsPVntT2r_DvbsFARjCrcHlKJaqMI5G02i9JtDIpVtqEATjw0BvfX3c0ouDja2eYkHFCflqi04qg65ZRbtDTX4lOgQ-ZGrX4RCGY7LLNwCWRpqWBpjpvTGDi-1t5YWDz1X9lNpbucYCj7_bfUqsFvRK3whir1l7-Zs9_xi1A="), api_id, api_hash)

TARGET = "@dd28"
ADMIN = None  # 你自己的TG用户ID，后面可以填

# 状态存储
history = []          # 存最近20条开奖记录
current_streak = []   # 当前连续命中记录
MAX_RECORDS = 20

def parse_result(text):
    """
    从 @dd28 的消息里提取期号和开奖号码
    消息格式举例：第20240101期 开奖 1 2 3 4 5
    返回: (期号末位, a球, b球) 或 None
    """
    try:
        lines = text.strip().split('\n')
        for line in lines:
            if '期' in line and ('开' in line or '开奖' in line):
                # 提取期号
                import re
                issue_match = re.search(r'第(\d+)期', line)
                if not issue_match:
                    return None
                issue_num = issue_match.group(1)
                issue_last = int(issue_num[-1])  # 期号末位

                # 提取号码
                nums = re.findall(r'\d+', line)
                if len(nums) < 3:
                    return None
                # 假设 a球=第一个号码, b球=第二个号码
                a_ball = int(nums[-2]) if len(nums) >= 2 else int(nums[0])
                b_ball = int(nums[-1])

                return (issue_last, a_ball, b_ball)
    except:
        pass
    return None

def calc_value(history_list):
    """
    算法：第3期a球 + 第2期b球 + 最新期号末位 = value
    杀完全相反组合
    """
    if len(history_list) < 3:
        return None, "等够3期数据才开始"

    entry_3 = history_list[-3]  # 第3期a球
    entry_2 = history_list[-2]  # 第2期b球
    entry_1 = history_list[-1]  # 最新期（取期号末位）

    a_3 = entry_3[1]  # 第3期a球
    b_2 = entry_2[2]  # 第2期b球
    issue_last = entry_1[0]  # 最新期号末位

    value = (a_3 + b_2 + issue_last) % 10  # 取个位
    kill = (value + 5) % 10  # 完全相反组合（0↔5, 1↔6, 2↔7, 3↔8, 4↔9）

    return value, kill

@client.on(events.NewMessage(chats=TARGET))
async def on_new_result(event):
    """监听 @dd28 新消息"""
    global history, current_streak

    parsed = parse_result(event.message.text)
    if not parsed:
        return  # 解析不了就跳过

    issue_last, a_ball, b_ball = parsed
    history.append((issue_last, a_ball, b_ball))

    # 满20条重置
    if len(history) >= MAX_RECORDS:
        history = history[-3:]  # 只保留最近3期用于计算

    if len(history) < 3:
        return  # 数据不够，不发

    value, kill = calc_value(history)
    if value is None:
        return

    # 判断上一期杀的对错
    # 这里需要根据实际开奖结果判断 kill 是否命中
    # 简化逻辑：假设最新一期开奖号码的某位 == kill 就是杀错
    # 实际你需要根据 @dd28 的具体规则调整

    # 发送报数
    msg = f"📊 自动报数\n"
    msg += f"期号末位: {issue_last} | a球: {a_ball} | b球: {b_ball}\n"
    msg += f"计算: 第3期a({history[-3][1]}) + 第2期b({history[-2][2]}) + 期号末位({issue_last}) = {history[-3][1] + history[-2][2] + issue_last} → value={value}\n"
    msg += f"🔪 杀: {kill}（反组合）\n"
    msg += f"📈 连中: {len(current_streak)} 条"

    # 发给自己的保存消息
    me = await client.get_me()
    await client.send_message(me.id, msg)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('✅ 自动报数已启动，监听 @dd28 中...')
    print("收到 /start")

@client.on(events.NewMessage(pattern='/status'))
async def status(event):
    await event.respond(f'📊 已记录 {len(history)} 期数据，当前连中 {len(current_streak)} 条')

print("启动中...")
client.start()
client.run_until_disconnected()
