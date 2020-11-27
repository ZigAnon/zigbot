import discord
import asyncio
import random
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
import stackprinter as sp
import numpy as np
from bin import zb
from bin import cp

# Settings for guild_id
_guild_check = 744322815469027376

class ThatPublicServerCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

    # Events on member update
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            # If any bot
            if before.bot:
                return

            if before.guild.id != _guild_check:
                return

            try:
                # If punished, no log
                punished = zb.get_punish_num(before)
                if punished > 0:
                    return
                # If busy, no log
                data, rows = zb.get_roles_special(before.guild.id,51,before.id)
                if rows > 0:
                    return
                busy = zb.get_roles_by_group_id(before.guild.id,51)[0][0]
                for role in before.roles:
                    if role.id == busy:
                        return
            except:
                pass

            # # If user has 200 messages and is on server > 14 days
            # sql = """ SELECT DISTINCT m.message_id
            #           FROM messages m
            #           LEFT JOIN users u ON m.int_user_id = u.int_user_id
            #           LEFT JOIN guild_membership g ON m.int_user_id = g.int_user_id
            #           WHERE NOT m.int_user_id in (
            #               SELECT m.int_user_id
            #               FROM role_membership m
            #               LEFT JOIN roles r ON m.role_id = r.role_id
            #               WHERE r.role_perms >= 5
            #               AND m.guild_id = {0})
            #           AND g.guild_id = {0}
            #           AND u.real_user_id = {1}
            #           AND g.punished = 0
            #           AND g.joined_at <= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '14 days' """
            # sql = sql.format(before.guild.id,before.id)
            # data, rows, junk1 = zb.sql_query(sql)
            # if rows < 200:
            #     return

            # # Calculate Trusted
            # now = datetime.utcnow()
            # joined = before.joined_at
            # diff = (now - joined).days

            # require = -(80*diff)+2200
            # if require < 200:
            #     require = 200
            # if require < rows:
            #     sql = """ SELECT role_id
            #               FROM roles
            #               WHERE guild_id = {0}
            #               AND role_perms = 5 """
            #     sql = sql.format(before.guild.id)
            #     data, junk1, junk2 = zb.sql_query(sql)
            #     trusted = before.guild.get_role(data[0][0])
            #     await before.add_roles(trusted,reason=f'Member has been in server {diff} days with {rows} messages')

        except Exception as e:
            await zb.bot_errors(self,sp.format(e))

    # @commands.Cog.listener()
    # async def on_message(self, message):
    #     try:
    #         # If any bot
    #         if message.author.bot:
    #             return

    #         # Ignore self
    #         if message.author == self.bot.user:
    #             return
    #         # Ignore if not guild
    #         if not message.guild is guild:
    #             return

    #         # Delete @everyone post
    #         if(not zb.is_trusted(message,5) and
    #                 ('@everyone' in message.content.lower() or
    #                     '@here' in message.content.lower())):
    #             await message.delete()

    #         # If discord link
    #         # if(not zb.is_trusted(message,5) and zb.is_pattern(message.content.lower(),
    #         #         '(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|disboard\.org\/server|discordapp\.com\/invite)\/.+([0-9]|[a-z])')):
    #         #     punishchan = message.guild.get_channel(517882333752459264)
    #         #     embed=discord.Embed(title="Banned!",
    #         #             description=f'**{message.author}** was banned by ' +
    #         #             '**ZigBot#1002** for violation of rule 6!',
    #         #             color=0xd30000)
    #         #     await punishchan.send(embed=embed)
    #         #     await message.author.send('It\'s in the rules, no sharing discord ' +
    #         #             'links.\n Bye bye!')
    #         #     await message.author.ban(reason='Posted invite')
    #     except Exception as e:
    #         await zb.bot_errors(self,sp.format(e))

    # Events on member join voice
    # @commands.Cog.listener()
    # async def on_voice_state_update(self, member, before, after):
    #     # Checks for right guild
    #     try:
    #         if member.guild.id != _guild_check:
    #             return
    #     except:
    #         return

    #     try:
    #         # Gather voice channel roles
    #         sql = """ SELECT role_id,channel_id
    #                   FROM roles
    #                   WHERE group_id = 50 """
    #         data, junk1, junk2 = zb.sql_query(sql)
    #         _voice_roles = data.astype(int).tolist()

    #         # If voice channel doesn't change
    #         if before.channel is after.channel:
    #             return
    #         # Joined voice channel
    #         elif before.channel is None and not after.channel is None:
    #             sql = """ UPDATE guild_membership g
    #                       SET voice_channel = {0}
    #                       FROM (SELECT int_user_id, real_user_id
    #                       FROM users) AS u
    #                       WHERE g.int_user_id = u.int_user_id
    #                       AND g.guild_id = {1}
    #                       AND u.real_user_id = {2} """
    #             sql = sql.format(after.channel.id,member.guild.id,member.id)
    #             junk1, junk2 = zb.sql_update(sql)

    #             try:
    #                 i = [(i, _voice_roles.index(after.channel.id))
    #                         for i, _voice_roles in enumerate(_voice_roles)
    #                         if after.channel.id in _voice_roles][0][0]
    #                 role = member.guild.get_role(_voice_roles[i][0])
    #                 await member.add_roles(role,reason='Joined voice')
    #             except:
    #                 pass
    #         # Switched voice channel
    #         elif not before.channel is None and not after.channel is None:
    #             sql = """ UPDATE guild_membership g
    #                       SET voice_channel = {0}
    #                       FROM (SELECT int_user_id, real_user_id
    #                       FROM users) AS u
    #                       WHERE g.int_user_id = u.int_user_id
    #                       AND g.guild_id = {1}
    #                       AND u.real_user_id = {2} """
    #             sql = sql.format(after.channel.id,member.guild.id,member.id)
    #             junk1, junk2 = zb.sql_update(sql)
    #             try:
    #                 try:
    #                     j = [(i, _voice_roles.index(before.channel.id))
    #                             for i, _voice_roles in enumerate(_voice_roles)
    #                             if before.channel.id in _voice_roles][0][0]
    #                     rmv = member.guild.get_role(_voice_roles[j][0])
    #                     await member.remove_roles(rmv,reason='Left voice')
    #                 except:
    #                     pass
    #                 i = [(i, _voice_roles.index(after.channel.id))
    #                         for i, _voice_roles in enumerate(_voice_roles)
    #                         if after.channel.id in _voice_roles][0][0]
    #                 add = member.guild.get_role(_voice_roles[i][0])
    #                 await member.add_roles(add,reason='Joined voice')
    #             except:
    #                 pass
    #         # Left voice channel
    #         elif not before.channel is None and after.channel is None:
    #             sql = """ UPDATE guild_membership g
    #                       SET voice_channel = 0
    #                       FROM (SELECT int_user_id, real_user_id
    #                       FROM users) AS u
    #                       WHERE g.int_user_id = u.int_user_id
    #                       AND g.guild_id = {0}
    #                       AND u.real_user_id = {1} """
    #             sql = sql.format(member.guild.id,member.id)
    #             junk1, junk2 = zb.sql_update(sql)

    #             try:
    #                 j = [(i, _voice_roles.index(before.channel.id))
    #                         for i, _voice_roles in enumerate(_voice_roles)
    #                         if before.channel.id in _voice_roles][0][0]
    #                 rmv = member.guild.get_role(_voice_roles[j][0])
    #                 await member.remove_roles(rmv,reason='Left voice')
    #             except:
    #                 pass
    #     except Exception as e:
    #         await zb.bot_errors(self,sp.format(e))

    # @commands.command(name='template', description='defined')
    # @is_in_guild(509242768401629204)
    # async def template(self, ctx, member: discord.Member):
    #     """ DESCRIBE """
    #     try:
    #         pass
    #     except Exception as e:
    #         await zb.bot_errors(ctx,sp.format(e))

    # @commands.command(name='temp', description='Command to fix things I break')
    # @commands.is_owner()
    # async def temp_command(self, ctx):
    #     """ Command to fix things I break """
    #     try:
    #         tempID = 744625525573550081
    #         tempRole = ctx.guild.get_role(tempID)
    #         for member in ctx.guild.members:
    #             try:
    #                 await member.add_roles(tempRole,reason=f'Adding Employee role seperator')
    #             except:
    #                 pass
    #     except Exception as e:
    #         await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='settopic', description='Sets Temp role to Employee')
    @is_in_guild(744322815469027376)
    async def set_topic(self, ctx, *, roomName: str):
        """ Sets Event Room names """
        try:
            if not zb.is_trusted(ctx,3):
                return

            textChannel = ctx.guild.get_channel(768167677151674389)
            voiceChannel = ctx.guild.get_channel(762464559314763838)
            oldName = textChannel.name

            await voiceChannel.edit(name=roomName,reason=f'Changed by {ctx.author}')
            await textChannel.edit(name=roomName,reason=f'Changed by {ctx.author}')
            await ctx.channel.send(f'Event 1 Changed:\nfrom {oldName} to ' \
                    f'<#{textChannel.id}>')

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='settopic2', description='Sets Temp role to Employee')
    @is_in_guild(744322815469027376)
    async def set_topic2(self, ctx, *, roomName: str):
        """ Sets Event Room names """
        try:
            if not zb.is_trusted(ctx,3):
                return

            textChannel = ctx.guild.get_channel(768167712224444436)
            voiceChannel = ctx.guild.get_channel(768167756541460500)
            oldName = textChannel.name

            await voiceChannel.edit(name=roomName,reason=f'Changed by {ctx.author}')
            await textChannel.edit(name=roomName,reason=f'Changed by {ctx.author}')
            await ctx.channel.send(f'Event 2 Changed:\nfrom {oldName} to ' \
                    f'<#{textChannel.id}>')

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='settopic18', description='Sets Temp role to Employee')
    @is_in_guild(744322815469027376)
    async def set_topic18(self, ctx, *, roomName: str):
        """ Sets Event Room names """
        try:
            if not zb.is_trusted(ctx,3):
                return

            textChannel = ctx.guild.get_channel(768598542943125535)
            voiceChannel = ctx.guild.get_channel(768598571851055134)
            oldName = textChannel.name

            await voiceChannel.edit(name=roomName,reason=f'Changed by {ctx.author}')
            await textChannel.edit(name=roomName,reason=f'Changed by {ctx.author}')
            await ctx.channel.send(f'Mature Event Changed:\nfrom {oldName} to ' \
                    f'<#{textChannel.id}>')

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='hire', description='Sets Temp role to Employee')
    @is_in_guild(744322815469027376)
    async def new_hire(self, ctx, member: discord.Member):
        """ Sets Temp role to Employee """
        try:
            if not zb.is_trusted(ctx,3):
                return

            # Get Roles
            tempID = 744623716398268539
            empID = 744623766063022203
            empRanksID = 744625525573550081
            flairRolesID = 744626018085634198
            welcomeChan = 744322816156893228
            empRole = ctx.guild.get_role(empID)
            empRanksRole = ctx.guild.get_role(empRanksID)
            flairRolesRole = ctx.guild.get_role(flairRolesID)
            tempRole = ctx.guild.get_role(tempID)

            # Assign and remove roles
            await member.add_roles(empRole,reason=f'Member hired by {ctx.author}')
            await member.remove_roles(tempRole,reason=f'Member hired by {ctx.author}')
            await member.add_roles(flairRolesRole,reason=f'Member hired by {ctx.author}')
            await member.add_roles(empRanksRole,reason=f'Member hired by {ctx.author}')

            # Log hire
            embed=discord.Embed(description=f'**{member.mention} ' \
                    f'was hired by #{ctx.author}**',
                    color=0x23d160)
            embed.set_author(name=member, icon_url=member.avatar_url)
            await zb.print_log(self,member,embed)

            # Vocalize hire
            embed=discord.Embed(description=f'**Congratulation! ' \
                    f'{member.mention} was hired by #{ctx.author}**',
                    color=0x23d160)
            embed.set_author(name=member, icon_url=member.avatar_url)
            await ctx.channel.send(embed=embed)

            # Let people know they were hired
            welChan = ctx.guild.get_channel(welcomeChan)
            msg = f'Welcome {member.mention}!  <#{welcomeChan}> is the server\'s ' \
            f'main chat!  Take a look around and be sure to assign some roles in ' \
            f'<#751657293522796645>!'
            await welChan.send(msg,delete_after=300)


            # Remove message
            await ctx.message.delete()
        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))


def setup(bot):
    bot.add_cog(ThatPublicServerCog(bot))
