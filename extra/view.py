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
        new_quest_path: str = f"{self.view.quest_path}/{self.label}"
        await self.view.cog.play_sloth_quest_callback(new_quest_path, self.view.member)

class ChooseOptionView(discord.ui.View):
    """ View for choosing an option into the Quest's story. """

    def __init__(self, cog: commands.Cog, member: discord.Member, quest: Dict[str, str], quest_path: str):
        super().__init__(timeout=None)
        self.cog = cog
        self.member = member
        self.quest = quest
        self.quest_path = quest_path

        for i, option in enumerate(self.quest['options']):
            button: discord.ui.Button = ChosenOptionButton(style=discord.ButtonStyle.blurple, label=option, custom_id=f"option_{i+1}")
            self.add_item(button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """ Checks whether it's the player who started the game who's clicking on the button option. """

        return self.member.id == interaction.user.id