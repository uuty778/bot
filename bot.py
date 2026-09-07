from telethon import TelegramClient
import asyncio
import requests
import os
import json
import re

# ==================== 配置 ====================
API_ID = 26048878
API_HASH = "735a5e369c70f328eab9ad3c52c3b5cf"
SESSION_FILE = "report_session"
TARGETS = "@dd28"

# 代理
SOCKS5_PROXY = {
    "server": "207.57.132.47",
    "port": 27790,
    "username": "1884e79a4b59",
    "password": "bcb15199-1fac-493e-bd4f-99bafa8376a0",
}

REPORT_FILE = "report_history.json"
# ==============================================

history = []          # 每条: [期号, 杀组, 状态, 开奖值]
last_processed = ""

def get_telethon_proxy():
    return (
        "socks5",
        SOCKS5_PROXY["server"],
        SOCKS5_PROXY["port"],
        True,
        SOCKS5_PROXY["username"],
        SOCKS5_PROXY["password"],
    )

def apply_requests_proxy():
    proxy_url = f"socks5://{SOCKS5_PROXY['username']}:{SOCKS5_PROXY['password']}@{SOCKS5_PROXY['server']}:{SOCKS5_PROXY['port']}"
    requests.proxies = {"http": proxy_url, "https": proxy_url}
    requests.verify = False
    _original_get = requests.get
    def _proxied_get(*args, **kwargs):
        kwargs.setdefault("proxies", requests.proxies)
        kwargs.setdefault("verify", False)
        return _original_get(*args, **kwargs)
    requests.get = _proxied_get

def get_type(total):
    return ("大" if total >= 5 else "小") + ("单" if total % 2 == 1 else "双")

def unbold(t):
    bold_map = {'𝟬':'0','𝟭':'1','𝟮':'2','𝟯':'3','𝟰':'4','𝟱':'5','𝟲':'6','𝟳':'7','𝟴':'8','𝟵':'9'}
    for k, v in bold_map.items():
        t = t.replace(k, v)
    return t

# ========== 你的算法 ==========
def calc_kill(data):
    """
    data: 最近开奖列表，data[0]=最新, data[1]=上期, data[2]=上上期
    算法：第3期a + 第2期b + 最新期号末位 = value，杀相反
    """
    global history
    if not data or len(data) < 3:
        return None
    try:
        # data[0]=最新, data[1]=第2期, data[2]=第3期
        cur = data[0]
        a3 = data[2].get("number1", 0)   # 第3期a
        b2 = data[1].get("number2", 0)   # 第2期b
        cur_tail = int(cur.get("expect", "0")[-1])  # 最新期号末位

        val = (a3 + b2 + cur_tail) % 10
        kill_ss = get_type(val)
        # 杀相反
        reverse_map = {
            "大单": "小双", "小双": "大单",
            "大双": "小单", "小单": "大双"
        }
        kill = reverse_map.get(kill_ss, kill_ss)
        print(f"📊 算法: 第3期a={a3} 第2期b={b2} 期号末位={cur_tail} → val={val} → 杀{kill}")
        return kill
    except Exception as e:
        print(f"计算错误: {e}")
        return None

def fetch_data():
    try:
        r = requests.get("https://pc28.help/api/kj.json?nbr=300", timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = data.get('data') if isinstance(data, dict) else None
            if results:
                converted = []
                for item in results:
                    number = item.get('number', '0+0+0')
                    sep = '+' if '+' in number else ','
                    parts = number.split(sep)
                    a = int(parts[0]) if len(parts) > 0 else 0
                    b = int(parts[1]) if len(parts) > 1 else 0
                    c = int(parts[2]) if len(parts) > 2 else 0
                    num = item.get('num')
                    final = int(num) if num not in (None, '') else (a + b + c)
                    converted.append({
                        'expect': item.get('nbr', ''),
                        'number1': a,
                        'number2': b,
                        'number3': c,
                        'final_result': final,
                    })
                if converted:
                    print(f"📡 最新: {converted[0].get('expect', '')} ({a},{b},{c})")
                return converted
    except Exception as e:
        print(f"API请求失败: {e}")
    return None

def build_message():
    lines = []
    shuangzu_map = {
        "小单": "小双大单",
        "小双": "小单大双",
        "大单": "大双小单",
        "大双": "大单小双"
    }
    for h in history:
        kill = h[1]
        shuangzu = shuangzu_map.get(kill, "")
        if len(h) > 2 and h[2]:
            status = h[2]
            value = h[3]
            lines.append(f"{h[0]}期杀{kill} {shuangzu}{status}{value}")
        else:
            lines.append(f"{h[0]}期杀{kill} {shuangzu}⏳")
    return "\n".join(lines) if lines else "暂无数据"

async def send_message(client, entity, msg):
    try:
        await client.send_message(entity, msg)
        print(f"📤 已发送: {msg}")
        return True
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

async def main():
    global history, last_processed

    print("=" * 50)
    print("🤖 自动报数机器人")
    print(f"📌 代理: {SOCKS5_PROXY['server']}:{SOCKS5_PROXY['port']}")
    print("=" * 50)

    apply_requests_proxy()

    history = []
    last_processed = ""

    proxy = get_telethon_proxy()
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH, proxy=proxy)
    await client.start()
    me = await client.get_me()
    print(f"✅ 已登录: {me.first_name}")

    entity = await client.get_entity(TARGETS)
    print(f"✅ 目标群: {TARGETS}")

    print("📡 监听中...\n")

    while True:
        try:
            results = fetch_data()
            if not results or len(results) < 3:
                await asyncio.sleep(5)
                continue

            current = results[0]
            current_expect = current.get('expect', '')
            current_value = current.get('final_result', 0)
            current_type = get_type(current_value)

            if not current_expect or current_expect == last_processed:
                await asyncio.sleep(3)
                continue

            print(f"📦 新期: {current_expect} 开奖: {current_value}")

            # 结算上期
            just_lose = False
            if last_processed and len(history) > 0:
                last_kill = history[-1][1]
                if last_kill == current_type:
                    status = "🍉"
                    just_lose = True
                else:
                    status = "🀄"
                    just_lose = False
                history[-1][2] = status
                history[-1][3] = current_value
                print(f"📊 {last_processed}期 杀{last_kill} 开{current_type} {status}{current_value}")

            # 挂了清空
            if just_lose:
                history.clear()
                print("🍉 挂了，清空")

            # 算杀组
            kill = calc_kill(results)
            if kill:
                predict_issue = str(int(current_expect) + 1)
                history.append([predict_issue, kill, "", ""])

            # 发消息
            msg = build_message()
            if msg:
                await send_message(client, entity, msg)

            last_processed = current_expect
            await asyncio.sleep(3)

        except Exception as e:
            print(f"❌ 错误: {e}")
            await asyncio.sleep(10)

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
