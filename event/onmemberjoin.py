import discord
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
from bin import zb_config
from bin import zb

_var = zb_config

class onmemberjoinCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            # Resets counters on hammered members
            if zb.is_hammer(member.guild.id):
                zb.reset_hammer(member.guild)

            # Get log channels
            channel = self.bot.get_channel(zb.log_channel(member))
            joinChan = self.bot.get_channel(zb.join_channel(member))
            welcomeChan = self.bot.get_channel(zb.welcome_channel(member))

            # Build logs
            try:
                embed = discord.Embed(description=member.mention + " " +
                        member.name, color=0x23d160)
                embed.add_field(name="Account Creation Date",
                        value=member.created_at, inline=False)
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name="Member Joined", icon_url=member.avatar_url)
                await zb.print_log(self,member,embed)
            except Exception as e:
                await zb.bot_errors(self,e)

            # Main tasks
            try:
                # Checks if server is closed
                if zb.is_closed(member.guild.id):
                    # If closed prevents exploiting API by joining quickly
                    if zb.hammering(member) > 2:
                        await channel.send(member.mention +
                                ' can\'t read so I banned them.')
                        await member.send('**"{0}"** has banned you for '.format(member.guild.name) +
                                'being unable to read. ' +
                                'Sorry, go play roblox elsewhere.')
                        await member.ban(delete_message_days=0)
                        return
                    else:
                        await channel.send(member.mention + ' tried to join ' +
                                'but I kicked them because server is closed.  ' +
                                'To open server, please `!disboard bump`.')
                        # Lets member join when server opens again
                        await member.send('**"{0}"** is currently not accepting members'.format(member.guild.name) +
                                 ' at this time.  If you wish to join our discussions please' +
                                 ' wait a few days and try again.\nhttps://discord.gg/' +
                                 '{0}'.format(zb.get_invite(member.guild.id)))
                        await member.kick()
                        return

                # Checks if raidNumber in 5 mins is exceeded
                elif zb.is_raid(member.guild.id):
                    zb.close_server(member.guild.id)
                    await channel.send('@everyone\n__**RAID DETECTED**__\n__**RAID DETECTED**__\n__**RAID DETECTED**__')
                    return

                # If member account is newer than config time, kick
                elif datetime.utcnow() - timedelta(hours=_var.newAccount) < member.created_at:
                    if zb.hammering(member) > 1:
                        await channel.send(member.mention +
                                ' can\'t read so I banned them.')
                        await member.send('**"{0}"** has banned you for '.format(member.guild.name) +
                                'being unable to read. ' +
                                'Sorry, go play roblox elsewhere.')
                        await member.ban(delete_message_days=0)
                        return
                    else:
                        await member.send('Your account is too new to for "{0}". '.format(member.guild.name) +
                                ' If you wish to join our discussions please wait a few days' +
                                ' and try again.  :D')
                        try:
                            await channel.send('I kicked ' + member.mention +
                                    ' because account was made in the last ' +
                                    str(_var.newAccount) + ' hours.')
                        except Exception as e:
                            print(f'**`ERROR:`** {type(e).__name__} - {e}')
                        await member.kick()
                        return

                # Checks if member is blacklisted
                data, rows, string = zb.get_blacklist(member)
                if rows > 0:
                    memberID = int(data[0][0])
                    banBy = self.bot.get_user(memberID)
                    await channel.send('@here\n' + member.mention +
                            ' banned by __**' + banBy.name + '**__ for reason: ' +
                            '`' + data[0][1] + '`.')
                    await member.ban(delete_message_days=0)

                # If member leaves after being punished and returns
                elif zb.get_punish_num(member) != 0:
                    punishNum = zb.get_punish_num(member)
                    #TODO: public log their punishment
                    data = zb.get_roles_special(member.guild.id,12)
                    reason = 'Left and rejoined after punishment {0}'.format(punishNum)
                    await zb.add_roles(self,member,data,reason)

                # Else, send welcome
                else:
                    # Adds server join roles
                    if zb.is_role_group(member.guild.id,1):
                        data = zb.get_roles_special(member.guild.id,1)
                        reason = 'Member joined'
                        await zb.add_roles(self,member,data,reason)
                    await welcomeChan.send('Hey ' + member.mention +
                            ', welcome to **{0}** \U0001F389\U0001F917 !'.format(member.guild.name))

                    # Sends join instructions
                    msg = 'Welcome {0}! {1}'.format(member.mention,
                            zb.join_msg(member))
                    await zb.is_good_nick(self,member)
                    await zb.timed_msg(joinChan,msg,_var.timeout*2)

            except Exception as e:
                await zb.bot_errors(self,e)
        except Exception as e:
            await zb.bot_errors(self,e)


def setup(bot):
    bot.add_cog(onmemberjoinCog(bot))
