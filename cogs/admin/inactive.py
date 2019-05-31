import discord
import psycopg2 as dbSQL
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
import stackprinter as sp
from bin import zb
from bin import zb_config

_var = zb_config


class InactiveCog(commands.Cog):
    """ Forecast, kick, ban, exclude inactive members """

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='ialist', hidden=True)
    async def server_setup(self, ctx, *args):
        """Command to show inactive members"""
        try:
            # Ensures only bot owner or user with perms can use command
            if zb.is_trusted(ctx,4):
                async with ctx.channel.typing():

                    # Lists current Server Access Roles
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

                    # Get members
                    lst = []
                    members = []
                    unMembers = []
                    now = datetime.utcnow()
                    i = 0
                    while i < rows:
                        undecided = '❁-'
                        unRole = ctx.guild.get_role(517850437626363925)
                        member = ctx.guild.get_member(data[i][2])
                        if not unRole in member.roles:
                            undecided = ''
                            unMembers.append(member)
                        diff = (now - data[i][1]).days
                        lst.append(f'{diff} days -{undecided} {member}')
                        members.append(member)

                        # increment loop
                        i+=1
                    title = f'**There are** {rows} **inactive members**'
                    pages, embeds = await zb.build_embed_print(self,ctx,lst,title)

                    # Starting page
                    try:
                        page = int(args[0])
                        if page < 1:
                            page = 1
                        elif page > pages:
                            page = pages
                    except:
                        page = 1

                    initialEmbed = embeds[page-1]
                    await zb.print_embed_nav(self,ctx,initialEmbed,embeds,pages,page,'')

                # Purge members
                purge = False
                try:
                    check = args[0]
                    if check.lower == 'purge':
                        purge = True
                except:
                    pass

                if not purge:
                    return

                if zb.is_trusted(ctx,2):
                    for member in members:
                        await member.kick(reason='Purged for inactivity')
                elif zb.is_trusted(ctx,3):
                    for member in unMembers:
                        await member.kick(reason='Purged for inactivity')

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))


def setup(bot):
    bot.add_cog(InactiveCog(bot))
