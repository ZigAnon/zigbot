import discord
import psycopg2 as dbSQL
from discord.ext import commands
from bin import zb
from bin import zb_config


class SetupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='setup', hidden=True)
    async def server_setup(self, ctx):
        """Command which aid's in setting up perms"""

        try:
            if zb.is_trusted(ctx,3):

                embed=discord.Embed(title="Choose from selection below to setup server.")
                embed.set_author(name="Server Setup Menu",
                                 icon_url=self.bot.user.avatar_url)
                embed.set_thumbnail(url=ctx.author.avatar_url)
                embed.add_field(name="Set admin roles",
                                value=".sar \<role_name\> [1-5]",
                                inline=False)
                embed.set_footer(text="Type '.setup' to start over.")
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    # Hidden means it won't show up on the default help.
    @commands.command(name='sar', hidden=True)
    async def set_role(self, ctx, *, role: str):
        """ allow role permissions """

        try:
            maxRanks = str(zb_config.maxRoleRanks)
            maxNum = len(maxRanks)

            # Ensures only bot owner or user with perms can use command
            if zb.is_owner(ctx) or zb.is_trusted(ctx,3):

                try:

                    # Verifies pattern is valid
                    if zb.is_pattern(ctx.message.content.lower(),
                            '^(.\w+)\s+(\w+\W+){1,}([0-' + maxRanks + '])$'):
                        role = role[:-(1+maxNum)].lower()
                        role_perms = int(ctx.message.content[-1:])
                    else:
                        await ctx.send('Please use format `.sar <role_name> [1-' +
                                       maxRanks +  ']`.')
                        return

                    # Get role id by name
                    roles = zb.get_roles_by_name(ctx,role)

                    if len(roles) > 1:
                        rows = len(roles)

                        await ctx.send('Multiple roles were found for `' + role + '`.')
                        select = await zb.print_select(ctx,roles)
                        if select >= 0:
                            role_id = roles[select][0]
                            role_name = roles[select][1]
                        else:
                            return
                    else:
                        try:
                            role_id = roles[0][0]
                            role_name = roles[0][1]
                        except:
                            await ctx.send('Unable to find the role `' + role + '`.\n' +
                                           'Check your spelling and try again.')
                            return

                    sql = """ UPDATE roles
                              SET role_perms = {0}
                              WHERE guild_id = {1}
                              AND role_id = {2} """
                    sql = sql.format(role_perms, ctx.guild.id, role_id)
                    rows, string = zb.sql_update(sql)

                    if rows > 0:
                        await ctx.send('Updated role `' + role_name +
                                       '` with id `' + str(role_id) +
                                       '`.\nPermission is now ' + str(role_perms))
                    else:
                        await ctx.send('Something went wrong.\n' +
                                       'Check the spelling and try again. ' +
                                       'I\'ll let <@{0}> know there is an issue'.format('zig'))
                except Exception as e:
                    await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
                    await zb.bot_errors(ctx,e)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(SetupCog(bot))
