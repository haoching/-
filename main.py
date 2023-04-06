import nextcord
from nextcord.ext import commands
import logging
import json


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
  def __init__(self, flag_id: str, flag: str):
    self.flag_id = flag_id
    self.flag = flag
    super().__init__(f"No. {flag_id}", timeout = None)

    self.flag_input = nextcord.ui.TextInput(
      label = "輸入答案",
      required = True,
      placeholder = "SCAICT{some_flag_here}",
    )
    self.add_item(self.flag_input)

  async def callback(self, interaction: nextcord.Interaction) -> None:
    try:
      with open("group_data.json", "r", encoding = "utf-8") as f:
        group_data = json.load(f)
      group_role = interaction.user.roles[list(map(lambda role: str(role.id) in group_data.keys(), interaction.user.roles)).index(True)]
      if self.flag_id in group_data[str(group_role.id)]["answered"]:
        await interaction.response.send_message(f"小組成員已經完成 No. {self.flag_id} 了！", ephemeral = True)
        return
      if self.flag_input.value == self.flag:
        with open("group_data.json", "w", encoding = "utf-8") as f:
          group_data[str(group_role.id)]["score"] += 100
          group_data[str(group_role.id)]["answered"].append(self.flag_id)
          json.dump(group_data, f, indent = 2, ensure_ascii = False)
        flag_embed = nextcord.Embed(
          title = f"中電會迎新CTF",
          description = f"點擊下面的按鈕來回答對應題目"
        )
        with open("group_data.json", "r", encoding = "utf-8") as f:
          group_data = json.load(f)
        for group in sorted(list(group_data.values()), key = lambda data: data.get('score'), reverse = True):
          flag_embed.add_field(
            name = group.get("name"),
            value = f"Score: {group.get('score')} | Answered: {len(group.get('answered'))}",
            inline = False
          )
        await interaction.edit(embed = flag_embed, view = CtfQuestionButtons())
        await interaction.followup.send(f"No. {self.flag_id} 答題正確，小組分數+100", ephemeral = True)
      else:
        await interaction.response.send_message(f"No. {self.flag_id} 答題錯誤，再試試看吧", ephemeral = True)
    except ValueError:
      await interaction.response.send_message(f"未參賽", ephemeral = True)

class CtfQuestionButtons(nextcord.ui.View):
  def __init__(self):
    super().__init__(timeout = None)
    with open("flag_data.json", "r", encoding = "utf-8") as f:
      flag_data = json.load(f)
    for flag_id, data in flag_data.items():
      async def try_open_response(interaction: nextcord.Interaction):
        data = interaction.data.get("custom_id").split(":")
        await interaction.response.send_modal(CtfFlagResponseModal(data[0], data[1]))
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
  with open("group_data.json", "r", encoding = "utf-8") as f:
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

client.run("OTY4NTMyMjY0MTc2NzIyMDEz.GlfYfu.XkRDOtsh-ARBPEWmr5mK96df1FIuRz3f9W5Wk8")