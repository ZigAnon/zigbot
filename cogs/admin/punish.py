import discord
import asyncio
from discord.ext import commands
import stackprinter as sp
from bin import zb
from bin import cp


class PunishCog(commands.Cog):
    """ Punish members """

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='raid', hidden=True)
    async def raid_control(self, ctx):
        """Command to show inactive members"""
        try:
            if zb.is_trusted(ctx,3):
                data = [['Open Server', 'Lets members join'],
                        ['Close Server', 'Auto kicks members who join  ']]
                choice = await zb.print_select(ctx,data)

                sql = """ UPDATE guilds
                          SET can_join = {0}
                          WHERE guild_id = {1} """
            # Open Server
            if choice == -1:
                return
            elif choice == 0:
                sql = sql.format('TRUE',ctx.guild.id)
                await ctx.send('__**`RAID OFF:`**__ Server is open to public!')
            elif choice == 1:
                sql = sql.format('FALSE',ctx.guild.id)
                await ctx.send('__**`RAID ON:`**__ All invite links are disabled!')
            rows, string = zb.sql_update(sql)
        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='shitpost', hidden=True)
    async def shitpost(self, ctx, member: discord.Member):
        """ Banishes member to shitpost chat. """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):

                # If no shitpost role for guild, ignore
                add = zb.get_roles_by_group_id(ctx.guild.id,10)
                if len(add) == 0:
                    return

                # If punished, can't use command
                rows = zb.get_punish_num(member)
                if rows > 0:
                    await ctx.send('User is already punished.',
                            delete_after=15)
                    await ctx.message.delete()
                    return

                # Update database
                cp.punish_user(member,1)

                # If no punish chan, skip log
                embed=discord.Embed(title="Shitposter!",
                        description=f'**{member}** was given Shitposter by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                await zb.print_log_by_group_id(ctx.guild,80,embed)

                # If no shit chan, skip notify
                embed=discord.Embed(description=f'Looks like you pushed it ' \
                        f'too far {member.mention}. You live here now. Enjoy!!',
                        delete_after=60)
                await zb.print_log_by_group_id(ctx.guild,10,embed)

                # Removes roles and sets shitposter
                rmv = await zb.store_all_special_roles(ctx,member,10)
                if len(rmv) != 0:
                    await member.remove_roles(*rmv,reason='Shitposted')
                    await zb.add_roles(self,member,add,'Shitposted')

                # Kick from voice
                try:
                    await member.edit(voice_channel=None)
                except:
                    pass

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='mute', hidden=True)
    async def mute(self, ctx, member: discord.Member):
        """ Removes all write permissions from all channels """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):

                # If no mute role for guild, ignore
                add = zb.get_roles_by_group_id(ctx.guild.id,11)
                if len(add) == 0:
                    return

                # If punished, can't use command
                rows = zb.get_punish_num(member)
                if rows > 0:
                    await ctx.send('User is already punished.',
                            delete_after=15)
                    await ctx.message.delete()
                    return

                # Update database
                cp.punish_user(member,1)

                # If no punish chan, skip log
                embed=discord.Embed(title="User Muted!",
                        description=f'**{member}** was muted by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                await zb.print_log_by_group_id(ctx.guild,80,embed)

                # Removes roles and sets mute
                rmv = await zb.store_all_special_roles(ctx,member,11)
                if len(rmv) != 0:
                    await member.remove_roles(*rmv,reason='Muted')
                    await zb.add_roles(self,member,add,'Muted')

                # Mute in voice
                try:
                    await member.edit(mute=True)
                except:
                    pass

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='jail', hidden=True)
    async def jail(self, ctx, member: discord.Member):
        """ Removes all chats and allows user to state case
            in jail chat."""
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):

                # If no jail role for guild, ignore
                add = zb.get_roles_by_group_id(ctx.guild.id,12)
                if len(add) == 0:
                    return

                # If punished, can't use command
                rows = zb.get_punish_num(member)
                if rows > 0:
                    await ctx.send('User is already punished.',
                            delete_after=15)
                    await ctx.message.delete()
                    return

                # Update database
                cp.punish_user(member,1)

                # If no punish chan, skip log
                embed=discord.Embed(title="User Jailed!",
                        description=f'**{member}** was jailed by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                await zb.print_log_by_group_id(ctx.guild,80,embed)

                # Removes roles and sets mute
                rmv = await zb.store_all_special_roles(ctx,member,12)
                if len(rmv) != 0:
                    await member.remove_roles(*rmv,reason='Jailed')
                    await zb.add_roles(self,member,add,'Jailed')

                # Kick from voice
                try:
                    await member.edit(voice_channel=None)
                except:
                    pass

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='cleanpost', aliases=['free','unmute'], hidden=True)
    async def cleanpost(self, ctx, member: discord.Member):
        """ Removes punishment tag and gives back roles """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):

                # If no punish role for guild, ignore
                shit = zb.get_roles_by_group_id(ctx.guild.id,10)
                mute = zb.get_roles_by_group_id(ctx.guild.id,11)
                jail = zb.get_roles_by_group_id(ctx.guild.id,12)
                sRole = ctx.guild.get_role(shit[0][0])
                mRole = ctx.guild.get_role(mute[0][0])
                jRole = ctx.guild.get_role(jail[0][0])
                if not len(shit) == 0 and sRole in member.roles:
                    rmv = shit
                    embed=discord.Embed(title="Good Job!",
                            description=f'**{member}** it seems ' +
                            f'**{ctx.message.author}** has faith in you.',
                            color=0x27d300)
                elif not len(mute) == 0 and mRole in member.roles:
                    rmv = mute
                    embed=discord.Embed(title="User Unmuted!",
                            description=f'**{member}** follow the rules.',
                            color=0x27d300)
                elif not len(jail) == 0 and jRole in member.roles:
                    rmv = jail
                    embed=discord.Embed(title="User Freed!",
                            description=f'**{member}** was freed by ' +
                            f'**{ctx.message.author}**!',
                            color=0x27d300)
                else:
                    return

                # If punished, can't use command
                rows = zb.get_punish_num(member)
                if rows == 0:
                    await ctx.send(f'**{member}** is not punished.',
                            delete_after=15)
                    await ctx.message.delete()
                    return

                # Update database
                cp.punish_user(member,0)

                # If no punish chan, skip log
                await zb.print_log_by_group_id(ctx.guild,80,embed)

                # Gathers punishment removed roles
                add = await zb.get_all_special_roles(ctx,member,10,12)
                if not len(add) > 0:
                    return

                # Removes punishment and adds old roles
                async with ctx.channel.typing():
                    await zb.add_roles(self,member,add,'Cleanposted')
                    await zb.remove_roles(self,member,rmv,'Cleanposted')
                    zb.rmv_special_role(ctx.guild.id,10,member.id)
                    zb.rmv_special_role(ctx.guild.id,11,member.id)
                    zb.rmv_special_role(ctx.guild.id,12,member.id)

                # Mute in voice
                try:
                    await member.edit(mute=False)
                except:
                    pass

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))


def setup(bot):
    bot.add_cog(PunishCog(bot))
