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
            # If any bot
            if message.author.bot:
                return

            # Ignore self
            if message.author == self.bot.user:
                return

            # If bot dm
            if message.guild is None:
                return

            # Checks for good nickname
            await zb.is_good_nick(self,message.author)

            reminders = zb.get_startswith(message.guild.id)
            if message.content.lower().startswith(reminders):
                # Get Context
                ctx = await self.bot.get_context(message)

                await zb.do_reminder(ctx)

            # I'm hungry
            if zb.is_pattern(message.content.lower(),
                    """^(((\s+)?i((\s+)?|[']|)m\s+?)|(\s+)?i(\s+)?am\s+?)\w+(\W+)?$"""):
                #"""^((\s+)?i((\s+)?|[']|)m\s+?)\w+(\W+)?$"""):
                hungry = zb.get_pattern(message.content.lower(),"""[^(i'm)(am)(\s)]\w+""")
                msg = 'Hi {0}, I\'m {1}.'.format(hungry.capitalize(),
                    self.bot.user.display_name)
                await zb.timed_msg(message.channel,msg,30)

            if len(message.mentions) > 0:
                count = zb.mention_spamming(message.author)

                # Determins action to take
                # if 10 or more, ban
                if count >= 10:
                    # Truncates long messages
                    msg = (message.clean_content[:1021] + '...') if len(message.clean_content) > 1024 else message.clean_content

                    # Sends edited message
                    embed=discord.Embed(description="**Too many mentions in " +
                            message.channel.mention + "** " +
                            f'[Jump to Message]({message.jump_url})', color=0x117ea6)
                    embed.add_field(name="Message", value=msg,
                            inline=False)
                    embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                    await zb.print_log(self,message.author,embed)
                    await message.channel.send(f'I have banned {message.author.mention} ' +
                            'for mention spamming.', delete_after=90)
                    await message.author.ban(delete_message_days=0,reason='Mention spamming')
                # if 5 or more, mute
                elif count >= 5:
                    role = zb.get_roles_special(message.guild.id,11)
                    if not role:
                        zb.punish_user(message.author,1)
                        await message.channel.send(f'Careful {message.author.mention}, ' +
                                'I don\'t want to ban you.', delete_after=90)
                    else:
                        talk = zb.get_roles_special(message.guild.id,2)
                        await zb.remove_roles(self,message.author,talk,'Mention spamming')
                        mute = zb.get_roles_special(message.guild.id,11)
                        await zb.add_roles(self,message.author,mute,'Mention spamming')
                        zb.punish_user(message.author,1)
                        await message.channel.send(f'I have muted {message.author.mention} ' +
                                'for mention spamming.', delete_after=90)
                # if 3 or more, warn
                elif count == 3:
                    await message.channel.send(f'{message.author.mention}' +
                            f'{message.author.mention}' + f'{message.author.mention} ' +
                            '__**STOP MENTION SPAMMING**__' + f' {message.author.mention} ' +
                            f'{message.author.mention}' + f'{message.author.mention}',
                            delete_after=90)
                # if 3 or more, log
                if 10 > count > 3:
                    # Truncates long messages
                    msg = (message.clean_content[:1021] + '...') if len(message.clean_content) > 1024 else message.clean_content

                    # Sends edited message
                    embed=discord.Embed(description="**Member mention spammed in " +
                            message.channel.mention + "** " +
                            f'[Jump to Message]({message.jump_url})', color=0x117ea6)
                    embed.add_field(name="Message", value=msg,
                            inline=False)
                    embed.set_author(name=message.author, icon_url=message.author.avatar_url)
                    await zb.print_log(self,message.author,embed)

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
