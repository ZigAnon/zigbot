import discord
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
from bin import zb_config
from bin import zb

_var = zb_config

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
            sendWelcome = True
            # Checks if server is closed
            if zb.is_closed(member.guild.id):
                # Lets member join when server opens again
                await member.send('**"{0}"** is currently not accepting members'.format(member.guild.name) +
                         ' at this time.  If you wish to join our discussions please' +
                         ' wait a few days and try again.\nhttps://discord.gg/' +
                         '{0}'.format(zb.get_invite(member.guild.id)))
                # If closed prevents exploiting API by joining quickly
                if zb.hammering(member) > 1:
                    print('hammer time')
                    #TODO: add to heartbeat remove ban after time
                    #TODO: send message to read
                    return
                    # await member.ban(delete_message_days=0)
            # Checks if raidNumber in 5 mins is exceeded
            if zb.is_raid(member.guild.id):
                #TODO: Close server
                pass

            data, rows, string = zb.get_blacklist(member)
            if rows > 0:
                #TODO: Print reason and who
                pass

            # If account is newer than config time, kick
            if datetime.utcnow() - timedelta(hours=_var.newAccount) < member.created_at:
                await member.send('Your account is too new to for "{0}". '.format(member.guild.name) +
                        ' If you wish to join our discussions please wait a few days' +
                        ' and try again.  :D')
                try:
                    if zb.log_channel(member) != 0:
                        channel = self.bot.get_channel(zb.log_channel(member))
                        await channel.send('I kicked ' + member.mention +
                                ' because account was made in the last ' +
                                str(_var.newAccount) + ' hours.')
                except Exception as e:
                    print(f'**`ERROR:`** {type(e).__name__} - {e}')
                await member.kick()

            #TODO: Check if left after punishment
            #    TODO: if punished, add roles
            #TODO: Add roles on join
            #TODO: Send welcome message
        except Exception as e:
            print(f'**`ERROR:`** {type(e).__name__} - {e}')


def setup(bot):
    bot.add_cog(OmjCog(bot))
