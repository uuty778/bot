from telethon import TelegramClient, events, sync
from telethon.sessions import StringSession
import re
import sys
import asyncio
import traceback
import urllib.request
import json

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"
session_str = "1BVtsOHIBu3gEssUc9irbBC-w70gHKfOgYDhcm9lOJAsU-sR8cGHBIgcvqNBzjU9QGyOeySXx9wi_wQeVrnydm1NqjZM3zrgwjcx1bt59htsDlYz_T-3kQXPpl_bbEQ87k1EmR8AGZyK7j8x2L5I0O_Sbryvxzukpgts-2-RcXTDLC4syU6af-OVG-HSbKCoCTuu_ltyUhAIoeo21dpuKgF-vSGI0k7IFtSA5U6oEcWv21wyP4TlTpPuyQkwBvtrZCJNOaamx1TGo8DMJeTiF-hhpOJfVN7nks7HMyt9G9XzjeUztLTDPjmH-ur895O9NCyVUGRGTrJvuNR4srZcVk2Aka-epg1o="

TARGET = "@qwpc8"
CUSTOM_PREFIX = "神天降而来"
history = []
results = []
processed_ids = set()

DELAY_SECONDS = 30

API_URL = "https://pc28.help/api/kj.json?nbr=1"

bold_map = {
    '𝟬': '0', '𝟭': '1', '𝟮': '2', '𝟯': '3', '𝟰': '4',
    '𝟱': '5', '𝟲': '6', '𝟳': '7', '𝟴': '8', '𝟵': '9'
}

def unbold(text):
    for k, v in bold_map.items():
        text = text.replace(k, v)
    text = text.replace('**', '')
    return text

def parse(text):
    text = unbold(text)

    iss = re.search(r'第\**\s*(\d{4,})\s*\**期', text)
    if not iss:
        iss = re.search(r'(\d{6,})', text)
    if not iss:
        print(f"[PARSE] ❌ 没找到期号。文本片段: {text[:120]}")
        return None
    num = int(iss.group(1))

    sm = re.search(r'(\d)\s*[+＋]\s*(\d)\s*[+＋]\s*(\d)\s*=\s*(\d+)', text)
    if not sm:
        print(f"[PARSE] ❌ 没匹配到 a+b+c=d。文本: {text[:150]}")
        return None
    a = int(sm.group(1))
    b = int(sm.group(2))
    c = int(sm.group(3))
    open_num = int(sm.group(4))

    print(f"[PARSE] ✅ 第{num}期 A={a} B={b} C={c} 开奖={open_num}")
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

def getOpposite(combo_type):
    opposite_map = {
        '小单': '大双',
        '大双': '小单',
        '小双': '大单',
        '大单': '小双'
    }
    return opposite_map.get(combo_type, '小单')

def predict(history):
    if len(history) < 1:
        return None
    recent = history[-3:] if len(history) >= 3 else history
    a_total = sum(rec[1] for rec in recent)
    b_total = sum(rec[2] for rec in recent)
    c_total = sum(rec[3] for rec in recent)
    final_sum = a_total + b_total + c_total
    while final_sum > 27:
        final_sum -= 27
    combo = getCombination(final_sum)
    kill_type = getOpposite(combo)
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
        tail = "🀄" + str(open_result)
    return short_num + "期杀" + pred_type + tail

def fetch_latest():
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            items = data.get("data", [])
            if not items:
                return None
            it = items[0]
            num = int(it["nbr"])
            a, b, c = map(int, it["number"].split("+"))
            open_num = int(it["num"])
            return (num, a, b, c, open_num)
    except Exception as e:
        print(f"[API] ❌ 拉取失败: {e}")
        return None

client = TelegramClient(StringSession(session_str), api_id, api_hash)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('动！')

async def delayed_send(pred_num, pred_type, double_group, history_snapshot):
    try:
        await asyncio.sleep(DELAY_SECONDS)

        global results

        should_clear = False
        if results and history_snapshot:
            last_pred_num, last_pred_type, last_double_group = results[-1]
            for rec in history_snapshot:
                if rec[0] == last_pred_num and rec[4] is not None:
                    open_num = rec[4]
                    combo = getCombination(open_num)
                    print(f"[CHECK] 第{last_pred_num}期开奖={open_num} combo={combo} 杀{last_pred_type}")
                    if combo == last_pred_type:
                        print(f"[CHECK] 🍉 杀到了，清空")
                        should_clear = True
                    else:
                        print(f"[CHECK] 🀄 没杀到，继续叠")
                    break

        if should_clear:
            results.clear()

        results.append((pred_num, pred_type, double_group))

        lines = [build_line(pn, pt, dg, history_snapshot) for (pn, pt, dg) in results]
        msg = CUSTOM_PREFIX + "\n" + "\n".join(lines)
        await client.send_message(TARGET, msg)

        print(f"[SEND] ✅ 第{pred_num}期 发送成功，当前共{len(results)}期叠加")

    except Exception as e:
        print(f"[SEND] ❌ 发送失败: {e}")
        traceback.print_exc()

async def poll_api():
    global history, processed_ids
    last_num = None
    while True:
        try:
            p = fetch_latest()
            if p and p[0] != last_num:
                last_num = p[0]
                print(f"[API] ✅ 最新第{p[0]}期 A={p[1]} B={p[2]} C={p[3]} 开奖={p[4]}")

                if history:
                    last = history[-1]
                    if last[0] == p[0] and last[4] == p[4]:
                        await asyncio.sleep(10)
                        continue

                history.append(p)
                if len(history) > 30:
                    history = history[-30:]

                pred_num = p[0] + 1
                res = predict(history)
                if res is None:
                    await asyncio.sleep(10)
                    continue
                pred_type, double_group = res

                history_snapshot = list(history)

                asyncio.create_task(
                    delayed_send(pred_num, pred_type, double_group, history_snapshot)
                )

                print(f"[PREDICT] ✅ 预测第{pred_num}期 杀{pred_type}")

            await asyncio.sleep(10)
        except Exception as e:
            print(f"[POLL] ❌ 异常: {e}")
            traceback.print_exc()
            await asyncio.sleep(10)

print("启动中...")

with client:
    try:
        client.connect()
        if not client.is_user_authorized():
            print("❌ session 未授权！")
            sys.exit(1)
        me = client.get_me()
        print(f"✅ 登录成功: {me.first_name} @{me.username}")
        print(f"✅ 开始监听 API {TARGET} ...\n")
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        sys.exit(1)

    client.loop.create_task(poll_api())
    client.run_until_disconnected()
