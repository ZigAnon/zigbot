import discord
import asyncio
from discord.ext import commands
from bin import zb
from bin import cp


class PunishCog(commands.Cog):
    """ Punish members """

    def __init__(self, bot):
        self.bot = bot

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

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
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

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
                await member.edit(voice_channel=None)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='mute', hidden=True)
    @is_in_guild(509242768401629204)
    async def mute(self, ctx, member: discord.Member):
        """ Removes all write permissions from all channels """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(517882333752459264)
                embed=discord.Embed(title="User Muted!",
                        description=f'**{member}** was muted by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                await punishchan.send(embed=embed)
                # Update database
                cp.punish_user(member,1)
                # Get roles
                addRole = ctx.guild.get_role(517140313408536576)
                data = zb.grab_first_col(cp.rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Muted')
                # Add role
                await member.add_roles(addRole,reason='Muted')
                # Kick from voice
                await member.edit(mute=True)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='jail', hidden=True)
    @is_in_guild(509242768401629204)
    async def jail(self, ctx, member: discord.Member):
        """ Removes all chats and allows user to state case
            in jail chat."""
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(517882333752459264)
                embed=discord.Embed(title="User Jailed!",
                        description=f'**{member}** was jailed by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                await punishchan.send(embed=embed)
                # Update database
                cp.punish_user(member,1)
                # Get roles
                addRole = ctx.guild.get_role(509865275705917440)
                data = zb.grab_first_col(cp.rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Jailed')
                # Add role
                await member.add_roles(addRole,reason='Jailed')
                # Kick from voice
                await member.edit(voice_channel=None)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='cleanpost', hidden=True)
    async def cleanpost(self, ctx, member: discord.Member):
        """ Removes shitpost tag. """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):

                # If no shitpost role for guild, ignore
                rmv = zb.get_roles_by_group_id(ctx.guild.id,10)
                if len(rmv) == 0:
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
                embed=discord.Embed(title="Good Job!",
                        description=f'**{member}** it seems ' +
                        f'**{ctx.message.author}** has faith in you.',
                        color=0x27d300)
                await zb.print_log_by_group_id(ctx.guild,80,embed)

                # Gathers punishment removed roles
                add = await zb.get_all_special_roles(ctx,member,10,12)
                if not len(add) > 0:
                    return

                async with ctx.channel.typing():
                    await zb.add_roles(self,member,add,'Cleanposted')
                    await zb.remove_roles(self,member,rmv,'Cleanposted')
                    zb.rmv_special_role(ctx.guild.id,10,member.id)
                    zb.rmv_special_role(ctx.guild.id,11,member.id)
                    zb.rmv_special_role(ctx.guild.id,12,member.id)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='unmute', hidden=True)
    @is_in_guild(509242768401629204)
    async def unmute(self, ctx, member: discord.Member):
        """ Removes mute status. """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(517882333752459264)
                embed=discord.Embed(title="User unmuted.",
                        description=f'**{member}** follow the rules.',
                        color=0x27d300)
                await punishchan.send(embed=embed)
                # Update database
                cp.punish_user(member,0)
                # Get roles
                addRole = ctx.guild.get_role(513156267024449556)
                data = zb.grab_first_col(cp.rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Unmuted')
                # Add role
                await member.add_roles(addRole,reason='Unmuted')

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='free', hidden=True)
    @is_in_guild(509242768401629204)
    async def free(self, ctx, member: discord.Member):
        """ Frees member from jail """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(517882333752459264)
                embed=discord.Embed(title="User Jailed!",
                        description=f'**{member}** was freed by ' +
                        f'**{ctx.message.author}**!',
                        color=0x27d300)
                await punishchan.send(embed=embed)
                # Update database
                cp.punish_user(member,0)
                # Get roles
                addRole = ctx.guild.get_role(513156267024449556)
                data = zb.grab_first_col(cp.rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Freed')
                # Add role
                await member.add_roles(addRole,reason='Freed')

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(PunishCog(bot))
