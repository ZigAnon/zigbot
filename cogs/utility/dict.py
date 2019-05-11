
import discord
from discord.ext import commands
from bin import zb
from bin import zb_config

_var = zb_config


class DictionaryCog(commands.Cog):
    """ Dictionary API calls """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='define', description='Defines word using Oxford Living Dictionary.')
    async def define(self, ctx):
        """ Posts navigateable Oxford dictionary list """
        try:
            pass
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(DictionaryCog(bot))
