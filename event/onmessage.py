import discord
from discord.ext import commands
from bin import zb

class onmessageCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore self
        if message.author == self.bot.user:
            return

        triggers = zb.get_startswith(message.guild.id)
        if message.content.lower().startswith(triggers):
            await zb.do_trigger(self,message)

        #TODO: disboard bump
        #TODO: get server, member, channel
        #TODO: open_server
        #TODO: log time

        #TODO: disboard stop
        #TODO: close_server

        #TODO: check chat and voice xp for trusted
        #    TODO: if trusted removed, nope
        #TODO: skip following if has role_perms
        #TODO: if invite message sent without trusted
        #TODO: public log ban, priv log ban, message person, del message, ban
        #TODO: if message abused like || or zalgo msg and del
        #TODO: if too many caps, log and message
        #TODO: if mass mentions, log and message, and jail

        #TODO: if message starts with keyword
        #TODO: do a thing

        # Main tasks
        try:
            pass
        except Exception as e:
            print(f'**`ERROR:`** {type(e).__name__} - {e}')


def setup(bot):
    bot.add_cog(onmessageCog(bot))
