import discord
from discord.ext import commands


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='say', hidden=True)
    @commands.guild_only()
    async def say_remove(self, ctx):
        """Says when a member joined."""
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(MembersCog(bot))
