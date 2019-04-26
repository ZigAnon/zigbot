import discord
from discord.ext import commands
from bin import zb


class OmjCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            guild_id = member.guild.id
            sendWelcome = True
            #TODO: Add member join to log channel
            #TODO: Check if server closed
            # Checks if server is closed
            if zb.is_closed(guild_id):
                #TODO: send dm to user with invite
                pass
            #    TODO: if join too many times, temp ban
            # Checks if raidNumber in 5 mins is exceeded
            if zb.is_raid(guild_id):
                #TODO: Close server
                pass
            #TODO: Check blacklist
            #TODO: Check to see if account too new
            #    TODO: if too new, log
            #TODO: Check if left after punishment
            #    TODO: if punished, add roles
            #TODO: Add roles on join
            #TODO: Send welcome message
        except Exception as e:
            print(f'**`ERROR:`** {type(e).__name__} - {e}')


def setup(bot):
    bot.add_cog(OmjCog(bot))
