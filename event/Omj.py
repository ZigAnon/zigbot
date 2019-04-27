import discord
from discord.ext import commands
from datetime import datetime
from bin import zb


class OmjCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Build logs
        try:
            if zb.log_channel(member) != 0:
                channel = self.bot.get_channel(zb.log_channel(member))
                embed = discord.Embed(description=member.mention + " " + 
                        member.name, color=0x23d160)
                embed.add_field(name="Account Creation Date",
                        value=member.created_at, inline=False)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name="Member Joined", icon_url=member.avatar_url)
                embed.set_footer(text="ID: " + str(member.id) +
                        " • Today at " + f"{datetime.now():%I:%M %p}")

                await channel.send(embed=embed)
        except Exception as e:
            print(f'**`ERROR:`** {type(e).__name__} - {e}')

        # Main tasks
        try:
            guild_id = member.guild.id
            sendWelcome = True
            # Checks if server is closed
            if zb.is_closed(guild_id):
                #TODO: send dm to user with invite
                pass
            #    TODO: if join too many times, temp ban
            # Checks if raidNumber in 5 mins is exceeded
            if zb.is_raid(guild_id):
                #TODO: Close server
                pass

            data, rows, string = zb.get_blacklist(member)
            if rows > 0:
                #TODO: Print reason and who
                pass

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
