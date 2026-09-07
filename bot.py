from telethon import TelegramClient, events
from telethon.sessions import StringSession

api_id = 26048878
api_hash = "735a5e369c70f328eab9ad3c52c3b5cf"

# 下面这行是直接用你刚拿到的字符串，不用存文件
client = TelegramClient(StringSession("1BVtsOJwBu7BHZ4dw5wrqj2vMGDM-NssuixY7R9tfQAyhxi28e39nI21N01khdIphhE9-af078ZPXNnMNIUby83b5ZE-i6QYjHWKGUKa9JJOxyF76qyakjJubnaEOHo2IHy-aQ6QUIZZIsUTfgb8uwgfVnOtIQVzOHM-rJmCWuy3w5ZNXMzBndLvCmr3G-LdeuwWRfXuErSGEh3uovNjbrRbLR5pdQwXMYoCL7V882Y8K93WHvduo6AD2zd_M_dqzKq4E81j8SDseaug09B1e4IM_kSO8dv0nT90xNoPqzKw-xev9Bj_BPLv2neZtqobtgxE__CFt5jHQeWEXQo-jdkSYgolrrv_9e4="), api_id, api_hash)

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond('Bot 跑通了！')
    print("收到 /start")

print("启动中...")
client.start()
client.run_until_disconnected()
