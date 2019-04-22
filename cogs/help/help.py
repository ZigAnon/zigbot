import discord
from discord.ext import commands
from bin import zb
from bin import zb_config


class HelpCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def server_setup(self, ctx):
        """Command which aid's in setting up perms"""

        await ctx.send('Help will go here.')


def setup(bot):
    bot.add_cog(HelpCog(bot))
