from telethon import TelegramClient, events
from telethon.sessions import StringSession

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"

# 直接用你刚刚生成的这串新密码
client = TelegramClient(StringSession("1BVtsOJwBu49t0kwYRsMp3tbGg1Ulu0Vyxox-C5bMS0vkEZOZmhwI9YSlHsXWgpyHwlLECg36zd_yiITwUkMjaDsI7wR6NtyfIRVQLy5KT9HqTMfUXkmKmcGiaDpdIwR8i79oCIi-U4K0ynrTJPsuZOx9xOYXrFBvdKceeD2FYStw1q3CkQouCc2jsPVntT2r_DvbsFARjCrcHlKJaqMI5G02i9JtDIpVtqEATjw0BvfX3c0ouDja2eYkHFCflqi04qg65ZRbtDTX4lOgQ-ZGrX4RCGY7LLNwCWRpqWBpjpvTGDi-1t5YWDz1X9lNpbucYCj7_bfUqsFvRK3whir1l7-Zs9_xi1A="), api_id, api_hash)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Bot 跑通了！')
    print("收到 /start")

print("启动中...")
client.start()
client.run_until_disconnected()
