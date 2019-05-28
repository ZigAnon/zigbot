import math
import discord
from discord.ext import commands
import stackprinter as sp
from bin import zb
from bin import cp


class MembersCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='say', hidden=True)
    @commands.guild_only()
    async def say_remove(self, ctx, *, phrase: str):
        """Removes bot commands."""
        try:
            await ctx.message.delete()

            # Grab punishchan
            sql = """ SELECT channel_id
                      FROM channels
                      WHERE channel_id = {0}
                      AND group_id = 80 """
            sql = sql.format(ctx.channel.id)

            data, rows, string = zb.sql_query(sql)
            if not rows > 0:
                return

            channel = ctx.guild.get_channel(int(data[0][0]))
            permissions = ctx.author.permissions_in(channel)
            if permissions.send_messages and not permissions.manage_webhooks:
                embed=discord.Embed(description=f'{phrase}',
                        color=0x117ea6)
                await zb.print_log_by_group_id(ctx.guild,80,embed)
        except Exception as e:
            await zb.bot_errors(self,sp.format(e))

    @commands.command(name='lsar', hidden=True)
    @commands.guild_only()
    async def list_self_assignable_roles(self, ctx, *args):
        """Lists roles"""
        try:
            # Checks for group 3 roles
            sql = """ SELECT name
                      FROM roles
                      WHERE guild_id = {0}
                      AND group_id = 3
                      ORDER BY group_id ASC, name ASC """
            sql = sql.format(ctx.guild.id)
            roles, rows, junk1 = zb.sql_query(sql)
            # If none found, return
            if rows == 0:
                return

            # Checks for group 4+ roles
            sql = """ SELECT name
                      FROM roles
                      WHERE guild_id = {0}
                      AND group_id >= 4
                      AND group_id <= 5
                      ORDER BY group_id ASC, name ASC """
            sql = sql.format(ctx.guild.id)
            rolesP, rowsP, junk1 = zb.sql_query(sql)

            # Checks if user can talk
            sql = """ SELECT m.role_id
                      FROM role_membership m
                      LEFT JOIN users u ON m.int_user_id = u.int_user_id
                      LEFT JOIN roles r ON m.role_id = r.role_id
                      WHERE m.guild_id = {0}
                      AND u.real_user_id = {1}
                      AND r.group_id = 3 """
            sql = sql.format(ctx.guild.id,ctx.author.id)
            junk1, canTalk, junk2 = zb.sql_query(sql)
            if int(canTalk) == 0:
                rolesP = [[]]
                rowsP = 0

            # Calculate pages
            header = 0
            if rows > 0:
                header += 1
            if rowsP > 0:
                header += 1
            totalRows = rows+rowsP+header
            pages = int(math.ceil((totalRows)/20))
            # Starting page
            try:
                page = int(args[0])
                if page < 1:
                    page = 1
                elif page > pages:
                    page = pages
            except:
                page = 1

            # Build Chat Roles
            embeds = []
            strings = []
            if pages > 1:
                string = '⟪**Chat Roles**⟫\n' + roles[0][0]
                i = 1
                j = 0
                limit = 19
                while i < rows or j < rowsP:
                    while i < rows and i < limit:
                        string = string + '\n' + roles[i][0]
                        # Increment loop
                        i+=1
                        if i == rows:
                            limit = limit - i
                    # Build Vanity Roles
                    while j < rowsP and i == rows and j < limit:
                        if j == 0:
                            string = string + '\n⟪**Vanity Roles**⟫\n' + rolesP[0][0]
                            limit-=1
                        else:
                            string = string + '\n' + rolesP[j][0]
                        # Increment loop
                        j+=1
                    if i == rows:
                        limit = j + 20
                    else:
                        limit = i + 20
                    strings.append(string)
                    string = ''
            else:
                string = '⟪**Chat Roles**⟫\n' + roles[0][0]
                i = 1
                while i < rows:
                    string = string + '\n' + roles[i][0]
                    # Increment loop
                    i+=1
                # Build Vanity Roles
                if rowsP > 0:
                    string = string + '\n⟪**Vanity Roles**⟫\n' + rolesP[0][0]
                    i = 1
                    while i < rowsP:
                        string = string + '\n' + rolesP[i][0]
                        # Increment loop
                        i+=1
                strings.append(string)

            initialEmbed=discord.Embed(color=0xf5d28a)
            initialEmbed.add_field(name=f'**There are {rows+rowsP} self assignable roles**',
                    value=f'{strings[page-1]}')
            i = 0
            while i < pages:
                embed=discord.Embed(color=0xf5d28a)
                embed.add_field(name=f'**There are {rows+rowsP} self assignable roles**',
                        value=f'{strings[i]}')
                embeds.append(embed)
                # Increment loop
                i+=1

            await zb.print_embed_nav(self,ctx,initialEmbed,embeds,pages,page,'')

        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='iam', hidden=True)
    @commands.guild_only()
    async def i_am(self, ctx, *, cmd: str):
        """Adds roles"""
        try:
            if any(x in cmd.lower() for x in ['update','delete',
                'database','table','truncate','commit','drop',
                'insert','create','alter','writepage',';']):
                return

            if not cmd == 'busy':
                # Is user busy
                busy = zb.get_roles_by_group_id(ctx.guild.id,51)[0][0]
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
                if rows == 0 or not ctx.message.channel.id in chan:
                    return

                # Get talk role
                talk = zb.get_roles_by_group_id(ctx.guild.id,2)
                if len(talk) > 0:
                    # Get non-talk role
                    join = zb.get_roles_by_group_id(ctx.guild.id,1)

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

                    # Role doesn't exist
                    if rows == 0:
                        #TODO: role doesnt exist or check spelling

                        # Punishments below
                        # Trusted returns from here
                        if zb.is_trusted(ctx,5):
                            return

                        # Check for shitpost role
                        if not zb.is_role_group(ctx.guild.id,10):
                            return

                        # Check for meme role
                        sql = """ SELECT role_name
                                  FROM meme_roles
                                  WHERE guild_id = {0} """
                        sql = sql.format(ctx.guild.id)
                        role_name, rows, junk2 = zb.sql_query(sql)
                        if rows == 0:
                            return
                        elif cmd in role_name:
                            # If no shitpost role for guild, ignore
                            sql = """ SELECT role_id
                                      FROM roles
                                      WHERE guild_id = {0}
                                      AND group_id = 10 """
                            sql = sql.format(ctx.guild.id)

                            add, rows, junk2 = zb.sql_query(sql)
                            if rows == 0:
                                return

                            await ctx.message.delete()

                            # Update database
                            cp.punish_user(ctx.author,1)

                            # Removes roles and sets shitposter
                            rmv = await zb.store_all_special_roles(ctx,
                                    ctx.author,10)
                            await ctx.author.remove_roles(*rmv,reason='Meme role')
                            await zb.add_roles(self,ctx.author,add,'Meme role')

                            # If no shit chan, skip notify
                            embed=discord.Embed(description=f'{ctx.author.mention} this role ' \
                                    f'is commonly used by memers raiders.\n' \
                                    f'Please contact admin/mod to regain access.',
                                    delete_after=120)
                            await zb.print_log_by_group_id(ctx.guild,10,embed)

                            # If no punish chan, skip log
                            embed=discord.Embed(title="Meme Role!",
                                    description=f'**{ctx.author}** was shitposted pending ' \
                                    f'manual approval.', color=0xd30000, delete_after=120)
                            await zb.print_log_by_group_id(ctx.guild,80,embed)

                        return

                    # Does member have role
                    for role in ctx.author.roles:
                        if role.id == add[0][0]:
                            embed=discord.Embed(description=f'**{ctx.author}** You already have ' \
                                    f'the **{cmd.capitalize()}** role.',
                                    color=0xee281f)
                            await ctx.send(embed=embed)
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

                    # Punishments below
                    # Trusted returns from here
                    if zb.is_trusted(ctx,5):
                        return

                    # Check for shitpost role
                    if not zb.is_role_group(ctx.guild.id,10):
                        return

                    # Check for meme role
                    sql = """ SELECT role_name
                              FROM meme_roles
                              WHERE guild_id = {0} """
                    sql = sql.format(ctx.guild.id)
                    role_name, rows, junk2 = zb.sql_query(sql)
                    if rows == 0:
                        return
                    elif cmd in role_name:
                        # If no shitpost role for guild, ignore
                        sql = """ SELECT role_id
                                  FROM roles
                                  WHERE guild_id = {0}
                                  AND group_id = 10 """
                        sql = sql.format(ctx.guild.id)

                        add, rows, junk2 = zb.sql_query(sql)
                        if rows == 0:
                            return

                        await ctx.message.delete()

                        # Update database
                        cp.punish_user(ctx.author,1)

                        # Removes roles and sets shitposter
                        int_id = zb.get_member_sql_int(ctx.author.id)
                        string = '('
                        rmv = []
                        async with ctx.channel.typing():
                            for role in ctx.author.roles:
                                if not role.name == '@everyone':
                                    string += f'10,{int_id},{ctx.author.id},{ctx.guild.id},{role.id}),('
                                    rmv.append(role)
                            await ctx.author.remove_roles(*rmv,reason='Meme role')
                            await zb.add_roles(self,ctx.author,add,'Meme role')
                            string = string[:-2]
                            zb.add_special_role(string)

                        await ctx.send(f'**{ctx.author}** was shitposted pending ' \
                                f'manual approval.')

                        # If no shit chan, skip notify
                        sql = """ SELECT channel_id
                                  FROM channels
                                  WHERE guild_id = {0}
                                  AND group_id = 10 """
                        sql = sql.format(ctx.guild.id)

                        chan, rows, junk2 = zb.sql_query(sql)
                        if rows != 0:
                            shitchan = ctx.guild.get_channel(int(chan[0][0]))
                            await shitchan.send(f'{ctx.author.mention} this role ' \
                                    f'is commonly used by memers raiders.\n' \
                                    f'Please contact admin/mod to regain access.',
                                    delete_after=120)
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
            data, rows = zb.get_roles_special(ctx.guild.id,51,ctx.author.id)
            if rows > 0:
                await ctx.send('Your status is still set to busy.\n Please `.iamn busy` to get your roles back.',
                        delete_after=15)
                await ctx.message.delete()
                return

            # Removes roles and sets to busy
            int_id = zb.get_member_sql_int(ctx.author.id)
            string = '('
            rmv = []
            async with ctx.channel.typing():
                for role in ctx.author.roles:
                    if not role.name == '@everyone':
                        string += f'51,{int_id},{ctx.author.id},{ctx.guild.id},{role.id}),('
                        rmv.append(role)
                string = string[:-2]
                zb.add_special_role(string)
                await ctx.author.remove_roles(*rmv,reason='Is Busy')
                await zb.add_roles(self,ctx.author,add,'Is Busy')
                embed=discord.Embed(description=f'**{ctx.author}** You now have ' \
                        f'the **{cmd.capitalize()}** role.\nAll other roles are ' \
                        f'removed.', color=0xf5d28a)
                await ctx.send(embed=embed)
                await ctx.author.send('Join voice channel to type `.iamn busy`.')
        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='iamn', aliases=['iamnot'], hidden=True)
    @commands.guild_only()
    async def i_am_not(self, ctx, *, cmd: str):
        """Remove busy role and readd others."""
        try:
            if any(x in cmd.lower() for x in ['update','delete',
                'database','table','truncate','commit','drop',
                'insert','create','alter','writepage',';']):
                return

            if not cmd == 'busy':
                # Is user busy
                busy = zb.get_roles_by_group_id(ctx.guild.id,51)[0][0]
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
                if rows == 0 or not ctx.message.channel.id in chan:
                    return

                # Get talk role
                talk = zb.get_roles_by_group_id(ctx.guild.id,2)
                if len(talk) > 0:
                    # Get non-talk role
                    join = zb.get_roles_by_group_id(ctx.guild.id,1)

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

                    # Does member have role
                    found = False
                    for role in ctx.author.roles:
                        if role.id == rmv[0][0]:
                            found = True
                    if not found:
                        embed=discord.Embed(description=f'**{ctx.author}** You don\'t have ' \
                                f'the **{cmd.capitalize()}** role.',
                                color=0xee281f)
                        await ctx.send(embed=embed)
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
            data, rows = zb.get_roles_special(ctx.guild.id,51,ctx.author.id)
            async with ctx.channel.typing():
                if rows == 0:
                    await ctx.send('You aren\'t busy.\n Please `.iam busy` if you wish to become busy.',
                            delete_after=15)
                    await ctx.message.delete()
                    return
                await zb.add_roles(self,ctx.author,data,'No longer busy')
                await zb.remove_roles(self,ctx.author,rmv,'No longer busy')
                zb.rmv_special_role(ctx.guild.id,51,ctx.author.id)
        except Exception as e:
            await zb.bot_errors(ctx,sp.format(e))


def setup(bot):
    bot.add_cog(MembersCog(bot))
