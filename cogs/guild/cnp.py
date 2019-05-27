import discord
import asyncio
from discord.ext import commands
import stackprinter as sp
import numpy as np
from bin import zb
from bin import cp

# Settings for guild_id
_guild_check = 509242768401629204

class CoffeePolCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

    #TODO: Add to main loop
    @commands.Cog.listener()
    async def on_message(self, message):
        guild = self.bot.get_guild(509242768401629204)
        # If message in #landing
        if message.channel.id == 574748648072544273:
            await message.delete(delay=120)

        # If any bot
        if message.author.bot:
            return

        # Ignore self
        if message.author == self.bot.user:
            return

        # Adds people to blacklist
        if(message.author in guild.members and
                message.guild is None):
            channel = guild.get_channel(509244241776738304)

            # Sets static values
            member = message.author
            carryMsg = message
            # Looks for last message in admin chats
            async for message in channel.history(limit=500):
                if message.author == member:
                    msg = message

            # Try to get message ctx if found
            try:
                ctx = await self.bot.get_context(msg)
            except:
                return

            # If ctx found, test for permissions
            if(zb.is_trusted(ctx,4) and
                    zb.is_pattern(carryMsg.content,
                        '^([0-9]{14,})\s+(((\w+\s+)+(\w+)?)|(\w+)).+')):
                data = carryMsg.content.split(' ',1)
                sql = """ SELECT real_user_id
                          FROM blacklist
                          WHERE guild_id = {0}
                          AND real_user_id = {1} """
                sql = sql.format(guild.id,data[0])

                junk, rows, junk2 = zb.sql_query(sql)

                # Checks if already in list
                if rows > 0:
                    await carryMsg.author.send('Thank you for reporting ' +
                            f'`{data[0]}`, but it already exists for **{guild.name}**.')
                    return
                else:
                    await carryMsg.author.send(f'I have added `{data[0]}` ' +
                            f'to the blacklist for **{guild.name}**')
                    zb.add_blacklist(message,data[0],data[1])

        # Ignore if not guild
        if not message.guild is guild:
            return

        # Delete @everyone post
        if(not zb.is_trusted(message,5) and
                ('@everyone' in message.content.lower() or
                    '@here' in message.content.lower())):
            await message.delete()

        # If discord link
        if(not zb.is_trusted(message,5) and zb.is_pattern(message.content.lower(),
                '(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|disboard\.org\/server|discordapp\.com\/invite)\/.+([0-9]|[a-z])')):
            punishchan = message.guild.get_channel(517882333752459264)
            embed=discord.Embed(title="Banned!",
                    description=f'**{message.author}** was banned by ' +
                    '**ZigBot#1002** for violation of rule 6!',
                    color=0xd30000)
            await punishchan.send(embed=embed)
            await message.author.send('It\'s in the rules, no sharing discord ' +
                    'links.\n Bye bye!')
            await message.author.ban(reason='Posted invite')

        # If IQ, stop topic
        if(not zb.is_trusted(message,5) and
                (' iq' in message.content.lower() or
                    'iq ' in message.content.lower())):
            await message.channel.send(f'{message.author.mention}, there are ' \
                    f'better arguments than IQ to make your case.\n' \
                    f'https://www.independent.co.uk/news/science/iq-tests' \
                    f'-are-fundamentally-flawed-and-using-them-alone-to-measure' \
                    f'-intelligence-is-a-fallacy-study-8425911.html\n' \
                    f'https://www.cell.com/neuron/fulltext/S0896-6273(12)00584-3',
                    delete_after=300)

    # Events on member join voice
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Checks for right guild
        try:
            if member.guild.id != _guild_check:
                return
        except:
            return

        try:
            # Gather voice channel roles
            sql = """ SELECT role_id,channel_id
                      FROM roles
                      WHERE group_id = 50 """
            data, junk1, junk2 = zb.sql_query(sql)
            _voice_roles = data.astype(int).tolist()

            # If voice channel doesn't change
            if before.channel is after.channel:
                return
            # Joined voice channel
            elif before.channel is None and not after.channel is None:
                sql = """ UPDATE guild_membership g
                          SET voice_channel = {0}
                          FROM (SELECT int_user_id, real_user_id
                          FROM users) AS u
                          WHERE g.int_user_id = u.int_user_id
                          AND g.guild_id = {1}
                          AND u.real_user_id = {2} """
                sql = sql.format(after.channel.id,member.guild.id,member.id)
                junk1, junk2 = zb.sql_update(sql)

                i = [(i, _voice_roles.index(after.channel.id))
                        for i, _voice_roles in enumerate(_voice_roles)
                        if after.channel.id in _voice_roles][0][0]
                role = member.guild.get_role(_voice_roles[i][0])
                await member.add_roles(role,reason='Joined voice')
            # Switched voice channel
            elif not before.channel is None and not after.channel is None:
                sql = """ UPDATE guild_membership g
                          SET voice_channel = {0}
                          FROM (SELECT int_user_id, real_user_id
                          FROM users) AS u
                          WHERE g.int_user_id = u.int_user_id
                          AND g.guild_id = {1}
                          AND u.real_user_id = {2} """
                sql = sql.format(after.channel.id,member.guild.id,member.id)
                junk1, junk2 = zb.sql_update(sql)

                i = [(i, _voice_roles.index(after.channel.id))
                        for i, _voice_roles in enumerate(_voice_roles)
                        if after.channel.id in _voice_roles][0][0]
                try:
                    j = [(i, _voice_roles.index(before.channel.id))
                            for i, _voice_roles in enumerate(_voice_roles)
                            if before.channel.id in _voice_roles][0][0]
                    rmv = member.guild.get_role(_voice_roles[j][0])
                    await member.remove_roles(rmv,reason='Left voice')
                except:
                    pass
                add = member.guild.get_role(_voice_roles[i][0])
                await member.add_roles(add,reason='Joined voice')
            # Left voice channel
            elif not before.channel is None and after.channel is None:
                sql = """ UPDATE guild_membership g
                          SET voice_channel = 0
                          FROM (SELECT int_user_id, real_user_id
                          FROM users) AS u
                          WHERE g.int_user_id = u.int_user_id
                          AND g.guild_id = {0}
                          AND u.real_user_id = {1} """
                sql = sql.format(member.guild.id,member.id)
                junk1, junk2 = zb.sql_update(sql)

                try:
                    j = [(i, _voice_roles.index(before.channel.id))
                            for i, _voice_roles in enumerate(_voice_roles)
                            if before.channel.id in _voice_roles][0][0]
                    rmv = member.guild.get_role(_voice_roles[j][0])
                    await member.remove_roles(rmv,reason='Left voice')
                except:
                    pass
        except Exception as e:
            await zb.bot_errors(self,e)

    # @commands.command(name='template', description='defined')
    # @is_in_guild(509242768401629204)
    # async def template(self, ctx, member: discord.Member):
    #     """ DESCRIBE """
    #     try:
    #         pass
    #     except Exception as e:
    #         await zb.bot_errors(ctx,sp.format(e)

    @commands.command(name='hotchicks', description='Posts hot chicks')
    @is_in_guild(509242768401629204)
    async def hotchicks(self, ctx):
        """ Posts SFW hot chicks """
        try:
            await ctx.channel.send('**All these hot chicks**\nhttps://media.giphy.com/media/madDH4fTGefvvL8P96/giphy.gif',
                    delete_after=30)
            await ctx.message.delete()
        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='roles', description='Redirects to roles page')
    @is_in_guild(509242768401629204)
    async def roles(self, ctx):
        """ When member tries to get all roles,
            this redirects to listed roles """
        try:
            await ctx.channel.send('You can view roles by typing `.lsar` ' +
                    'or going to <#512473259376246808>', delete_after=15)
            await ctx.message.delete()
        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))


def setup(bot):
    bot.add_cog(CoffeePolCog(bot))
