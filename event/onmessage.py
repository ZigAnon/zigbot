import discord
from discord.ext import commands
from bin import zb

_var = zb_config

class onmessageCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_message(self, member):
        # Ignore self
        if message.author == self.user:
            return

        # Get log channels
        channel = self.bot.get_channel(zb.log_channel(member))
        channelp = self.bot.get_channel(zb.log_channel_pub(member))
        welcomeChan = self.bot.get_channel(zb.welcome_channel(member))

        # Main tasks
        try:
            pass

        except Exception as e:
            print(f'**`ERROR:`** {type(e).__name__} - {e}')


def setup(bot):
    bot.add_cog(onmessageCog(bot))
