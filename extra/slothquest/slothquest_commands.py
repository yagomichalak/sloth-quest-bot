import discord
from discord.ext import commands
from discord.app import slash_command, Option

from typing import Optional, Union, List
import os
from extra import utils

guild_ids: List[int] = [int(os.getenv('SERVER_ID'))]

class SlothQuestCommands(commands.Cog):
    """ Category for the Sloth Quest's commands. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client

    @commands.command(name="quest_profile", aliases=["profile"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def quest_profile_command(self, ctx, member: Optional[Union[discord.Member, discord.User]] = None) -> None:
        """ Shows someone's Quest Profile.
        :param member: The member to show. [Optional][Default = You] """

        member = member if member else ctx.author
        await self.quest_profile_callback(ctx, member)

    @slash_command(name="quest_profile", guild_ids=guild_ids)
    async def quest_profile_slash(self, ctx, 
        member: Option(discord.Member, name="member", description="The member from whom to show the profile.", required=False)
    ) -> None:
        """ Shows someone's Quest Profile.
        :param member: The member to show. [Optional][Default = You] """

        await ctx.defer()
        member = member if member else ctx.author
        await self.quest_profile_callback(ctx, member)

    async def quest_profile_callback(self, ctx, member: Union[discord.Member, discord.User]) -> None:
        """ Callback for the Quest Profile command.
        :param member: The member to show. """

        answer: discord.PartialMessageable = ctx.reply if isinstance(ctx, commands.Context) else ctx.respond

        quest_player: List[int] = await self.get_quest_player(member.id)
        if not quest_player:
            return await answer(f"**{member} doesn't have a Quest Profile!**")


        current_time = await utils.get_time_now()
        embed: discord.Embed = discord.Embed(
            title="__Quest Profile__",
            description=f"**Quests Played**: {quest_player[1]}\n" \
                f"**Last Time Played**: <t:{quest_player[2]}:R>"
            ,
            color=member.color,
            timestamp=current_time
        )
        embed.set_thumbnail(url=member.display_avatar)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.display_avatar)

        await answer(embed=embed)

