import discord
import psycopg2 as dbSQL
from discord.ext import commands
from bin import zb


class LookupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='list', hidden=True)
    async def server_setup(self, ctx, *, tool: str):
        """Command which aid's in looking up current settings"""

        # Ensures only bot owner or user with perms can use command
        if zb.is_owner(ctx) or zb.has_permission(ctx,3):

            # Lists current Server Access Roles
            if tool == 'sar':
                title = '**`List of Server Access Roles`**'
                sql = """ SELECT role_id, name, role_perms
                          FROM roles
                          WHERE role_perms > 0
                          AND guild_id = {0}
                          ORDER BY role_perms, name ASC """
                sql = sql.format(str(ctx.guild.id))

                data, rows, string = zb.sql_query(sql)
                await zb.print_lookup(ctx,rows,data,title,string)
            else:
                await ctx.send('**`INVALID OPTION:`** {0}'.format(tool))


def setup(bot):
    bot.add_cog(LookupCog(bot))
