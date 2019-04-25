from discord.ext import commands
from bin import zb


class OwnerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dev', hidden=True)
    @commands.is_owner()
    # async def tool_dev(self, ctx, *, cog: str):
    async def tool_dev(self, ctx):
        """ Command that tests modules. """
        try:
            string = ['string 1','string 2']
            lst = ['bacon', 'eggs', 'foo', 'bar']
            await ctx.send(string)
            i = 0
            print(zb.SqlData.i)
            print(len(string[0]))
            print(len(lst[0]))
            if len(string[0]) == 1:
                await ctx.send(string)
            else:
                while i < len(string):
                    await ctx.send(string[i])
                    i+=1
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def tool_load(self, ctx, *, cog: str):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def tool_unload(self, ctx, *, cog: str):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def tool_reload(self, ctx, *, cog: str):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""

        try:
            self.bot.unload_extension(cog)
            self.bot.load_extension(cog)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
        else:
            await ctx.send('**`SUCCESS`**')


def setup(bot):
    bot.add_cog(OwnerCog(bot))
