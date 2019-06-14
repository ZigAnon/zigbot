import discord
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
import stackprinter as sp
from bin import zb

class onmemberbanCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):

        try:
            # Ignore self
            if member == self.bot.user:
                return

            embed=discord.Embed(description=member.mention + " " +
                    member.name, color=0xff470f)
            try:
                embed.add_field(name="Join Date", value=member.joined_at,
                        inline=False)
            except:
                pass
            if not zb.is_pattern(member.display_name,'^[A-Z]\w+[0-9]{3,}'):
                embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name="Member Banned",
                    icon_url=member.avatar_url)
            embed.set_footer(text="ID: " + str(member.id))
            embed.timestamp = datetime.utcnow()

            await zb.print_log_by_group_id(guild,81,embed)

        except Exception as e:
            await zb.bot_errors(self,sp.format(e))


def setup(bot):
    bot.add_cog(onmemberbanCog(bot))
