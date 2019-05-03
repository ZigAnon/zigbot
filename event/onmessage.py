import discord
from discord.ext import commands
from bin import zb

class onmessageCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_message(self, message):

        try:
            # Ignore self
            if message.author == self.bot.user:
                return

            reminders = zb.get_startswith(message.guild.id)
            if message.content.lower().startswith(reminders):
                # Get Context
                ctx = await self.bot.get_context(message)

                await zb.do_reminder(ctx)

            # I'm hungry
            if zb.is_pattern(message.content.lower(),
                    """^((\s+)?i((\s+)?|[']|)m\s+?)\w+(\W+)?$"""):
                hungry = zb.get_pattern(message.content.lower(),"""[^i'm(\s)]\w+""")
                msg = 'Hi {0}, I\'m {1}.'.format(hungry.capitalize(),
                    self.bot.user.display_name)
                await zb.timed_msg(message.channel,msg,30)


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
        except Exception as e:
            ctx = await self.bot.get_context(message)
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(onmessageCog(bot))
