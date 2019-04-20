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
        embed.set_author(name="Server Setup Menu", icon_url="https://cdn.discordapp.com/avatars/506310779298119680/4a4ff80747f598f562c68a88ba4786af.png")
        embed.set_thumbnail(url="https://cdn.discordapp.com/avatars/506310779298119680/4a4ff80747f598f562c68a88ba4786af.png")
        embed.add_field(name="Set admin roles", value=".sar \<role_name\> [1-5]", inline=False)
        embed.set_footer(text="aaa")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(SetupCog(bot))
