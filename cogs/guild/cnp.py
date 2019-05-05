import discord
import asyncio
from discord.ext import commands
from bin import zb
from bin import cp


class CoffeePolCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

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
