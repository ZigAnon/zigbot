import discord
import psycopg2 as dbSQL
from discord.ext import commands
from bin import zb_checks


class LookupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='list', hidden=True)
    async def server_setup(self, ctx, *, tool: str):
        """Command which aid's in setting up perms"""
        if tool == 'sar':
            try:
                pass
            except Exception as e:
                await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            else:
                await ctx.send('**`SUCCESS`**')
        else:
            await ctx.send('**`INVALID OPTION:`** {0}'.format(tool))


def setup(bot):
    bot.add_cog(LookupCog(bot))
