import discord
import asyncio
from discord.ext import commands
from bin import zb_config
from bin import zb

_var = zb_config
_query = """ SELECT g.guild_id,u.real_user_id,r.role_id,u.name,g.nick,u.int_user_id
             FROM users u
             LEFT JOIN guild_membership g ON u.int_user_id = g.int_user_id
             LEFT JOIN role_membership r ON u.int_user_id = r.int_user_id """

rmvRoles = [[562694658933653524],[562995654079545365],[562995727844900865],
        [562995775940984832],[562998542986379264]]

_int_user_id = """ SELECT int_user_id
                   FROM users
                   WHERE real_user_id = {0} """

_update_punish = """ UPDATE guild_membership
                     SET punished = {0}
                     WHERE int_user_id = {1}
                     AND guild_id = {2} """

def punish_user(member,number):
    sql = _int_user_id.format(member.id)
    data, rows, string = zb.sql_query(sql)
    intID = int(data[0])

    sql = _update_punish.format(number,intID,member.guild.id)
    rows, string = zb.sql_update(sql)

def is_outranked(member1, member2, role_perms):
    """ test for valid data in database at two columns """

    idList1 = []
    for role in member1.roles:
        idList1.append(role.id)

    idList2 = []
    for role in member2.roles:
        idList2.append(role.id)

    sql = """ SELECT MIN(role_perms)
              FROM roles
              WHERE guild_id = {0}
              AND NOT role_perms = 0
              AND role_perms <= {1}
              AND role_id in {2} """
    sql = sql.format(member1.guild.id,
                     role_perms,
                     zb.sql_list(idList1))
    data1, rows, string = zb.sql_query(sql)

    sql = """ SELECT MIN(role_perms)
              FROM roles
              WHERE guild_id = {0}
              AND NOT role_perms = 0
              AND role_perms <= {1}
              AND role_id in {2} """
    sql = sql.format(member2.guild.id,
                     role_perms,
                     zb.sql_list(idList2))
    data2, rows, string = zb.sql_query(sql)

    try:
        var = int(data2[0])
    except:
        return True
    if rows == 0:
        return True
    elif int(data1[0]) < int(data2[0]):
        return True
    else:
        return False


