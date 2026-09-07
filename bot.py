from telethon import TelegramClient, events, Button
import requests, json, time, os, urllib3
urllib3.disable_warnings()

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"
targets = "@dd28"

history = []
stats = {"total":0,"win":0,"lose":0}
last_expect = None
running = False

def fetch():
    try:
        r = requests.get("https://pc28.help/api/kj.json?nbr=300", timeout=10)
        if r.status_code == 200:
            d = r.json()["data"]
            out = []
            for i in d:
                p = i["number"].replace(",", "+").split("+")
                a,b,c = int(p[0]),int(p[1]),int(p[2])
                out.append({"expect":i["nbr"],"number1":a,"number2":b,"number3":c,"final_result":int(i["num"]) if i["num"] else a+b+c})
            return out
    except: pass
    return None

def get_type(v):
    return ("大" if v>=14 else "小")+("单" if v%2 else "双")

def opp(c):
    return ("大" if c[0]=="小" else "小")+("单" if c[1]=="双" else "双")

def calc_kill(d):
    if not d or len(d)<3: return None
    v = d[2]["number1"]+d[1]["number2"]+int(d[0]["expect"][-1])
    return opp(get_type(v))

def build_msg():
    lines = []
    for h in history:
        if len(h)>2 and h[2]:
            lines.append(f"{h[0]}期杀{h[1]} {h[2]} 开{h[3]}")
        else:
            lines.append(f"{h[0]}期杀{h[1]} ⏳")
    return "\n".join(lines) if lines else "暂无"

async def send_single(client, text):
    for t in targets.split(","):
        try: await client.send_message(t.strip(), text)
        except: pass

async def loop_task(client):
    global running, last_expect, history, stats
    while running:
        try:
            data = fetch()
            if not data or len(data)<3:
                await asyncio.sleep(5); continue
            cur = data[0]
            if cur["expect"] == last_expect:
                await asyncio.sleep(3); continue
            ct = get_type(cur["final_result"])
            jl = False
            if last_expect and history:
                lk = history[-1][1]
                if lk == ct:
                    history[-1][2]="🍉"; stats["lose"]+=1; jl=True
                else:
                    history[-1][2]="🀄"; stats["win"]+=1; stats["total"]+=1
                history[-1][3]=cur["final_result"]
            if jl:
                nk = calc_kill(data)
                if nk:
                    ni = str(int(cur["expect"])+1)
                    history = [[ni,nk,"",""]]
                    stats = {"total":0,"win":0,"lose":0}
            if len(history)>=20:
                history=[]; stats={"total":0,"win":0,"lose":0}
            await send_single(client, build_msg())
            last_expect = cur["expect"]
            await asyncio.sleep(3)
        except:
            await asyncio.sleep(10)

async def main():
    global running, last_expect, history
    client = TelegramClient("bot_session", api_id, api_hash)
    await client.start()
    print("登录成功")

    d = fetch()
    if d:
        k = calc_kill(d)
        ni = str(int(d[0]["expect"])+1)
        history = [[ni,k,"",""]]

    @client.on(events.NewMessage(pattern=r'^/start'))
    async def cmd(event):
        global running
        if not running:
            running = True
            asyncio.create_task(loop_task(client))
        await event.reply("▶️ 已启动自动报数")

    @client.on(events.NewMessage(pattern=r'^/stop'))
    async def stp(event):
        global running
        running = False
        await event.reply("⏹ 已停止")

    @client.on(events.NewMessage(pattern=r'^/status'))
    async def sta(event):
        rate = f"{stats['win']/stats['total']*100:.1f}%" if stats['total']>0 else "0%"
        await event.reply(f"总:{stats['total']} 中:{stats['win']} 挂:{stats['lose']} 胜率:{rate}")

    await client.run_until_disconnected()

import asyncio
asyncio.run(main())
