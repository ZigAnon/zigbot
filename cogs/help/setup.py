import discord
from discord.ext import commands


class SetupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='setup', hidden=True)
    @commands.is_owner()
    async def server_setup(self, ctx):
        """Command which aid's in setting up perms"""

        embed=discord.Embed(title="Choose from selection below to setup server.")
        embed.set_author(name="Server Setup Menu",
                         icon_url=self.bot.user.avatar_url)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name="Set admin roles",
                        value=".sar \<role_name\> [1-5]",
                        inline=False)
        embed.set_footer(text="Type '.setup' to start over.")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SetupCog(bot))
