import discord
from discord.ext import commands
from bin import zb
from bin import zb_config

_var = zb_config


class HelpCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def server_setup(self, ctx):
        """ Command to tell you what to do """

        try:
            embed=discord.Embed(title="For more details type .help <command>.")
            embed.set_author(name="Help Menu",
                             icon_url=self.bot.user.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name="Ask for help",
                            value=".help - not many other commands in here yet LoL",
                            inline=False)
            embed.set_footer(text="Type '.help' to start over.")

            if zb.is_trusted(ctx,int(_var.maxRoleRanks)):
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(HelpCog(bot))
