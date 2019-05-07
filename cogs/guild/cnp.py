import discord
import asyncio
from discord.ext import commands
import numpy as np
from bin import zb
from bin import cp

# Settings for guild_id
_guild_check = 509242768401629204

# role_id, role_name, channel_id
_voice_roles = [[538750807538008084,'VC1',509242768829317141],
        [538750916694638602,'VC2',527947459981213696],[538751001881083938,'VC3',0],
        [538751040523337728,'VC5',0],[538751077705842728,'VC6',0],
        [538751116842631168,'VC7',0],[538751158802579456,'VC8',0],
        [538751195725168649,'MC1',513096462335213569],[538751267908878336,'MC2',0],
        [538751306513514508,'MC3',0],[538773262700773380,'SC1',521862351461548033],
        [538773299744997386,'SC2',509243691098177547],[538773327796502546,'SC3',521862247585284098],
        [538773357039058944,'SC4',0],[538773384679522345,'SC5',0]]


class CoffeePolCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

    #TODO: Add to main loop
    @commands.Cog.listener()
    async def on_message(self, message):
        # If any bot
        if message.author.bot:
            return

        # Ignore self
        if message.author == self.bot.user:
            return

        # Adds people to blacklist
        guild = self.bot.get_guild(509242768401629204)
        if(message.author in guild.members and
                message.guild is None):
            channel = guild.get_channel(509244241776738304)

            # Sets static values
            member = message.author
            carryMsg = message
            # Looks for last message in admin chats
            while True:
                async for message in channel.history(limit=500):
                    if message.author == member:
                        msg = message
                        break
                break

            # Try to get message ctx if found
            try:
                ctx = await self.bot.get_context(msg)
            except:
                return

            # If ctx found, test for permissions
            if(zb.is_trusted(ctx,4) and
                    zb.is_pattern(carryMsg.content,
                        '^([0-9]{14,})\s+(((\w+\s+)+(\w+)?)|(\w+)).+')):
                data = carryMsg.content.split(' ',1)
                sql = """ SELECT real_user_id
                          FROM blacklist
                          WHERE guild_id = {0}
                          AND real_user_id = {1} """
                sql = sql.format(guild.id,data[0])

                junk, rows, junk2 = zb.sql_query(sql)

                # Checks if already in list
                if rows > 0:
                    await carryMsg.author.send('Thank you for reporting ' +
                            f'`{data[0]}`, but it already exists for **{guild.name}**.')
                    return
                else:
                    await carryMsg.author.send(f'I have added `{data[0]}` ' +
                            f'to the blacklist for **{guild.name}**')
                    zb.add_blacklist(message,data[0],data[1])

    # Events on member join voice
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Checks for right guild
        try:
            if member.guild.id != _guild_check:
                return
        except:
            return

        args = [self, 'guild_membership', 'voice_updating', _guild_check, member.id]
        try:
            if before.channel is after.channel:
                return
            elif zb.is_updating(*args):
                print('updating')
                return
            # Joined voice channel
            elif before.channel is None and not after.channel is None:
                await zb.toggle_updating(*args)
                i = [(i, _voice_roles.index(after.channel.id))
                        for i, _voice_roles in enumerate(_voice_roles)
                        if after.channel.id in _voice_roles][0][0]
                role = member.guild.get_role(_voice_roles[i][0])
                await member.add_roles(role,reason='Joined voice')
                await zb.toggle_updating(*args)
            # Switched voice channel
            elif not before.channel is None and not after.channel is None:
                await zb.toggle_updating(*args)
                i = [(i, _voice_roles.index(after.channel.id))
                        for i, _voice_roles in enumerate(_voice_roles)
                        if after.channel.id in _voice_roles][0][0]
                try:
                    j = [(i, _voice_roles.index(before.channel.id))
                            for i, _voice_roles in enumerate(_voice_roles)
                            if before.channel.id in _voice_roles][0][0]
                    rmv = member.guild.get_role(_voice_roles[j][0])
                    await member.remove_roles(rmv,reason='Left voice')
                except:
                    pass
                add = member.guild.get_role(_voice_roles[i][0])
                await member.add_roles(add,reason='Joined voice')
                await zb.toggle_updating(*args)
            # Left voice channel
            elif not before.channel is None and after.channel is None:
                await zb.toggle_updating(*args)
                roles = np.array([x[0] for x in _voice_roles])
                await zb.remove_roles(self,member,roles,'Left voice')
                await zb.toggle_updating(*args)
        except Exception as e:
            await zb.bot_errors(self,e)

    @commands.command(name='shitpost', hidden=True)
    @is_in_guild(509242768401629204)
    async def shitpost(self, ctx, member: discord.Member):
        """ Banishes member to shitpost chat. """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):
                shitchan = ctx.guild.get_channel(533390486845653027)
                punishchan = ctx.guild.get_channel(517882333752459264)
                embed=discord.Embed(title="Shitposter!",
                        description=f'**{member}** was given Shitposter by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                msg = await shitchan.send('Looks like you pushed it too far ' +
                        f'{member.mention}. You live here now. Enjoy!!')
                await punishchan.send(embed=embed)
                # Update database
                cp.punish_user(member,1)
                # Get roles
                addRole = ctx.guild.get_role(509865272283496449)
                data = zb.grab_first_col(cp.rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Shitposted')
                # Add role
                await member.add_roles(addRole,reason='Shitposted')
                # Kick from voice
                await member.edit(voice_channel=None)

                await asyncio.sleep(60)
                await msg.delete()
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
    @is_in_guild(509242768401629204)
    async def cleanpost(self, ctx, member: discord.Member):
        """ Removes shitpost tag. """
        try:
            if(zb.is_trusted(ctx,4) and
                    cp.is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(517882333752459264)
                embed=discord.Embed(title="Good Job!",
                        description=f'**{member}** it seems ' +
                        f'**{ctx.message.author}** has faith in you.',
                        color=0x27d300)
                await punishchan.send(embed=embed)
                # Update database
                cp.punish_user(member,0)
                # Get roles
                addRole = ctx.guild.get_role(513156267024449556)
                data = zb.grab_first_col(cp.rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Cleanposted')
                # Add role
                await member.add_roles(addRole,reason='Cleanposted')

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
    bot.add_cog(CoffeePolCog(bot))
