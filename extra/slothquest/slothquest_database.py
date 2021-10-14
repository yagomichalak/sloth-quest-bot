import discord
from discord.ext import commands
from external_cons import the_database
from typing import List

class SlothQuestDatabase(commands.Cog):
    """ Cog for the Sloth Quest's database commands and methods. """

    def __init__(self, client: commands.Bot) -> None:
        """ Class init method. """

        self.client = client


    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def create_table_quest_players(self, ctx) -> None:
        """ Creates the QuestPlayers table in the database. """

        author: discord.Member = ctx.author
        if await self.check_quest_players_table_exists():
            return await ctx.send(f"**`QuestPlayers` table already exists, {author.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("""
            CREATE TABLE QuestPlayers (
                user_id BIGINT NOT NULL,
                quests_played INT DEFAULT 1,
                last_played_ts BIGINT NOT NULL,
                PRIMARY KEY(user_id)
            )""")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Successfully created the `QuestPlayers` table, {author.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def drop_table_quest_players(self, ctx) -> None:
        """ Drops the QuestPlayers table from the database. """

        author: discord.Member = ctx.author
        if not await self.check_quest_players_table_exists():
            return await ctx.send(f"**`QuestPlayers` table doesn't exist, {author.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DROP TABLE QuestPlayers")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Successfully dropped the `QuestPlayers` table, {author.mention}!**")

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def reset_table_quest_players(self, ctx) -> None:
        """ Resets the QuestPlayers table in the database. """

        author: discord.Member = ctx.author
        if not await self.check_quest_players_table_exists():
            return await ctx.send(f"**`QuestPlayers` table doesn't exist yet, {author.mention}!**")

        mycursor, db = await the_database()
        await mycursor.execute("DELETE FROM QuestPlayers")
        await db.commit()
        await mycursor.close()

        await ctx.send(f"**Successfully reset the `QuestPlayers` table, {author.mention}!**")


    async def check_quest_players_table_exists(self) -> bool:
        """ Checks whether the QuestPlayers table exists in the database. """

        mycursor, _ = await the_database()
        await mycursor.execute("SHOW TABLE STATUS LIKE 'QuestPlayers'")
        exists = await mycursor.fetchone()
        await mycursor.close()
        if exists:
            return True
        else:
            return False

    # === INSERT ===

    async def insert_quest_player(self, user_id: int, current_ts: int) -> None:
        """ Inserts a Quest player.
        :param user_id: The ID of the user to insert.
        :param current_ts: The current timestamp. """

        mycursor, db = await the_database()
        await mycursor.execute("""
            INSERT INTO QuestPlayer (user_id, last_played_ts)
            VALUES (%s, %s)""", (user_id, current_ts))
        await db.commit()
        await mycursor.close()

    # === SELECT ===

    async def get_quest_player(self, user_id: int) -> List[int]:
        """ Gets a Quest player.
        :param user_id: The ID of the user to get. """

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM QuestPlayers WHERE user_id = %s", (user_id,))
        player = await mycursor.fetchone()
        await mycursor.close()
        return player

    async def get_quest_players(self) -> List[List[int]]:
        """ Gets all Quest players."""

        mycursor, _ = await the_database()
        await mycursor.execute("SELECT * FROM QuestPlayers")
        players = await mycursor.fetchall()
        await mycursor.close()
        return players
    
    # === UPDATE ===
    async def update_player_quests_played(self, user_id: int, current_ts: int, increment: int = 1) -> None:
        """ Updates the QuestPlayer's quests played counter and updates their last played timestamp.
        :param user_id: The ID of the user to update.
        :param current_ts: The current timestamp.
        :param increment: The incremention value for the quests played counter. [Default = 1] """

        mycursor, db = await the_database()
        await mycursor.execute("""
            UPDATE QuestPlayers SET quests_played = quests_played + %s, last_played_ts = %s
            WHERE user_id = %s""", (increment, current_ts, user_id))
        await db.commit()
        await mycursor.close()