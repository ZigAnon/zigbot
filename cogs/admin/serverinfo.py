import discord
from discord.ext import commands
from datetime import datetime
from time import strftime

modroles = ['Owner', 'High Admin', 'Moderator', 'Representative', 'BotAdmin']

class ServerInfoCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='serverinfo', hidden=True)
    @commands.guild_only()
    @commands.has_any_role(*modroles)
    async def embed_serverinfo(self, ctx):
        embed=discord.Embed(color=0xbaab7d)
        embed.set_author(name=ctx.guild.name,icon_url=ctx.guild.icon_url)
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.add_field(name="Owner", value=ctx.guild.owner, inline=True)
        embed.add_field(
            name="Region",
            value=ctx.guild.region,
            inline=True)
        embed.add_field(
            name="Channel Categories",
            value=len(ctx.guild.categories),
            inline=True)
        embed.add_field(
            name="Text Channels",
            value=len(ctx.guild.text_channels),
            inline=True)
        embed.add_field(
            name="Voice Channel",
            value=len(ctx.guild.voice_channels),
            inline=True)
        embed.add_field(
            name="Members",
            value=len(ctx.guild.members),
            inline=True)

        # Counts members and bots
        members = ctx.guild.members
        humans = 0
        bots = 0
        for member in members:
            if member.bot:
                bots += 1
            else:
                humans += 1
        embed.add_field(name="Humans", value=humans, inline=True)
        embed.add_field(name="Bots", value=bots, inline=True)

        # Counts if online
        online = 0
        for member in members:
            if str(member.status) != "offline":
                online += 1
        embed.add_field(name="Online", value=online, inline=True)

        embed.add_field(
            name="Roles",
            value=len(ctx.guild.roles),
            inline=True)
        embed.set_footer(text=f'ID: {ctx.guild.id}  | Server Created • {ctx.guild.created_at.strftime("%m/%d/%Y")}')
        await ctx.send(embed=embed)
        """Command which displays Server info.
        Remember to use dot path. e.g: cogs.serverinfo"""

def setup(bot):
    bot.add_cog(ServerInfoCog(bot))