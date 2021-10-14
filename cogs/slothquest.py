import discord
from discord.app.commands import slash_command
from discord.ext import commands
from external_cons import the_drive
import shutil
import os

from extra import utils
from extra.view import ChooseOptionView
from extra.customerrors import NotPlayer
from extra.slothquest.slothquest_database import SlothQuestDatabase
from extra.slothquest.slothquest_commands import SlothQuestCommands

import asyncio
from typing import Optional, List, Any, Dict
from random import choice

language_quest_txt_id = int(os.getenv('LANGUAGE_QUEST_TXT_ID'))
language_quest_vc_id = int(os.getenv('LANGUAGE_QUEST_VC_ID'))
guild_ids: List[int] = [int(os.getenv('SERVER_ID'))]

quest_cogs: List[discord.Cog] = [
    SlothQuestDatabase, SlothQuestCommands
]

class SlothQuest(*quest_cogs):
    """ Category for SlothQuest game. """

    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.quests_played: List[str] = []
        self.root_path: str = './sloth_quest'
        self.round: int = 0
        self.quest_name: str = None
        self.player: discord.Member = None


    @commands.Cog.listener()
    async def on_ready(self) -> None:

        self.txt = await self.client.fetch_channel(language_quest_txt_id)
        self.vc = await self.client.fetch_channel(language_quest_vc_id)
        print("SlothQuest cog is online!")


    # Downloads all content for the Language Jungle game
    @commands.command(aliases=['sau'])
    @commands.has_permissions(administrator=True)
    async def quest_audio_update(self, ctx: Optional[commands.Context] = None, rall: str = 'no') -> None:
        """ Downloads all audios from the GoogleDrive for The Language quest game
        and stores in the bot's folder.
        :param ctx: The context of the command. [Optional]
        :param rall: Whether the it should remove all folders before downloading files. """

        if rall.lower() == 'yes':
            try:
                shutil.rmtree('./sloth_quest')
            except Exception:
                pass

        all_folders = {
            "Quests": "1MgRUwGW8Iw-ZROmqq0sYHcikwof2VG-3"
        }
        categories = ['Quests']
        for category in categories:
            try:
                os.makedirs(f'./sloth_quest/{category}')
                print(f"{category} folder made!")
            except FileExistsError:
                pass

        drive = await the_drive()

        for folder, folder_id in all_folders.items():

            await self.download_recursively(drive, 'sloth_quest', folder, folder_id)

        if ctx:
            await ctx.send("**Download update complete!**")

    async def download_recursively(self, drive, path: str, folder: str, folder_id: int) -> None:

        files = drive.ListFile({'q': "'%s' in parents and trashed=false" % folder_id}).GetList()
        download_path = f'./{path}/{folder}'

        for file in files:
            try:
                #print(f"\033[34mItem name:\033[m \033[33m{file['title']:<35}\033[m | \033[34mID: \033[m\033[33m{file['id']}\033[m")
                output_file = os.path.join(download_path, file['title'])
                temp_file = drive.CreateFile({'id': file['id']})
                temp_file.GetContentFile(output_file)
                #print("File downloaded!")
            except Exception as error:
                new_category = file['title']
                try:
                    new_download_path = f"{download_path}/{new_category}"
                    os.makedirs(new_download_path)
                    print(f"{new_category} folder made!")
                except FileExistsError:
                    pass
                else:
                    await self.download_recursively(drive, download_path, new_category, file['id'])


    @commands.command(name="play_sloth_quest", aliases=['quest', 'play_quest', 'pq', 'start_quest'])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play_sloth_quest_command(self, ctx) -> None:
        """ Starts the Language Quest game. """

        author = ctx.author
        if self.player:
            return await ctx.send(f"**Someone is already playing, {self.player.mention}!**")

        self.player = ctx.author

        quest_path: str = f"{self.root_path}/Quests"
        # Gets a random language audio
        await ctx.reply("**Quest starting!**")
        await self.reset_bot_status()
        await self.play_sloth_quest_callback(quest_path, author)

    @slash_command(name="play_quest", aliases=['quest'], guild_ids=guild_ids)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def play_sloth_quest_slash(self, ctx) -> None:
        """ Starts the Language Quest game. """

        author = ctx.author
        if self.player:
            return await ctx.respond(f"**Someone is already playing, {self.player.mention}!**")

        self.player = ctx.author

        quest_path: str = f"{self.root_path}/Quests"
        # Gets a random language audio
        await ctx.respond("**Quest starting!**")
        await self.reset_bot_status()
        await self.play_sloth_quest_callback(quest_path, author)


    async def play_sloth_quest_callback(self, quest_path: str, member: discord.Member) -> None:
        """ Starts the Language quest game..
        :param quest_path: The path of the current or next audio to be played.
        :param member: The member who started the game. """

        server_bot: discord.Member = member.guild.get_member(self.client.user.id)
        if (bot_voice := server_bot.voice) and bot_voice.mute:
            await server_bot.edit(mute=False)
        
        voice = member.voice
        voice_client = member.guild.voice_client

        voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=member.guild)

        # Checks if the bot is in a voice channel
        if not voice_client:
            await voice.channel.connect()
            await asyncio.sleep(1)
            voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=member.guild)

        # Checks if the bot is in the same voice channel that the user
        if voice and voice.channel == voice_client.channel:

            # Plays the song
            if not voice_client.is_playing():

                if os.path.isfile(f"{quest_path}/end.txt"):
                    return await self.end_game()

                self.round += 1

                if self.round == 1:
                    quest = await self.get_random_quest(quest_path, True)
                    quest_path = f"{quest_path}/{quest['name']}"
                    text: str = quest['text']
                else:
                    quest = await self.get_random_quest(quest_path)
                    text: str = await self.get_new_text(quest_path)


                embed = discord.Embed(
                    title=f"__`The Quest starts now! ({quest['name']})`__",
                    description=f"Text:\n\n{text}",
                    color=discord.Color.green()
                )

                files: List[discord.File] = []

                if os.path.isfile(f"{quest_path}/image.png"):
                    files.append(
                        discord.File(f"{quest_path}/image.png", filename="image.png")
                    )
                    embed.set_image(url="attachment://image.png")

                if os.path.isfile(f"{quest_path}/thumbnail.png"):
                    files.append(
                        discord.File(f"{quest_path}/thumbnail.png", filename="thumbnail.png")
                    )
                    embed.set_thumbnail(url="attachment://thumbnail.png")

                view: discord.ui.View = ChooseOptionView(cog=self, member=member, quest=quest, quest_path=quest_path)
                msg = await self.txt.send(content="\u200b", embed=embed, view=view, files=files)
                voice_client.play(discord.FFmpegPCMAudio(f"{quest_path}/audio.mp3"), after=lambda e: self.client.loop.create_task(self.enable_answers(msg, view)))

        else:
            # (to-do) send a message to a specific channel
            await self.txt.send("**The player left the voice channel, so it's game over!**")
            await self.reset_bot_status()

    async def enable_answers(self, message: discord.Message, view: discord.ui.View) -> None:
        """ Enables the buttons from the view, so the user can continue the game. """

        await utils.disable_buttons(view, False)
        await message.edit(view=view)

    async def get_new_text(self, quest_path: str) -> str:
        """ Gets a new text to display.
        :param quest_path: The path from which to get the text. """

        with open(f"{quest_path}/text.txt", 'r', encoding="utf-8") as f:
            text: str = f.read()

        return text


    async def get_random_quest(self, folder: str, random: bool = False) -> List[Any]:
        """ Gets a random Quest to play.
        :param folder: The folder from which to start looking. """

        quest: Dict[str, str] = {
            'name': None,
            'text': None,
            'audio': None,
            'options': []
        }

        while True:

            search_path: str = folder
            if random:
                quest_name = choice(os.listdir(f"{self.root_path}/Quests/"))
                search_path = f"{folder}/{quest_name}"
                if quest_name in self.quests_played:
                    continue
                self.quest_name = quest_name
                
                quest['name'] = quest_name
                quest['audio'] = f"{folder}/{quest_name}/audio.mp3"
                option_path: str = f"{folder}/{quest_name}"
                quest['options'] = [
                    file for file in os.listdir(option_path)
                    if os.path.isdir(f"{option_path}/{file}")
                ]
            
            else:
                quest_name = self.quest_name
                quest['name'] = quest_name
                quest['audio'] = f"{folder}/audio.mp3"
                option_path: str = f"{folder}/"
                quest['options'] = [
                    file for file in os.listdir(option_path)
                    if os.path.isdir(f"{option_path}/{file}")
                ]

            with open(f"{search_path}/text.txt", encoding="utf-8") as f:
                text = f.read()
                quest['text'] = text

            break

        return quest

    async def reset_bot_status(self) -> None:
        """ Resets the bot's status to its original state. """

        self.quests_played: List[str] = []
        self.root_path: str = './sloth_quest'
        self.round: int = 0
        self.quest_name: str = None
        self.player: discord.Member = None

    def check_player() -> bool:
        """ Checks whether it's the current player that is
        trying to run the command. """

        async def real_check(ctx: commands.Context) -> None:

            if ctx.cog.player.id == ctx.author.id:
                return True

            return NotPlayer()

        return commands.check(real_check)

    # Leaves the channel
    @commands.command()
    @commands.check_any(check_player(), commands.has_permissions(administrator=True))
    async def stop(self, ctx: commands.Context) -> None:
        """ Stops the game. """

        author: discord.Member = ctx.author
        await self.reset_bot_status()

        guild = ctx.message.guild
        voice_client: discord.VoiceClient = discord.utils.get(self.client.voice_clients, guild=guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()

        await ctx.send(f"**Quest terminated, {author.mention}!**")

    async def end_game(self) -> None:
        """ Ends the SlothQuest game. """

        current_ts = await utils.get_timestamp()
        if await self.get_quest_player(self.player.id):
            await self.update_player_quests(self.player.id, current_ts)
        else:
            await self.insert_quest_player(self.player.id, current_ts)

        await self.reset_bot_status()
        await self.txt.send("**The end!**")


def setup(client) -> None:
    client.add_cog(SlothQuest(client))