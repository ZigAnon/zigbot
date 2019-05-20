import discord
import asyncio
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

        # Ensures only bot owner or admin can use command
        if ctx.author.guild_permissions.administrator:
            pass
        elif zb.is_owner(ctx):
            pass
        else:
            return

        try:
            maxRanks = str(zb_config.maxRoleRanks)
            maxNum = len(maxRanks)

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
                      AND group_id = 0
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

    @commands.command(name='asar', hidden=True)
    @commands.guild_only()
    async def add_self_assignable_role(self, ctx, *args):
        """Adds role to be assignable"""
        try:
            # Checks for mod permissions+
            if not zb.is_trusted(ctx,3):
                return

            # Checks for group 3 roles
            sql = """ SELECT name
                      FROM roles
                      WHERE guild_id = {0}
                      AND group_id = 3
                      ORDER BY group_id ASC, name ASC """
            sql = sql.format(ctx.guild.id)
            roles, rows, junk1 = zb.sql_query(sql)
            # If none found, return
            if rows == 0:
                return

            await ctx.message.delete(delay=30)

            try:
                group_id = int(args[0])
                try:
                    junk1 = str(args[1])
                    role_name = ' '.join(args[1:])
                except:
                    role_name = str(group_id)
                    group_id = -1
            except:
                group_id = -1
                try:
                    role_name = ' '.join(args)
                except:
                    return

            # If group_id out of range, return
            if group_id > 5 or (group_id != -1 and group_id < 3):
                return

            # Get role id
            sql = """ SELECT role_id,group_id,name
                      FROM roles
                      WHERE guild_id = {0}
                      AND role_perms = 0
                      AND lower(name) = '{1}' """
            sql = sql.format(ctx.guild.id,role_name.lower())
            mod, rows, junk1 = zb.sql_query(sql)

            # Role doesn't exist
            if rows == 0:
                #TODO: role doesnt exist or check spelling
                return

            # Assign variables
            role_id = mod[0][0]
            role_group = mod[0][1]
            role_name = mod[0][2]

            # Is already assigned
            if int(mod[0][1]) != 0:
                embed=discord.Embed(description=f'**{ctx.author}** Role ' \
                        f'**{role_name}** is already in group **{role_group}**',
                        color=0xee281f)
                await ctx.send(embed=embed,delete_after=30)
                return

            # Assign group id
            if group_id != -1:
                sql = """ UPDATE roles
                          SET group_id = {0}
                          WHERE role_id = {1} """
                sql = sql.format(group_id,role_id)
                rows, string = zb.sql_update(sql)

                embed=discord.Embed(description=f'**{ctx.author}** Role **{role_name}** ' \
                        f'has been added to the list in group **{group_id}**',
                        color=0xf5d28a)
                await ctx.send(embed=embed,delete_after=30)
            else:
                # Send question
                embed=discord.Embed(description=f'**{ctx.author}** Role **{role_name}** ' \
                        f'needs a **Group ID**\n\n**3** - Chat | **4** - Vanity | **5** - Other',
                        color=0xf5d28a)
                msg = await ctx.send(embed=embed)

                # Reactions
                ids = ['3\N{combining enclosing keycap}',
                        '4\N{combining enclosing keycap}',
                        '5\N{combining enclosing keycap}']

                # Check reaction
                def r_check(reaction, user):
                    return (reaction.message.id == msg.id and user == ctx.author and
                            reaction.message.channel == ctx.message.channel and
                            str(reaction) in ids)

                # Add reactions
                for id in ids:
                    try:
                        await msg.add_reaction(emoji=id)
                    except:
                        await ctx.send(f'I could not find emoji.id = {id}',
                                delete_after=5)
                while True:
                    print(f'looping true for reaction add or remove')
                    done, pending = await asyncio.wait([
                                        self.bot.wait_for('reaction_add', check=r_check),
                                        self.bot.wait_for('reaction_remove', check=r_check)
                                    ], timeout = 10, return_when=asyncio.FIRST_COMPLETED)

                    try:
                        stuff = done.pop().result()
                    except Exception as e:
                        break
                    try:
                        emoji_id = zb.get_pattern(str(stuff), "(?<=emoji=')((.{2})(?='\s))")
                        nav = ids.index(emoji_id)
                        break
                    except Exception as e:
                        await zb.bot_errors(ctx,e)

                try:
                    for future in pending:
                        future.cancel()
                except Exception as e:
                    await zb.bot_errors(ctx,e)

                # Assign group id
                try:
                    group_id = nav + 3
                    sql = """ UPDATE roles
                              SET group_id = {0}
                              WHERE role_id = {1} """
                    sql = sql.format(group_id,role_id)
                    rows, string = zb.sql_update(sql)
                    embed=discord.Embed(description=f'**{ctx.author}** Role **{role_name}** ' \
                            f'has been added to the list in group **{group_id}**',
                            color=0xf5d28a)
                    await msg.edit(embed=embed,delete_after=30)
                except:
                    embed=discord.Embed(description=f'**{ctx.author}** Role **{role_name}** ' \
                            f'not changed. Please .asar {role_name} again.',
                            color=0xf5d28a)
                    await msg.edit(embed=embed,delete_after=30)
                await msg.clear_reactions()
        except Exception as e:
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(SetupCog(bot))
