import discord
from discord.ext import commands
from typing import Optional, Union, Dict

class ChosenOptionButton(discord.ui.Button):
    """ Button of the soundboard. """

    def __init__(
        self, style: discord.ButtonStyle = discord.ButtonStyle.blurple, label: str = '\u200b', 
        emoji: Optional[Union[str, discord.Emoji, discord.PartialEmoji]] = None, custom_id: Optional[str] = None, row: Optional[int] = None) -> None:
        super().__init__(style=style, label=label, emoji=emoji, custom_id=custom_id, row=row, disabled=True)


    async def callback(self, interaction: discord.Interaction) -> None:
        """ Soundboard's button callback. """

        await interaction.response.defer()
        self.view.stop()
        new_story_path: str = f"{self.view.story_path}/{self.label}"
        await self.view.cog.start_ls_game_callback(new_story_path, self.view.member)

class ChooseOptionView(discord.ui.View):

    def __init__(self, cog: commands.Cog, member: discord.Member, story: Dict[str, str], story_path: str):
        super().__init__(timeout=None)
        self.cog = cog
        self.member = member
        self.story = story
        self.story_path = story_path

        for i, option in enumerate(self.story['options']):
            button: discord.ui.Button = ChosenOptionButton(style=discord.ButtonStyle.blurple, label=option, custom_id=f"option_{i+1}")
            self.add_item(button)