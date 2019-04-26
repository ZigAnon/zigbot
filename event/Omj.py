import discord
from discord.ext import commands
from bin import zb


class OmjCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.Cog.listener()
    async def on_member_join(self,member):
        print('Member Joined!!')


def setup(bot):
    bot.add_cog(OmjCog(bot))
