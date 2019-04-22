import discord
import psycopg2 as dbSQL
from discord.ext import commands
from bin import zb


class InactiveCog(commands.Cog):
    """ Forecast, kick, ban, exclude inactive members """

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='ialist', hidden=True)
    async def server_setup(self, ctx):
        """Command to show inactive members"""

        # Ensures only bot owner or user with perms can use command
        if zb.is_trusted(ctx,4):

            # Lists current Server Access Roles
            title = '**`List of Inactive Members`**'
            sql = """ SELECT name, created_at, real_user_id
                      FROM (
                          SELECT DISTINCT ON (m.int_user_id)
                          m.int_user_id, created_at, u.name, u.real_user_id, m.guild_id
                          FROM (
                              SELECT t1.* FROM (
                                  SELECT int_user_id, guild_id, max(created_at) AS MaxCreated
                                  FROM messages
                                  GROUP BY int_user_id, guild_id) t2
                              JOIN messages t1 on t2.int_user_id = t1.int_user_id
                              AND t2.guild_id = t1.guild_id
                              AND t2.MaxCreated = t1.created_at
                          ) m
                          LEFT JOIN users u ON u.int_user_id = m.int_user_id
                          ORDER BY m.int_user_id ASC
                      ) s
                      WHERE guild_id = {0}
                      AND NOT created_at > now() - INTERVAL '60 day'
                      AND real_user_id in {1}
                      ORDER BY created_at DESC; """
            sql = sql.format(str(ctx.guild.id),
                             zb.sql_list(zb.get_members_ids(ctx)))
            data, rows, string = zb.sql_query(sql)
            await zb.print_lookup(ctx,rows,data,title,string)


def setup(bot):
    bot.add_cog(InactiveCog(bot))
