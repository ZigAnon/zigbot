import discord
import asyncio
from discord.ext import commands
from datetime import datetime
import numpy as np
from bin import zb
from bin import cp

# Settings for guild_id
_guild_check = 509242768401629204

# role_id, role_name, channel_id
_voice_roles = [[538750807538008084,'VC1',509242768829317141],
        [538750916694638602,'VC2',527947459981213696],[538751001881083938,'VC3',0],
        [538751040523337728,'VC5',0],[538751077705842728,'VC6',0],
        [538751116842631168,'VC7',0],[538751158802579456,'VC8',0],
        [538751195725168649,'MC1',513096462335213569],[538751267908878336,'MC2',0],
        [538751306513514508,'MC3',0],[538773262700773380,'SC1',521862351461548033],
        [538773299744997386,'SC2',509243691098177547],[538773327796502546,'SC3',521862247585284098],
        [538773357039058944,'SC4',0],[538773384679522345,'SC5',0]]


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
                    return

        # Ignore if not guild
        if not message.guild is guild:
            return

        # If discord link
        if(not zb.is_trusted(message,5) and zb.is_pattern(message.content.lower(),
                '(https?:\/\/)?(www\.)?(discord\.(gg|io|me|li)|disboard\.org\/server|discordapp\.com\/invite)\/.+([0-9]|[a-z])')):
            punishchan = message.guild.get_channel(517882333752459264)
            embed=discord.Embed(title="Banned!",
                    description=f'**{message.author}** was given Banned by ' +
                    '**ZigBot#1002** for violation of rule 8!',
                    color=0xd30000)
            await punishchan.send(embed=embed)
            await message.author.send('It\'s in the rules, no sharing discord ' +
                    'links.\n Bye bye!')
            await message.author.ban(reason='Posted invite')

        # Gives trusted
        if zb.get_punish_num(message.author) > 0:
            pass
        elif zb.is_trusted(message,5):
            pass
        else:
            now = datetime.utcnow()
            joined = message.author.joined_at
            diff = (now - joined).days
            require = -(diff*diff)*2.2+2000
            if require < 0:
                add = message.guild.get_role(509861871193423873)
                await message.author.add_roles(add,
                        reason=f'Member for {diff} days')
            else:
                sql = """ SELECT m.message_id
                          FROM users u
                          LEFT JOIN messages m ON u.int_user_id = m.int_user_id
                          WHERE m.guild_id = {0}
                          AND u.real_user_id = {1} """
                sql = sql.format(message.guild.id,message.author.id)
                data, rows, string = zb.sql_query(sql)
                await message.channel.send(rows)
                if int(rows) > require:
                    add = message.guild.get_role(509861871193423873)
                    await message.author.add_roles(add,
                            reason=f'{rows} messages in {diff} days.')


    # Events on member join voice
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # Checks for right guild
        try:
            if member.guild.id != _guild_check:
                return
        except:
            return

        args = [self, 'guild_membership', 'voice_updating', _guild_check, member.id]
        try:
            if before.channel is after.channel:
                return
            elif zb.is_updating(*args):
                return
            # Joined voice channel
            elif before.channel is None and not after.channel is None:
                await zb.toggle_updating(*args)
                i = [(i, _voice_roles.index(after.channel.id))
                        for i, _voice_roles in enumerate(_voice_roles)
                        if after.channel.id in _voice_roles][0][0]
                role = member.guild.get_role(_voice_roles[i][0])
                await member.add_roles(role,reason='Joined voice')
                await zb.toggle_updating(*args)
            # Switched voice channel
            elif not before.channel is None and not after.channel is None:
                await zb.toggle_updating(*args)
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
                await zb.toggle_updating(*args)
            # Left voice channel
            elif not before.channel is None and after.channel is None:
                await zb.toggle_updating(*args)
                roles = np.array([x[0] for x in _voice_roles])
                await zb.remove_roles(self,member,roles,'Left voice')
                await zb.toggle_updating(*args)
        except Exception as e:
            await zb.bot_errors(self,e)

    # @commands.command(name='template', description='defined')
    # @is_in_guild(509242768401629204)
    # async def template(self, ctx, member: discord.Member):
    #     """ DESCRIBE """
    #     try:
    #         pass
    #     except Exception as e:
    #         await zb.bot_errors(ctx,e)

    @commands.command(name='hotchicks', description='Posts hot chicks')
    @is_in_guild(509242768401629204)
    async def hotchicks(self, ctx):
        """ Posts SFW hot chicks """
        try:
            await ctx.channel.send('**All these hot chicks**\nhttps://media.giphy.com/media/madDH4fTGefvvL8P96/giphy.gif',
                    delete_after=30)
            await ctx.message.delete()
        except Exception as e:
            await zb.bot_errors(ctx,e)

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
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(CoffeePolCog(bot))
