import discord
import psycopg2 as dbSQL
from discord.ext import commands
from bin import zb_checks


class LookupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='list', hidden=True)
    async def server_setup(self, ctx, *, tool: str):
        """Command which aid's in looking up current settings"""

        # Ensures only bot owner or user with perms can use command
        if zb_checks.is_owner(ctx) or zb_checks.has_permission(ctx,3):

            # Lists current Server Access Roles
            if tool == 'sar':
                try:
                    sql = """ SELECT role_id, name, role_perms
                              FROM roles
                              WHERE role_perms > 0
                              AND guild_id = {0}
                              ORDER BY role_perms, name ASC """
                    conn = None
                    rows = 0

                    try:
                        # connect to the PostgreSQL database
                        conn, cur = zb_checks.sql_login()
                        # execute the QUERY statement
                        cur.execute(sql.format(str(ctx.guild.id)))
                        # get the number of listed rows
                        rows = cur.rowcount
                        # Commit the changes to the database
                        title = '**`List of Server Access Roles`**'
                        data = cur.fetchall()
                        # Close communication with the PostgreSQL database
                        cur.close()
                    except (Exception, dbSQL.DatabaseError) as e:
                        await ctx.send(zb_checks.error(e))
                    finally:
                        if conn is not None:
                            conn.close()
                    # msg = zb_checks.pad_spaces(lst)
                except Exception as e:
                    await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
                else:
                    await ctx.send(zb_checks.print_lookup(rows,data,title))
                    # await ctx.send('**`SUCCESS`**')
            else:
                await ctx.send('**`INVALID OPTION:`** {0}'.format(tool))


def setup(bot):
    bot.add_cog(LookupCog(bot))
