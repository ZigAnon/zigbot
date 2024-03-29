import discord
from discord.ext import commands
import stackprinter as sp
from bin import zb
from bin import zb_config as _var

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

            # If bot dm
            if message.guild is None:
                return

            # Checks for good nickname
            await zb.is_good_nick(self,message.author)

            # Timestamps last message
            sql = """ UPDATE channels
                      SET last_message = date_trunc('minute', timezone('ZULU', NOW()))
                      WHERE channel_id = {0} """
            sql = sql.format(message.channel.id)
            junk, junk1 = zb.sql_update(sql)

            # Sends bot reminder
            sendHelp = zb.get_bot_help_counter(message.channel.id,3)
            if sendHelp >= 0:
                zb.increment_bot_help_counter(sendHelp,message.channel.id)
                if sendHelp > 5:
                    zb.increment_bot_help_counter(-1,message.channel.id)
                    embed=discord.Embed(title="Need Help?",
                            description=f'For a list of assignable roles type `.LSAR` into chat.\n' \
                                    f'Use the arrows to navigate the list.\n\n' \
                                    f'To assign a role you want, type `.iam that role\'s name`\n' \
                                    f'To remove a role you do not want, type `.iamn that role\'s name`\n' \
                                    f'OR `.iamnot that role\'s name`', color=0xf5d28a)
                    await message.channel.send(embed=embed)

            reminders = zb.get_startswith(message.guild.id)
            if message.content.lower().startswith(reminders):
                # Get Context
                ctx = await self.bot.get_context(message)

                await zb.do_reminder(ctx)

            # I'm hungry
            if zb.is_pattern(message.content.lower(),
                    """^(((\s+)?i((\s+)?|[']|)m\s+?)|(\s+)?i(\s+)?am\s+?)\w+(\W+)?$"""):
                #"""^((\s+)?i((\s+)?|[']|)m\s+?)\w+(\W+)?$"""):
                hungry = zb.get_pattern(message.content.lower(),"""(?<=m\s).*""")
                hungry = hungry.strip()
                msg = await message.channel.send(f'Hi {hungry.capitalize()}, I\'m' \
                        f' {self.bot.user.display_name}.',delete_after=30)

            # If cancer post or person, delete after 30 mins
            cancerIDs = [487608169615458324]
            cancerWords = ['nigger','kike','cringe']

            for i in cancerWords:
                if i in message.content.lower():
                    await message.delete(delay=1800)

            # if message.author.id in cancerIDs:
            #     await message.delete(delay=1800)

            # Mass mentions
            # if(len(message.mentions) > 0 and
            #         not zb.is_trusted(message,_var.maxRoleRanks)):
            #     count = zb.mention_spamming(message.author)

            #     # Determins action to take
            #     # if 10 or more, ban
            #     if count >= 10:
            #         # Truncates long messages
            #         msg = (message.clean_content[:1021] + '...') if len(message.clean_content) > 1024 else message.clean_content

            #         # Sends edited message
            #         embed=discord.Embed(description=f'**Too many mentions in ' \
            #                 f'{message.channel.mention}** ' \
            #                 f'[Jump to Message]({message.jump_url})', color=0x117ea6)
            #         embed.add_field(name="Message", value=msg,
            #                 inline=False)
            #         embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            #         await zb.print_log(self,message.author,embed)
            #         await message.channel.send(f'I have banned {message.author.mention} ' +
            #                 'for mention spamming.', delete_after=90)
            #         await message.author.ban(reason='Mention spamming')
            #     # if 5 or more, mute
            #     elif count >= 5:
            #         # If no mute role for guild, ignore but warn
            #         add = zb.get_roles_by_group_id(message.guild.id,11)
            #         if len(add) == 0:
            #             # Update database
            #             zb.punish_user(message.author,1)

            #             await message.channel.send(f'Careful {message.author.mention}, ' \
            #                     f'I don\'t want to ban you.', delete_after=90)
            #             return

            #         if zb.get_punish_num(message.author) == 0:
            #             # Update database
            #             zb.punish_user(message.author,1)

            #             embed=discord.Embed(title="Mention Spammer!",
            #                     description=f'**{message.author}** was muted by ' +
            #                     f'**ZigBot**!',
            #                     color=0xd30000)
            #             await zb.print_log_by_group_id(message.guild,80,embed)

            #             # Removes roles and sets mute
            #             rmv = await zb.store_all_special_roles(message,message.author,11)
            #             if len(rmv) != 0:
            #                 await message.author.remove_roles(*rmv,reason='Mention spamming')
            #                 await zb.add_roles(self,message.author,add,'Mention spamming')
            #                 await message.channel.send(f'I have muted {message.author.mention} ' +
            #                         'for mention spamming.', delete_after=90)
            #     # if 3 or more, warn
            #     elif count == 3:
            #         await message.channel.send(f'{message.author.mention}' +
            #                 f'{message.author.mention}{message.author.mention}' +
            #                 ' __**STOP MENTION SPAMMING**__ ' + f'{message.author.mention}' +
            #                 f'{message.author.mention}{message.author.mention}',
            #                 delete_after=90)
            #     # if 3 or more, log
            #     if 10 > count > 2:
            #         # Truncates long messages
            #         msg = (message.clean_content[:1021] + '...') if len(message.clean_content) > 1024 else message.clean_content

            #         # Sends edited message
            #         embed=discord.Embed(description="**Member mention spammed in " +
            #                 message.channel.mention + "** " +
            #                 f'[Jump to Message]({message.jump_url})', color=0x117ea6)
            #         embed.add_field(name="Message", value=msg,
            #                 inline=False)
            #         embed.set_author(name=message.author, icon_url=message.author.avatar_url)
            #         await zb.print_log(self,message.author,embed)

            # Special Channels
            # 1 = poll strict chan
            # 2 = poll and talk chan
            sql = """ SELECT channel_id, group_id
                      FROM channels
                      WHERE channel_id = {0}
                      AND NOT group_id = 0 """
            sql = sql.format(message.channel.id)

            data, rows, string = zb.sql_query(sql)
            if not rows > 0:
                return

            i = 0
            while i < rows:
                # poll channel
                if int(data[i][1]) == 1:
                    if message.content.lower().startswith('poll:'):
                        await message.add_reaction(emoji='\U0001F44D')
                        await message.add_reaction(emoji='\U0001F44E')
                        await message.add_reaction(emoji='\U0001F937')
                    else:
                        await message.channel.send('**Your message will be removed. ' +
                                '__Copy it now!__**\nYou can read this message after ' +
                                'you copy yours.\n\nThis is not in a valid poll ' +
                                'format "Poll: ".\nIf this was  poll, please type ' +
                                '"Poll: " first, then paste in your message.\n' +
                                'Thank you.',delete_after=90)
                        await message.delete(delay=30)

                # General + poll channel
                if int(data[i][1]) == 2 or int(data[i][1]) == 10:
                    if message.content.lower().startswith('poll:'):
                        await message.add_reaction(emoji='\U0001F44D')
                        await message.add_reaction(emoji='\U0001F44E')
                        await message.add_reaction(emoji='\U0001F937')
            # Increment
                i+=1

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
                await zb.bot_errors(self,sp.format(e))

            if message.content.lower().startswith('beetlejuice beetlejuice beetlejuice'):
                x = bytearray.fromhex("536f206c6f6e6720456c204a6573757321").decode()
                print(x)
                pass
        except Exception as e:
            await zb.bot_errors(self,sp.format(e))


def setup(bot):
    bot.add_cog(onmessageCog(bot))
