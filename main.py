import nextcord
from nextcord.ext import commands
import logging
import json
from dotenv import load_dotenv
from os import environ
import csv

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
      placeholder = "DDCIRC{xxxxxxxxxxxxxxxxxxxxxxxxxx}",
    )
    self.add_item(self.flag_input)
    self.client = client
  async def callback(self, interaction: nextcord.Interaction) -> None:
    try:
      with open("user_data.json", "r", encoding = "utf-8") as f:
        user_data = json.load(f)
      answered = user_data.get(str(interaction.user.id), {}).get("answered", [])
      if self.flag_id in answered:
        await interaction.response.send_message(f"你已經完成 No. {self.flag_id} 了！", ephemeral = True)
        return
      if self.flag_input.value == self.flag:
        user_data[str(interaction.user.id)]["score"] += 100
        user_data[str(interaction.user.id)]["answered"].append(self.flag_id)
        with open("user_data.json", "w", encoding = "utf-8") as f:
          json.dump(user_data, f, indent = 2, ensure_ascii = False)
        flag_embed = nextcord.Embed(
          title = f"電研數創第一屆定向越野大賽",
          description = f"點擊下面的按鈕來回答"
        )
        with open("user_data.json", "r", encoding = "utf-8") as f:
          user_data = json.load(f)
        d = {}
        with open("club_member.csv","r", encoding= "utf-8") as f:
          reader = csv.reader(f)
          next(reader) # toss headers
          for id, name in reader:
            d.setdefault(id, []).append(name)
        i = 0
        for group in sorted(list(user_data.values()), key = lambda data: data.get('score'), reverse = True):
          if i >= 10:
            break
          student_id = group.get("student_id")
          username = d.get(student_id)
          if username is not None:
            n = username[0]
          else:
            n = student_id+"(非社員)"
          flag_embed.add_field(
            name = n,
            value = f"Score: {group.get('score')} | Answered: {len(group.get('answered'))}",
            inline = False
          )
          i+=1
        await interaction.edit(embed = flag_embed, view = CtfQuestionButtons())
        await interaction.followup.send(f"No. {self.flag_id} 答題正確，社團價值+100", ephemeral = True)
      else:
        await interaction.response.send_message(f"No. {self.flag_id} 答題錯誤，可撥", ephemeral = True)
    except:
      await interaction.response.send_message(f"未註冊，如已註冊請詢問工作人員", ephemeral = True)


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


@client.slash_command(description="My first slash command", guild_ids=None)
async def test(interaction: nextcord.Interaction):
  flag_embed = nextcord.Embed(
    title = f"電研數創第一屆定向越野大賽",
    description = f"點擊下面的按鈕來回答"
  )
  with open("user_data.json", "r", encoding = "utf-8") as f:
    group_data = json.load(f)
  for group in sorted(list(group_data.values()), key = lambda data: data.get('score'), reverse = True):
    flag_embed.add_field(
      name = group.get("student_id"),
      value = f"Score: {group.get('score')} | Answered: {len(group.get('answered'))}",
      inline = False
    )
  await interaction.channel.send(
    embed = flag_embed,
    view = CtfQuestionButtons()
  )

@client.slash_command(description="My first slash command", guild_ids=None)
async def auth(interaction: nextcord.Interaction,student_id:int):
  try:
    if(student_id>11000000 and student_id<11199999):
      with open("user_data.json", "r", encoding = "utf-8") as f:
        user = json.load(f)
        user[str(interaction.user.id)]={'student_id':-1, 'score':-1,'answered':[]}
        user[str(interaction.user.id)]["student_id"] = str(student_id)
        user[str(interaction.user.id)]["score"] = 0
      with open("user_data.json", "w", encoding = "utf-8") as f:
        json.dump(user, f, indent = 2, ensure_ascii = False)
      await interaction.response.send_message(f"已驗證，學號為:{student_id}，如有錯誤請重新驗證，請注意分數將會歸零...糕?", ephemeral = True)
    else:
      await interaction.response.send_message(f"請打八碼學號", ephemeral = True)
  except ValueError:
      await interaction.response.send_message(f"驗證錯誤", ephemeral = True)

client.run(token)