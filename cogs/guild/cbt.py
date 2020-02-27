import discord
import asyncio
import random
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
import stackprinter as sp
import numpy as np
from bin import zb
from bin import cp

# Settings for guild_id
_guild_check = 681783307058675776
_thotadmins = [280455061140930562,341744189324918794,409206287424028672]
_thotpatrol = 681851633784586246
_thotrole = 681922891691982885

class CoffeePolCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='thotmode', hidden=True)
    async def thotmode(self, ctx, *, switch: str):
        """Command which gives CBT Admin perms"""

        try:
            # If CBT Resort, disable godmode
            if ctx.guild.id != _guild_check: return

            if ctx.author.id not in _thotadmins: return

            try:
                await ctx.message.delete()
                tp = ctx.guild.get_role(_thotpatrol)
                t = ctx.guild.get_role(_thotrole)
                if switch == 'on':
                    await ctx.author.add_roles(tp,reason='Begone THOTS')
                    await ctx.author.remove_roles(t,reason='Begone THOTS')
                else:
                    await ctx.author.add_roles(t,reason='I need THOTS')
                    await ctx.author.remove_roles(tp,reason='I need THOTS')

            except Exception as e:
                await zb.bot_errors(ctx,sp.format(e))

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

def setup(bot):
    bot.add_cog(CoffeePolCog(bot))
