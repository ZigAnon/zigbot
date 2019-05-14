import discord
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
            for channel in ctx.guild.voice_channels:
                await ctx.send(f'{channel.name} of id {channel.id} has object properties of {channel.members}')
            pass
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)
        # else:
        #     await ctx.send('**`SUCCESS`**')
    
    @commands.command(name='zinvite', hidden=True)
    @commands.is_owner()
    # async def tool_dev(self, ctx, *, cog: str):
    async def test_ban(self, ctx):
        """ Command that tests modules. """
        try:
            pass
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    # Hidden means it won't show up on the default help.
    @commands.command(name='godmode', hidden=True)
    @commands.is_owner()
    async def godmode(self, ctx, *, switch: str):
        """Command which gives Owner Admin perms"""

        try:
            await zb.give_admin(ctx,switch)
            await ctx.message.delete()
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')

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
            await zb.bot_errors(ctx,e)
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
            await zb.bot_errors(ctx,e)
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
            await zb.bot_errors(ctx,e)
        else:
            await ctx.send('**`SUCCESS`**')


def setup(bot):
    bot.add_cog(OwnerCog(bot))
