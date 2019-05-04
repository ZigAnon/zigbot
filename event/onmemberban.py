import discord
from discord.ext import commands
from bin import zb

class onmemberbanCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):

        try:
            # Ignore self
            if member == self.bot.user:
                return

            embed=discord.Embed(description=member.mention + " " +
                    member.name, color=0xff470f)
            embed.add_field(name="Join Date", value=member.joined_at,
                    inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name="Member Banned",
                    icon_url=member.avatar_url)

            await zb.print_log(self,member,embed)

        except Exception as e:
            await zb.bot_errors(self,e)


def setup(bot):
    bot.add_cog(onmemberbanCog(bot))