class BanesWeebECog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     # Ignore self
    #     if message.author == self.bot.user:
    #         return

    #     # Adds people to blacklist
    #     guild = self.bot.get_guild(562078425225887777)
    #     if(message.author in guild.members and
    #             message.guild is None):
    #         channel = guild.get_channel(562078853133107230)

    #         # Sets static values
    #         member = message.author
    #         carryMsg = message
    #         # Looks for last message in admin chats
    #         while True:
    #             async for message in channel.history(limit=500):
    #                 if message.author == member:
    #                     msg = message
    #                     break
    #             break

    #         # Try to get message ctx if found
    #         try:
    #             ctx = await self.bot.get_context(msg)
    #         except:
    #             return

    #         # If ctx found, test for permissions
    #         if(zb.is_trusted(ctx,4) and
    #                 zb.is_pattern(carryMsg.content,
    #                     '^([0-9]{14,})\s+(((\w+\s+)+(\w+)?)|(\w+)).+')):
    #             data = carryMsg.content.split(' ',1)
    #             sql = """ SELECT real_user_id
    #                       FROM blacklist
    #                       WHERE guild_id = {0}
    #                       AND real_user_id = {1} """
    #             sql = sql.format(guild.id,data[0])

    #             junk, rows, junk2 = zb.sql_query(sql)

    #             # Checks if already in list
    #             if rows > 0:
    #                 await carryMsg.author.send('Thank you for reporting ' +
    #                         f'`{data[0]}`, but it already exists for **{guild.name}**.')
    #                 return
    #             else:
    #                 await carryMsg.author.send(f'I have added `{data[0]}` ' +
    #                         f'to the blacklist for **{guild.name}**')
    #                 zb.add_blacklist(message,data[0],data[1])

    @commands.command(name='bweshit', hidden=True)
    @is_in_guild(562078425225887777)
    async def bweshitpost(self, ctx, member: discord.Member):
        """ Banishes member to shitpost chat. """
        try:
            if(zb.is_trusted(ctx,4) and
                    is_outranked(ctx.message.author,member,4)):
                shitchan = ctx.guild.get_channel(562764977623138324)
                punishchan = ctx.guild.get_channel(562763458425126912)
                embed=discord.Embed(title="Shitposter!",
                        description=f'**{member}** was given Shitposter by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                msg = await shitchan.send('Looks like you pushed it too far ' +
                        f'{member.mention}. You live here now. Enjoy!!')
                await punishchan.send(embed=embed)
                # Update database
                punish_user(member,1)
                # Get roles
                addRole = ctx.guild.get_role(562695065789530132)
                data = zb.grab_first_col(rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Shitposted')
                # Add role
                await member.add_roles(addRole,reason='Shitposted')
                # Kick from voice
                await member.edit(voice_channel=None)

                await asyncio.sleep(60)
                await msg.delete()
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='bwemute', hidden=True)
    @is_in_guild(562078425225887777)
    async def bwemute(self, ctx, member: discord.Member):
        """ Removes all write permissions from all channels """
        try:
            if(zb.is_trusted(ctx,4) and
                    is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(562763458425126912)
                embed=discord.Embed(title="User Muted!",
                        description=f'**{member}** was muted by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                await punishchan.send(embed=embed)
                # Update database
                punish_user(member,1)
                # Get roles
                addRole = ctx.guild.get_role(562387019188273155)
                data = zb.grab_first_col(rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Muted')
                # Add role
                await member.add_roles(addRole,reason='Muted')
                # Kick from voice
                await member.edit(mute=True)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='bwejail', hidden=True)
    @is_in_guild(562078425225887777)
    async def bwejail(self, ctx, member: discord.Member):
        """ Removes all chats and allows user to state case
            in jail chat."""
        try:
            if(zb.is_trusted(ctx,4) and
                    is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(562763458425126912)
                embed=discord.Embed(title="User Jailed!",
                        description=f'**{member}** was jailed by ' +
                        f'**{ctx.message.author}**!',
                        color=0xd30000)
                await punishchan.send(embed=embed)
                # Update database
                punish_user(member,1)
                # Get roles
                addRole = ctx.guild.get_role(562695118310604810)
                data = zb.grab_first_col(rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Jailed')
                # Add role
                await member.add_roles(addRole,reason='Jailed')
                # Kick from voice
                await member.edit(voice_channel=None)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='bweclean', hidden=True)
    @is_in_guild(562078425225887777)
    async def bwecleanpost(self, ctx, member: discord.Member):
        """ Removes shitpost tag. """
        try:
            if(zb.is_trusted(ctx,4) and
                    is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(562763458425126912)
                embed=discord.Embed(title="Good Job!",
                        description=f'**{member}** it seems ' +
                        f'**{ctx.message.author}** has faith in you.',
                        color=0x27d300)
                await punishchan.send(embed=embed)
                # Update database
                punish_user(member,0)
                # Get roles
                addRole = ctx.guild.get_role(562694658933653524)
                data = zb.grab_first_col(rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Cleanposted')
                # Add role
                await member.add_roles(addRole,reason='Cleanposted')

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='bweunmute', hidden=True)
    @is_in_guild(562078425225887777)
    async def bweunmute(self, ctx, member: discord.Member):
        """ Removes mute status. """
        try:
            if(zb.is_trusted(ctx,4) and
                    is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(562763458425126912)
                embed=discord.Embed(title="User unmuted.",
                        description=f'**{member}** follow the rules.',
                        color=0x27d300)
                await punishchan.send(embed=embed)
                # Update database
                punish_user(member,0)
                # Get roles
                addRole = ctx.guild.get_role(562694658933653524)
                data = zb.grab_first_col(rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Unmuted')
                # Add role
                await member.add_roles(addRole,reason='Unmuted')

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)

    @commands.command(name='bwefree', hidden=True)
    @is_in_guild(562078425225887777)
    async def bwefree(self, ctx, member: discord.Member):
        """ Frees member from jail """
        try:
            if(zb.is_trusted(ctx,4) and
                    is_outranked(ctx.message.author,member,4)):
                punishchan = ctx.guild.get_channel(562763458425126912)
                embed=discord.Embed(title="User Jailed!",
                        description=f'**{member}** was freed by ' +
                        f'**{ctx.message.author}**!',
                        color=0x27d300)
                await punishchan.send(embed=embed)
                # Update database
                punish_user(member,0)
                # Get roles
                addRole = ctx.guild.get_role(562694658933653524)
                data = zb.grab_first_col(rmvRoles)
                # Remove roles
                await zb.remove_roles(self,member,data,'Freed')
                # Add role
                await member.add_roles(addRole,reason='Freed')

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(BanesWeebECog(bot))
