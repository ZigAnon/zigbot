import os
import psutil
import discord
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
import stackprinter as sp
from datetime import datetime
from time import strftime
from bin import zb_config as _var
from bin import zb


class ServerInfoCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='stats', hidden=True)
    @commands.guild_only()
    async def embed_botinfo(self, ctx):
        async with ctx.channel.typing():
            try:
                # Gather data
                author = self.bot.user
                server = 6
                textChan = 0
                voiceChan = 0
                for guild in self.bot.guilds:
                    server+=1
                    textChan+=len(guild.text_channels)
                    voiceChan+=len(guild.voice_channels)
                sql = """ SELECT attachments
                          FROM messages
                          WHERE content like '.%' """
                junk1, cmds, junk2 = zb.sql_query(sql)
                sql = """ SELECT created_at
                          FROM messages
                          ORDER BY created_at ASC """
                dates, msgs, junk2 = zb.sql_query(sql)
                diff = int((datetime.utcnow() - dates[0][0]).total_seconds())
                msgsPer = msgs/diff
                day = 0
                hour = 0
                minute = 0
                while diff > 86400:
                    day+=1
                    diff-=86400
                while diff > 3600:
                    hour+=1
                    diff-=3600
                while diff > 60:
                    minute+=1
                    diff-=60
                pid = os.getpid()
                py = psutil.Process(pid)
                memoryUse = (py.memory_info()[0]/2.**30) * 1000

                # Build embed
                embed=discord.Embed(color=0xbaab7d)
                embed.set_author(name=f'{author.name} {_var.botVersion}',
                        icon_url=author.avatar_url)
                embed.add_field(name="Author", value=author, inline=True)
                embed.add_field(name="Bot ID", value=author.id, inline=True)
                embed.add_field(name="Shard", value='#0 / 1', inline=True)
                embed.add_field(name="Commands ran", value=cmds, inline=True)
                embed.add_field(name="Messages", value=f'{msgs} ({msgsPer:.2f}/sec)',
                        inline=True)
                embed.add_field(name="Memory", value=f'{memoryUse:.2f} MB',
                        inline=True)
                embed.add_field(name="Owner IDs", value=self.bot.owner_id, inline=True)
                embed.add_field(name="Uptime",
                        value=f'{day} days\n{hour} hours\n{minute} minutes', inline=True)
                embed.add_field(name="Presence",
                        value=(f'{server} Servers\n'
                               f'{textChan} Text Channels\n'
                               f'{voiceChan} Voice Channels'), inline=True)

                await ctx.send(embed=embed)
            except Exception as e:
                await zb.bot_errors(ctx,sp.format(e))

    # Hidden means it won't show up on the default help.
    @commands.command(name='serverinfo', hidden=True)
    @commands.guild_only()
    async def embed_serverinfo(self, ctx):
        try:
            if zb.is_trusted(ctx,5):
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
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))

def setup(bot):
    bot.add_cog(ServerInfoCog(bot))
