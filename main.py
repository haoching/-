import nextcord
from nextcord.ext import commands
import logging
import json
from dotenv import load_dotenv
from os import environ

load_dotenv()

token = environ["TOKEN"]

client = commands.AutoShardedBot(
  command_prefix = "CTF!",
  intents = nextcord.Intents.all()
)

logging.basicConfig(
  level = logging.INFO,
  format = '[%(asctime)s] [%(levelname)s] %(message)s',
  datefmt = '%Y/%m/%d %I:%M:%S'
)

@client.event
async def on_ready() -> None:
  client.add_view(CtfQuestionButtons())
  logging.info(f"Logged in as {client.user}")

@client.event
async def on_resumed() -> None:
  logging.info(f"Connection resumed")

@client.event
async def on_connect() -> None:
  logging.info("Connected to Discord")
  await client.sync_all_application_commands()

@client.event
async def on_disconnect() -> None:
  logging.warning("Disconnected to Discord")

class CtfFlagResponseModal(nextcord.ui.Modal):
  def __init__(self, client , flag_id: str, flag: str):
    self.flag_id = flag_id
    self.flag = flag
    super().__init__(f"No. {flag_id}", timeout = None)

    self.flag_input = nextcord.ui.TextInput(
      label = "輸入答案",
      required = True,
      placeholder = "SCAICT{some_flag_here}",
    )
    self.add_item(self.flag_input)
    self.client = client
  async def callback(self, interaction: nextcord.Interaction) -> None:
    with open("user_data.json", "r", encoding = "utf-8") as f:
      user_data = json.load(f)
      print("hello")
    answered = user_data.get(str(interaction.user.id), {}).get("answered", [])
    if self.flag_id in answered:
      await interaction.response.send_message(f"小組成員已經完成 No. {self.flag_id} 了！", ephemeral = True)
      return
    if self.flag_input.value == self.flag:
      with open("user_data.json", "w", encoding = "utf-8") as f:
        user_data[str(interaction.user.id)]["score"] += 100
        user_data[str(interaction.user.id)]["answered"].append(self.flag_id)
        json.dump(user_data, f, indent = 2, ensure_ascii = False)
      flag_embed = nextcord.Embed(
        title = f"中電會迎新CTF",
        description = f"點擊下面的按鈕來回答對應題目"
      )
      with open("user_data.json", "r", encoding = "utf-8") as f:
        user_data = json.load(f)
      for group in sorted(list(user_data.values()), key = lambda data: data.get('score'), reverse = True):
        flag_embed.add_field(
          name = group.get("name"),
          value = f"Score: {group.get('score')} | Answered: {len(group.get('answered'))}",
          inline = False
        )
      await interaction.edit(embed = flag_embed, view = CtfQuestionButtons())
      #await interaction.followup.send(f"No. {self.flag_id} 答題正確，小組分數+100", ephemeral = True)
      with open('questions.json', "r", encoding = "utf-8") as f:
        questions = json.load(f)
     # 從 JSON 檔案讀取問題
      options = []
      for option in questions['options']:
        options.append(nextcord.SelectOption(label=option, value=option))
      # 創建選項按鈕
    
      select = nextcord.ui.Select(
        placeholder='請選擇一個答案',
        min_values=1,
        max_values=1,
        options=options
      )
      # 創建選擇框
      view = nextcord.ui.View()
      view.add_item(select)
      print("2")
      message = await interaction.followup.send(content=questions['question'], view=view)
      # 發送問題和選擇框
    
      def check(res):
        return True
      # 檢查回應的用戶和訊息是否正確
      print(3)
      
      print(4)
      res = await client.wait_for('select_option', check=check, timeout=30)
        # 等待用戶回應
      print(5)
      if res.component[0].value == questions['answer']:
        await interaction.followup.send('回答正確！')
      else:
        await interaction.followup.send('回答錯誤！')
      print("1")
    else:
      await interaction.response.send_message(f"No. {self.flag_id} 答題錯誤，再試試看吧", ephemeral = True)


class CtfQuestionButtons(nextcord.ui.View):
  def __init__(self):
    super().__init__(timeout = None)
    with open("flag_data.json", "r", encoding = "utf-8") as f:
      flag_data = json.load(f)
    for flag_id, data in flag_data.items():
      async def try_open_response(interaction: nextcord.Interaction):
        data = interaction.data.get("custom_id").split(":")
        await interaction.response.send_modal(CtfFlagResponseModal(client,data[0], data[1]))
      btn = nextcord.ui.Button(
        label = f"No. {flag_id}",
        style = nextcord.ButtonStyle.success,
        custom_id = f"{flag_id}:{data.get('flag')}:try_open_response"
      )
      btn.callback = try_open_response
      self.add_item(btn)

# @client.command()
# async def test_dp(interaction: nextcord.Interaction):
#   flag_embed = nextcord.Embed(
#     title = f"中電會迎新CTF",
#     description = f"點擊下面的按鈕來回答對應題目"
#   )
#   with open("group_data.json", "r", encoding = "utf-8") as f:
#     group_data = json.load(f)
#   for group in sorted(list(group_data.values()), key = lambda data: data.get('score'), reverse = True):
#     flag_embed.add_field(
#       name = group.get("name"),
#       value = f"Score: {group.get('score')} | Answered: {len(group.get('answered'))}",
#       inline = False
#     )
#   await interaction.channel.send(
#     embed = flag_embed,
#     view = CtfQuestionButtons()
#   )

@client.slash_command(description="My first slash command", guild_ids=None)
async def test(interaction: nextcord.Interaction):
  flag_embed = nextcord.Embed(
    title = f"中電會迎新CTF",
    description = f"點擊下面的按鈕來回答對應題目"
  )
  with open("user_data.json", "r", encoding = "utf-8") as f:
    group_data = json.load(f)
  for group in sorted(list(group_data.values()), key = lambda data: data.get('score'), reverse = True):
    flag_embed.add_field(
      name = group.get("name"),
      value = f"Score: {group.get('score')} | Answered: {len(group.get('answered'))}",
      inline = False
    )
  await interaction.channel.send(
    embed = flag_embed,
    view = CtfQuestionButtons()
  )

@client.slash_command(description="My first slash command", guild_ids=None)
async def auth(interaction: nextcord.Interaction,student_id:int):
  with open("user_data.json", "r", encoding = "utf-8") as f:
    user = json.load(f)
    user[str(interaction.user.id)]={'student_id':-1, 'score':-1,'answered':[]}
    user[str(interaction.user.id)]["student_id"] = str(student_id)
    user[str(interaction.user.id)]["score"] = 0
  with open("user_data.json", "w", encoding = "utf-8") as f:
    json.dump(user, f, indent = 2, ensure_ascii = False)
  #except ValueError:
   #   await interaction.response.send_message(f"未參賽", ephemeral = True)

client.run(token)