import discord
from discord.ext import commands
from datetime import datetime
from bin import zb

class onmemberunbanCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):

        try:
            # If any bot
            if user.bot:
                return

            sql = """ SELECT log_channel
                      FROM guilds
                      WHERE guild_id = {0} """
            sql = sql.format(str(guild.id))
            data, rows, string = zb.sql_query(sql)

            channel = self.bot.get_channel(int(data[0]))

            embed=discord.Embed(description=user.mention + " " +
                    user.name, color=0x117ea6)
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_author(name="Member Unbanned",
                    icon_url=user.avatar_url)
            embed.set_footer(text="ID: " + str(user.id))
            embed.timestamp = datetime.utcnow()
            await channel.send(embed=embed)

        except Exception as e:
            await zb.bot_errors(self,e)


def setup(bot):
    bot.add_cog(onmemberunbanCog(bot))
