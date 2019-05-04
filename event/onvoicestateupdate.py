import discord
from discord.ext import commands
from bin import zb

class onvoicestateupdateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        try:
            # Ignore self
            if member == self.bot.user:
                return

            if not before.afk and after.afk:
                await member.edit(voice_channel=None)

            if not before.mute and after.mute:
                #TODO: log event
                return
            elif before.mute and not after.mute:
                #TODO: log event
                return

            if before.channel is after.channel:
                return
            elif before.channel is None and not after.channel is None:
                embed=discord.Embed(description="**" + member.mention +
                        " joined voice channel #" + after.channel.name +
                        "**\n", color=0x23d160)
                embed.set_author(name=member, icon_url=member.avatar_url)
                await zb.print_log(self,member,embed)
            elif not before.channel is None and not after.channel is None:
                embed=discord.Embed(description="**" + member.mention +
                        " switched voice channel `#" + before.channel.name +
                        "` -> `#" + after.channel.name + "`**", color=0x23d160)
                embed.set_author(name=member, icon_url=member.avatar_url)
                await zb.print_log(self,member,embed)
            elif not before.channel is None and after.channel is None:
                embed=discord.Embed(description="**" + member.mention +
                        " left voice channel #" + before.channel.name +
                        "**\n", color=0x23d160)
                embed.set_author(name=member, icon_url=member.avatar_url)
                await zb.print_log(self,member,embed)

        except Exception as e:
            await zb.bot_errors(self,e)


def setup(bot):
    bot.add_cog(onvoicestateupdateCog(bot))
