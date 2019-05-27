import discord
from discord.ext import commands
import stackprinter as sp
from bin import zb

class onrawbulkmessagedeleteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_raw_bulk_message_delete(self, payload):

        try:
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(self.bot.user.id)
            channel = guild.get_channel(payload.channel_id)

            embed=discord.Embed(description="**Bulk Delete in " +
                    channel.mention + f', {len(payload.message_ids)} messages ' +
                    "deleted**", color=0x117ea6)
            await zb.print_log(self,member,embed)

        except Exception as e:
            await zb.bot_errors(self,sp.format(e))


def setup(bot):
    bot.add_cog(onrawbulkmessagedeleteCog(bot))
