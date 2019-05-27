import discord
import aiohttp
import feedparser as fp
import stackprinter as sp
from discord.ext import commands
from datetime import datetime
from bin import zb
from bin import cp


class OwnerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dev', hidden=True)
    @commands.is_owner()
    # async def tool_dev(self, ctx, *, cog: str):
    async def tool_dev(self, ctx):
        """ Command that tests modules. """
        try:
            permissions = ctx.author.permissions_in(ctx.channel)
            a = b/c
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))
        # else:
        #     await ctx.send('**`SUCCESS`**')

    @commands.command(name='rules', hidden=True)
    @commands.is_owner()
    async def post_rules(self, ctx):
        """ Command that posts server rules. """
        try:
            await ctx.message.delete(delay=5)
            # Grab rules and format
            sql = """ SELECT "order",channel_id,title,description,
                             fields,author_name,author_icon,color,
                             footer_text,footer_icon,message_id
                      FROM rules
                      WHERE guild_id = {0}
                      AND NOT "order" IS NULL
                      ORDER BY "order" ASC """
            sql = sql.format(ctx.guild.id)
            data, rows, junk1 = zb.sql_query(sql)
            if not rows > 0:
                return

            i=0
            while i < rows:
                # Set values
                channel = ctx.guild.get_channel(int(data[i][1]))
                title = data[i][2]
                desc = data[i][3]
                fields = data[i][4]
                a_name = data[i][5]
                a_icon = data[i][6]
                color = int(data[i][7])
                f_text = data[i][8]
                f_icon = data[i][9]

                # Checks for existing message to edit
                if int(data[i][10]) == 0:
                    #Build and send embed structure
                    embed=discord.Embed(title=f'{title}',
                            description=f'{desc}',
                            color=color)
                    #TODO: for field not equal to 'none', add field
                    embed.set_author(name=f'{a_name}',
                            icon_url=f'{a_icon}')
                    embed.set_footer(text=f'{f_text}',
                            icon_url=f'{f_icon}')
                    embed.timestamp = datetime.utcnow()
                    msg = await channel.send(embed=embed)

                    # Save msg id
                    sql = """ UPDATE rules
                              SET message_id = {0}
                              WHERE description = '{1}'
                              AND "order" = {2}
                              AND title = '{3}'
                              AND channel_id = {4} """
                    sql = sql.format(msg.id,desc,int(data[i][0]),
                            title,channel.id)
                    await ctx.send(sql)
                    junk1, junk2 = zb.sql_update(sql)
                else:
                    # Edit message if exists
                    # Check for changes
                    msg = await channel.fetch_message(int(data[i][10]))
                    for embed in msg.embeds:
                        test = embed.description

                    # If changed, update
                    if test != desc:
                        embed=discord.Embed(title=f'{title}',
                                description=f'{desc}',
                                color=color)
                        #TODO: for field not equal to 'none', add field
                        embed.set_author(name=f'{a_name}',
                                icon_url=f'{a_icon}')
                        embed.set_footer(text=f'{f_text}',
                                icon_url=f'{f_icon}')
                        embed.timestamp = datetime.utcnow()
                        await msg.edit(embed=embed)

                #increment loop
                i+=1

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='zinvite', hidden=True)
    @commands.is_owner()
    # async def tool_dev(self, ctx, *, cog: str):
    async def test_ban(self, ctx):
        """ Command that tests modules. """
        try:
            pass
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))

    # Hidden means it won't show up on the default help.
    @commands.command(name='godmode', hidden=True)
    @commands.is_owner()
    async def godmode(self, ctx, *, switch: str):
        """Command which gives Owner Admin perms"""

        try:
            await ctx.message.delete()
            await zb.give_admin(ctx,switch)
            try:
                shit = zb.get_roles_by_group_id(ctx.guild.id,10)
                mute = zb.get_roles_by_group_id(ctx.guild.id,11)
                jail = zb.get_roles_by_group_id(ctx.guild.id,12)
                if not len(shit) == 0:
                    rmv = shit
                elif not len(mute) == 0:
                    rmv = mute
                elif not len(jail) == 0:
                    rmv = jail
                else:
                    return

                # Update database
                cp.punish_user(member,0)

                add = await zb.get_all_special_roles(ctx,member,10,12)
                await zb.add_roles(self,ctx.author,roles,'Troubleshooting')
                await zb.remove_roles(self,member,rmv,'Troubleshooting')
                zb.rmv_special_role(ctx.guild.id,10,ctx.author.id)
                zb.rmv_special_role(ctx.guild.id,11,member.id)
                zb.rmv_special_role(ctx.guild.id,12,member.id)

                # Mute in voice
                await member.edit(mute=False)
            except:
                pass
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')

    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def tool_load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def tool_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def tool_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))
        else:
            await ctx.send('**`SUCCESS`**')


def setup(bot):
    bot.add_cog(OwnerCog(bot))
