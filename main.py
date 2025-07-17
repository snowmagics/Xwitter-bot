import discord
import json
import os 
from keep_alive import keep_alive

keep_alive() 

usernames = {}

def load_usernames():
    global usernames
    try:
        with open("usernames.json", "r", encoding="utf-8") as f:
            usernames = json.load(f)
    except FileNotFoundError:
        usernames = {}

def save_usernames():
    with open("usernames.json", "w", encoding="utf-8") as f:
        json.dump(usernames, f, ensure_ascii=False)


# 設定ファイル読み込み
with open("configuration.json", "r", encoding="utf-8") as f:
    config = json.load(f)

TOKEN = os.environ["TOKEN"]
ANON_CHANNEL_ID = config["anonymous_channel_id"]
NON_ANON_CHANNEL_ID = config["non_anonymous_channel_id"]


# インテントの設定（ここが重要！）
intents = discord.Intents.default()
intents.message_content = True
intents.messages = True       # ←これが必要！！
intents.dm_messages = True    # ←これも！
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    load_usernames()
    print(f"ログイン成功！Bot名：{client.user}")

@client.event
async def on_message(message):
    # Bot自身のメッセージは無視
    if message.author == client.user:
        return
        
    # 名前登録コマンドの処理
    if message.content.startswith("/setname "):
        new_name = message.content[len("/setname "):].strip()
        if new_name == "":
            await message.channel.send("名前を入力してください。")
            return
        usernames[str(message.author.id)] = new_name
        save_usernames()
        await message.channel.send(f"名前を「{new_name}」に登録しました！")
        return
        
    # DMからのメッセージだけ処理
    if isinstance(message.channel, discord.DMChannel):
        content = message.content
        user_id = str(message.author.id)
        name = usernames.get(user_id, "風吹けば名無し")  # 登録名がなければ「匿名さん」

        # 匿名チャンネルに名前付きで投稿
        anon_channel = client.get_channel(ANON_CHANNEL_ID)
        if anon_channel:
            await anon_channel.send(f"**{name}**: {content}")

        # 非匿名チャンネルには名前つきで投稿
        non_anon_channel = client.get_channel(NON_ANON_CHANNEL_ID)
        if non_anon_channel:
            guild = client.get_guild(1343194530769276968)  # 対象のサーバーIDに置き換え
            member = guild.get_member(message.author.id) if guild else None
            if member:
                display_name = member.display_name
            else:
                display_name = message.author.name  # サーバーにいなければ通常名を使う
            await non_anon_channel.send(f"＠{display_name}({message.author.name})  {content}")

            

client.run(TOKEN)
