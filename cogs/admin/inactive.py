import discord
import psycopg2 as dbSQL
from discord.ext import commands
from bin import zb
from bin import zb_config

_var = zb_config


class InactiveCog(commands.Cog):
    """ Forecast, kick, ban, exclude inactive members """

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='ialist', hidden=True)
    async def server_setup(self, ctx):
        """Command to show inactive members"""
        try:
            # Ensures only bot owner or user with perms can use command
            if zb.is_trusted(ctx,4):
                async with ctx.channel.typing():

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
                              AND NOT real_user_id in {2}
                              ORDER BY created_at ASC; """
                    ignore = zb.get_member_with_role(ctx,
                            zb.get_trusted_roles(ctx,_var.maxRoleRanks))
                    sql = sql.format(str(ctx.guild.id),
                                     zb.sql_list(zb.get_members_ids(ctx)),
                                     zb.sql_list(ignore))
                    data, rows, string = zb.sql_query(sql)
                    await zb.print_lookup(ctx,rows,data,title,string)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(InactiveCog(bot))
