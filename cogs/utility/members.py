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
        """Adds busy role and removes others."""
        try:
            if not cmd == 'busy':
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
