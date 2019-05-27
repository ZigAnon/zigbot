import discord
from discord.ext import commands
import stackprinter as sp
from bin import zb

class onvoicestateupdateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        try:
            # Ignore bots
            if member.bot:
                return

            if before.afk:
                return

            if after.afk:
                await member.edit(voice_channel=None)
                embed=discord.Embed(description=f'**{member.mention} ' \
                        f'was kicked from voice for being AFK for ' \
                        f'{int(member.guild.afk_timeout/60)} minutes**',
                        color=0x23d160)
                embed.set_author(name=member, icon_url=member.avatar_url)
                await zb.print_log(self,member,embed)
                return

            if not before.mute and after.mute:
                #TODO: log event
                return
            elif before.mute and not after.mute:
                #TODO: log event
                return

            if before.channel is after.channel:
                return
            elif before.channel is None and not after.channel is None:
                embed=discord.Embed(description=f'**{member.mention} ' \
                        f'joined voice channel #{after.channel.name}**',
                        color=0x23d160)
                embed.set_author(name=member, icon_url=member.avatar_url)
                await zb.print_log(self,member,embed)
            elif not before.channel is None and not after.channel is None:
                embed=discord.Embed(description=f'**{member.mention} ' \
                        f'switched voice channel `#{before.channel.name}` ' \
                        f'-> `#{after.channel.name}`**',
                        color=0x23d160)
                embed.set_author(name=member, icon_url=member.avatar_url)
                await zb.print_log(self,member,embed)
            elif not before.channel is None and after.channel is None:
                embed=discord.Embed(description=f'**{member.mention} ' \
                        f'left voice channel #{before.channel.name}**',
                        color=0x23d160)
                embed.set_author(name=member, icon_url=member.avatar_url)
                await zb.print_log(self,member,embed)

        except Exception as e:
            await zb.bot_errors(self,sp.format(e))


def setup(bot):
    bot.add_cog(onvoicestateupdateCog(bot))
