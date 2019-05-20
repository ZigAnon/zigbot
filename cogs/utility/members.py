import discord
from discord.ext import commands
from bin import zb


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='say', hidden=True)
    @commands.guild_only()
    async def say_remove(self, ctx):
        """Removes bot commands."""
        await ctx.message.delete()

    @commands.command(name='iam', hidden=True)
    @commands.guild_only()
    async def i_am(self, ctx, *, cmd: str):
        """Adds roles"""
        try:
            if not cmd == 'busy':
                # Is user busy
                busy = zb.get_roles_special(ctx.guild.id,51)[0][0]
                for role in ctx.author.roles:
                    if role.id == busy:
                        await ctx.send('Your status is still set to busy.\n Please `.iamn busy` to get your roles back.',
                                delete_after=15)
                        await ctx.message.delete()
                        return

                # Is role channel
                sql = """ SELECT channel_id
                          FROM channels
                          WHERE guild_id = {0}
                          AND group_id = 3 """
                sql = sql.format(ctx.guild.id)
                chan, rows, junk2 = zb.sql_query(sql)
                if rows == 0 or ctx.message.channel.id != chan[0][0]:
                    return

                # Get talk role
                talk = zb.get_roles_special(ctx.guild.id,2)
                if len(talk) > 0:
                    # Get non-talk role
                    join = zb.get_roles_special(ctx.guild.id,1)

                    # Have chat perms
                    sql = """ SELECT m.role_id
                              FROM role_membership m
                              LEFT JOIN roles r ON m.role_id = r.role_id
                              LEFT JOIN users u ON m.int_user_id = u.int_user_id
                              WHERE m.guild_id = {0}
                              AND r.group_id = 2
                              AND u.real_user_id = {1} """
                    sql = sql.format(ctx.guild.id,ctx.author.id)
                    junk1, rows, junk2 = zb.sql_query(sql)
                    if rows > 0:
                        canTalk = True
                    else:
                        canTalk = False

                    # Get role id
                    sql = """ SELECT role_id,group_id
                              FROM roles
                              WHERE guild_id = {0}
                              AND group_id >= 3
                              AND group_id <= 5
                              AND lower(name) = '{1}' """
                    sql = sql.format(ctx.guild.id,cmd.lower())
                    add, rows, junk1 = zb.sql_query(sql)

                    # Does member have role
                    for role in ctx.author.roles:
                        if role.id == add[0][0]:
                            embed=discord.Embed(description=f'**{ctx.author}** You already have ' \
                                    f'the **{cmd.capitalize()}** role.',
                                    color=0xee281f)
                            await ctx.send(embed=embed)
                            return

                    # Role doesn't exist
                    if rows == 0:
                        #TODO: role doesnt exist or check spelling
                        return

                    # Add role
                    if add[0][1] == 3:
                        embed=discord.Embed(description=f'**{ctx.author}** You now have ' \
                                f'the **{cmd.capitalize()}** role.',
                                color=0xf5d28a)
                        await ctx.send(embed=embed)
                        add = ctx.guild.get_role(add[0][0])
                        await ctx.author.add_roles(add)
                        if not canTalk:
                            add = ctx.guild.get_role(talk[0][0])
                            join = ctx.guild.get_role(join[0][0])
                            await ctx.author.add_roles(add)
                            await ctx.author.remove_roles(join,reason='Added political role')
                    elif add[0][1] == 4:
                        embed=discord.Embed(description=f'**{ctx.author}** You now have ' \
                                f'the **{cmd.capitalize()}** role.',
                                color=0xf5d28a)
                        await ctx.send(embed=embed)
                        add = ctx.guild.get_role(add[0][0])
                        await ctx.author.add_roles(add)
                        if not canTalk:
                            embed=discord.Embed(description=f'**{ctx.author}** You aren\'t ' \
                                    f'allowed to chat without an ideology. Please choose ' \
                                    f'a role from #roles or `.lsar`.', color=0xf5d28a)
                            await ctx.send(embed=embed,delete_after=60)
                            await ctx.message.delete(delay=5)
                    return

            if ctx.author.permissions_in(ctx.channel).administrator:
                await ctx.send('As much as I would like to, I\'m not able to set you to busy.\n It\'s out of my power.')
                return

            # If no busy role for guild, ignore
            sql = """ SELECT role_id
                      FROM roles
                      WHERE guild_id = {0}
                      AND group_id = 51 """
            sql = sql.format(ctx.guild.id)

            add, rows, junk2 = zb.sql_query(sql)
            if rows == 0:
                return

            # If punished, can't use command
            sql = """ SELECT g.punished
                      FROM guild_membership g
                      LEFT JOIN users u ON g.int_user_id = u.int_user_id
                      WHERE g.guild_id = {0}
                      AND NOT punished = 0
                      AND u.real_user_id = {1} """
            sql = sql.format(ctx.guild.id,ctx.author.id)

            junk1, rows, junk2 = zb.sql_query(sql)
            if rows > 0:
                await ctx.send('You cannot use this command if punished.',
                        delete_after=15)
                await ctx.message.delete()
                return

            # Gathers removed roles and checks if busy
            sql = """ SELECT role_id
                      FROM special_roles
                      WHERE guild_id = {0}
                      AND type = 51
                      AND real_user_id = {1} """
            sql = sql.format(ctx.guild.id,ctx.author.id)
            data, rows, junk2 = zb.sql_query(sql)
            if rows > 0:
                await ctx.send('Your status is still set to busy.\n Please `.iamn busy` to get your roles back.',
                        delete_after=15)
                await ctx.message.delete()
                return

            # Removes roles and sets to busy
            int_id = zb.get_member_sql_int(ctx.author.id)
            string = '('
            rmv = []
            for role in ctx.author.roles:
                if not role.name == '@everyone':
                    string += f'51,{int_id},{ctx.author.id},{ctx.guild.id},{role.id}),('
                    rmv.append(role)
            await ctx.author.remove_roles(*rmv,reason='Is Busy')
            await zb.add_roles(self,ctx.author,add,'Is Busy')
            embed=discord.Embed(description=f'**{ctx.author}** You now have ' \
                    f'the **{cmd.capitalize()}** role.\nAll other roles are ' \
                    f'removed.', color=0xf5d28a)
            await ctx.send(embed=embed)
            string = string[:-2]
            zb.add_special_role(string)
        except Exception as e:
            await zb.bot_errors(ctx,e)

    @commands.command(name='iamn', aliases=['iamnot'], hidden=True)
    @commands.guild_only()
    async def i_am_not(self, ctx, *, cmd: str):
        """Remove busy role and readd others."""
        try:
            if not cmd == 'busy':
                # Is user busy
                busy = zb.get_roles_special(ctx.guild.id,51)[0][0]
                for role in ctx.author.roles:
                    if role.id == busy:
                        await ctx.send('Your status is still set to busy.\n Please `.iamn busy` to get your roles back.',
                                delete_after=15)
                        await ctx.message.delete()
                        return

                # Is role channel
                sql = """ SELECT channel_id
                          FROM channels
                          WHERE guild_id = {0}
                          AND group_id = 3 """
                sql = sql.format(ctx.guild.id)
                chan, rows, junk2 = zb.sql_query(sql)
                if rows == 0 or ctx.message.channel.id != chan[0][0]:
                    return

                # Get talk role
                talk = zb.get_roles_special(ctx.guild.id,2)
                if len(talk) > 0:
                    # Get non-talk role
                    join = zb.get_roles_special(ctx.guild.id,1)

                    # Get role id
                    sql = """ SELECT role_id,group_id
                              FROM roles
                              WHERE guild_id = {0}
                              AND group_id >= 3
                              AND group_id <= 5
                              AND lower(name) = '{1}' """
                    sql = sql.format(ctx.guild.id,cmd.lower())
                    rmv, rows, junk1 = zb.sql_query(sql)
                    if rows == 0:
                        #TODO: role doesnt exist or check spelling
                        return

                    # Remove found role
                    rmv = ctx.guild.get_role(rmv[0][0])
                    await ctx.author.remove_roles(rmv)
                    embed=discord.Embed(description=f'**{ctx.author}** You no ' \
                            f'longer have the **{cmd.capitalize()}** role.',
                            color=0xf5d28a)
                    await ctx.send(embed=embed)

                    # Check for talking roles
                    sql = """ SELECT m.role_id
                              FROM role_membership m
                              LEFT JOIN roles r ON m.role_id = r.role_id
                              LEFT JOIN users u ON m.int_user_id = u.int_user_id
                              WHERE m.guild_id = {0}
                              AND r.group_id = 3
                              AND u.real_user_id = {1} """
                    sql = sql.format(ctx.guild.id,ctx.author.id)
                    junk1, rows, junk2 = zb.sql_query(sql)
                    if rows == 0:
                        rmv = ctx.guild.get_role(talk[0][0])
                        add = ctx.guild.get_role(join[0][0])
                        await ctx.author.remove_roles(rmv)
                        await ctx.author.add_roles(add,reason='Removed political roles')

                        # Inform user that they removed all talking roles
                        embed=discord.Embed(description=f'**{ctx.author}** You aren\'t ' \
                                f'allowed to chat without an ideology. Please choose ' \
                                f'a role from #roles or `.lsar`.', color=0xf5d28a)
                        await ctx.send(embed=embed,delete_after=60)
                        await ctx.message.delete(delay=5)
                    return

            # If no busy role for guild, ignore
            sql = """ SELECT role_id
                      FROM roles
                      WHERE guild_id = {0}
                      AND group_id = 51 """
            sql = sql.format(ctx.guild.id)

            rmv, rows, junk2 = zb.sql_query(sql)
            if rows == 0:
                return

            # If punished, can't use command
            sql = """ SELECT g.punished
                      FROM guild_membership g
                      LEFT JOIN users u ON g.int_user_id = u.int_user_id
                      WHERE g.guild_id = {0}
                      AND NOT punished = 0
                      AND u.real_user_id = {1} """
            sql = sql.format(ctx.guild.id,ctx.author.id)

            junk1, rows, junk2 = zb.sql_query(sql)
            if rows > 0:
                return

            # Gathers removed roles and checks if busy
            sql = """ SELECT role_id
                      FROM special_roles
                      WHERE guild_id = {0}
                      AND type = 51
                      AND real_user_id = {1} """
            sql = sql.format(ctx.guild.id,ctx.author.id)
            data, rows, junk2 = zb.sql_query(sql)
            if rows == 0:
                await ctx.send('You aren\'t busy.\n Please `.iam busy` if you wish to become busy.',
                        delete_after=15)
                await ctx.message.delete()
                return
            await zb.add_roles(self,ctx.author,data,'No longer busy')
            await zb.remove_roles(self,ctx.author,rmv,'No longer busy')
            zb.rmv_special_role(ctx.guild.id,51,ctx.author.id)
        except Exception as e:
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(MembersCog(bot))
