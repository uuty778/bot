from telethon import TelegramClient, events, sync
from telethon.sessions import StringSession
import re
import sys

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"
session_str = "1BVtsOIUBu1EfT-ycSL5Tl-TFNXd50bYfHJeLbXOxD7_szD0Rf-YU1hxhgvntDTW5FW8KptkEGsH8ubUcKK563U8lSkxuxj-0fGqAFj_5s69BNn86Yf05mkrL4XBHXgmR5YGczswpBWZqj5E-imonIggO4OVFcsrGElQrPw7Se-eClIgpd9G09rEKR4l6R2lIOad2ChbuBtCfS3M_yAt35hfejLaiZ_wE3P30Egmq6U6nkVcEpzF18JXc85Vjnru5-Plnl5h8X5vQJHOoQII7Z_V6HnMbFhSocMda_EZ255-r2_Hx4PNNV9TQnCVzGkuKGV15zxB_S23zg093N67P0rGDG6yu67k="

TARGET = "@dd28"
CUSTOM_PREFIX = "好饿"
history = []
results = []
processed_ids = set()

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
    """根据总和值返回类型"""
    if total in (1, 3, 5, 7, 9, 11, 13):
        return '小单'
    elif total in (0, 2, 4, 6, 8, 10, 12):
        return '小双'
    elif total in (14, 16, 18, 20, 22, 24, 26):
        return '大双'
    elif total in (15, 17, 19, 21, 23, 25, 27):
        return '大单'
    return '小单'

def getOpposite(combo_type):
    """返回相反类型"""
    opposite_map = {
        '小单': '大双',
        '大双': '小单',
        '小双': '大单',
        '大单': '小双'
    }
    return opposite_map.get(combo_type, '小单')

def predict(history):
    """
    新算法：
    取最近三期（不足三期用0凑）的A、B、C球分别累加
    然后 A_total + B_total + C_total = final_sum
    如果 final_sum > 27，则 final_sum - 27
    用 final_sum 对应的组合类型，杀「相反」类型
    """
    if len(history) < 1:
        return None
    
    # 取最近三期，不足三期用0填充
    recent = history[-3:] if len(history) >= 3 else history
    
    # 分别累加A、B、C
    a_total = 0
    b_total = 0
    c_total = 0
    
    for rec in recent:
        # rec格式: (num, a, b, c, open_num)
        a_total += rec[1]
        b_total += rec[2]
        c_total += rec[3]
    
    # 如果不足三期，用0凑够三期
    # 比如只有2期，就需要补1期的0,0,0
    # 只有1期，补2期的0,0,0
    if len(recent) < 3:
        # 补 (3 - len(recent)) 期的 0 值
        pass  # a_total/b_total/c_total 已经是实际值，相当于0已经默认加了
    
    final_sum = a_total + b_total + c_total
    
    # 超出27就减27（循环取模，但按你的规则是减27）
    while final_sum > 27:
        final_sum -= 27
    
    # 如果 final_sum 是 0，对应小双（按getCombination逻辑）
    # 但0也可能出现，正常处理
    
    combo = getCombination(final_sum)
    kill_type = getOpposite(combo)
    
    # double_group 保持原来的逻辑（用于展示🀄/🍉标记）
    # 杀类型对应的双组
    if kill_type in ('小单', '大双'):
        double_group = ['小双', '大单']
    else:
        double_group = ['小单', '大双']
    
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
    await event.respond('动！')

@client.on(events.NewMessage(chats=TARGET))
@client.on(events.MessageEdited(chats=TARGET))
async def handler(event):
    global history, results, processed_ids
    
    msg_id = event.message.id
    if msg_id in processed_ids:
        return
    processed_ids.add(msg_id)
    if len(processed_ids) > 100:
        processed_ids = set(list(processed_ids)[-50:])

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

    if len(results) >= 10:
        results = [(pred_num, pred_type, double_group)]
        line = build_line(pred_num, pred_type, double_group, history)
        await client.send_message(TARGET, CUSTOM_PREFIX + "\n" + line)
    else:
        lines = [build_line(pred_num_i, pred_type_i, double_i, history) for (pred_num_i, pred_type_i, double_i) in results]
        await client.send_message(TARGET, CUSTOM_PREFIX + "\n" + "\n".join(lines))

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
