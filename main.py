import discord
from discord.app.commands import Option
from discord.ext import commands
import os
from dotenv import load_dotenv
load_dotenv()

from extra.customerrors import NotPlayer
from typing import List, Any

guild_ids: List[int] = [int(os.getenv('SERVER_ID'))]
client = commands.Bot(command_prefix='zq!', intents=discord.Intents.all(), help_command=None)
token = os.getenv('TOKEN')

@client.event
async def on_ready() -> None:
	print("Bot is ready!")

# Handles the errors
@client.event
async def on_command_error(ctx: commands.Context, error: Any):

    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You can't do that!")

    elif isinstance(error, NotPlayer):
        await ctx.send(f"**{ctx.author.mention}, you don't have perms to stop it!**")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please, inform all parameters!')

    elif isinstance(error, commands.NotOwner):
        await ctx.send("You're not the bot's owner!")

    elif isinstance(error, commands.CommandOnCooldown):
        secs = error.retry_after
        if int(secs) >= 60:
            await ctx.send(f"You are on cooldown! Try again in {secs/60:.1f} minutes!")
        else:
            await ctx.send(error)

    elif isinstance(error, commands.MissingAnyRole):
        await ctx.send(error)

    print(error)

@client.event
async def on_application_command_error(ctx, error) -> None:

    if isinstance(error, commands.MissingPermissions):
        await ctx.respond("**You can't do that!**")
    
    elif isinstance(error, NotPlayer):
        await ctx.send(f"**{ctx.author.mention}, you don't have perms to stop it!**")

    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.respond('**Please, inform all parameters!**')

    elif isinstance(error, commands.NotOwner):
        await ctx.respond("**You're not the bot's owner!**")

    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.respond(error)

    elif isinstance(error, commands.errors.CheckAnyFailure):
        await ctx.respond("**You can't do that!**")

    elif isinstance(error, commands.MissingAnyRole):
        role_names = [f"**{str(discord.utils.get(ctx.guild.roles, id=role_id))}**" for role_id in error.missing_roles]
        await ctx.respond(f"You are missing at least one of the required roles: {', '.join(role_names)}")

    elif isinstance(error, commands.errors.RoleNotFound):
        await ctx.respond(f"**{error}**")

    elif isinstance(error, commands.ChannelNotFound):
        await ctx.respond("**Channel not found!**")

    elif isinstance(error, discord.app.errors.CheckFailure):
        await ctx.respond("**It looks like you can't run this command!**")


    print('='*10)
    print(f"ERROR: {error} | Class: {error.__class__} | Cause: {error.__cause__}")
    print('='*10)

@client.command()
async def help(ctx: commands.Context, cmd: str = None) -> None:
  """ Shows some information about commands and categories.
  :param cmd: The command or cog to show info about. """
  
  if not cmd:
      embed = discord.Embed(
      title="All commands and categories",
      description=f"```ini\nUse {client.command_prefix}help command or {client.command_prefix}help category to know more about a specific command or category\n\n[Examples]\n[1] Category: {client.command_prefix}help games\n[2] Command : {client.command_prefix}help play```",
      timestamp=ctx.message.created_at,
      color=ctx.author.color
      )

      for cog in client.cogs:
          cog = client.get_cog(cog)
          commands = [c.name for c in cog.get_commands() if not c.hidden]
          if commands:
            embed.add_field(
            name=f"__{cog.qualified_name}__",
            value=f"`Commands:` {', '.join(commands)}",
            inline=False
            )

      cmds = []
      for y in client.walk_commands():
          if not y.cog_name and not y.hidden:
              cmds.append(y.name)
      embed.add_field(
      name='__Uncategorized Commands__', 
      value=f"`Commands:` {', '.join(cmds)}", 
      inline=False)
      await ctx.send(embed=embed)

  else:
    # Checks if it's a command
    if command := client.get_command(cmd.lower()):
      command_embed = discord.Embed(title=f"__Command:__ {command.name}", description=f"__**Description:**__\n```{command.help}```", color=ctx.author.color, timestamp=ctx.message.created_at)
      return await ctx.send(embed=command_embed)

    for cog in client.cogs:
      if str(cog).lower() == str(cmd).lower():
          cog = client.get_cog(cog)
          cog_embed = discord.Embed(title=f"__Cog:__ {cog.qualified_name}", description=f"__**Description:**__\n```{cog.description}```", color=ctx.author.color, timestamp=ctx.message.created_at)
          for c in cog.get_commands():
              if not c.hidden:
                  cog_embed.add_field(name=c.name,value=c.help,inline=False)

          return await ctx.send(embed=cog_embed)

    # Otherwise, it's an invalid parameter (Not found)
    else:
      await ctx.send(f"**Invalid parameter! `{cmd}` is neither a command nor a cog!**")



@client.command()
@commands.has_permissions(administrator=True)
async def logout(ctx: commands.Context) -> None:
    """ Logs-out the bot. """

    await ctx.send("**Bye!**")
    await client.close()


@client.command()
@commands.has_permissions(administrator=True)
async def load(ctx: commands.Context, extension: str = None) -> None:
    """ Loads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")

    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} loaded!**")


@client.command()
@commands.has_permissions(administrator=True)
async def unload(ctx: commands.Context, extension: str = None) -> None:
    """ Unloads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")

    client.unload_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} unloaded!**")


@client.command()
@commands.has_permissions(administrator=True)
async def reload(ctx: commands.Context, extension: str = None) -> None:
    """ Reloads a cog.
    :param extension: The cog. """

    if not extension:
        return await ctx.send("**Inform the cog!**")

    client.unload_extension(f'cogs.{extension}')
    client.load_extension(f'cogs.{extension}')
    return await ctx.send(f"**{extension} reloaded!**")


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(token)