import discord
from discord.ext import commands
from bin import zb_checks


class SetupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    # Hidden means it won't show up on the default help.
    @commands.command(name='setup', hidden=True)
    async def server_setup(self, ctx):
        if zb_checks.is_owner(ctx) or zb_checks.has_permission(ctx,1):
            """Command which aid's in setting up perms"""

            embed=discord.Embed(title="Choose from selection below to setup server.")
            embed.set_author(name="Server Setup Menu",
                             icon_url=self.bot.user.avatar_url)
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name="Set admin roles",
                            value=".sar \<role_name\> [1-5]",
                            inline=False)
            embed.set_footer(text="Type '.setup' to start over.")
            await ctx.send(embed=embed)

            print(zb_checks.is_owner(ctx))
            print(ctx.guild.id)

    # Hidden means it won't show up on the default help.
    @commands.command(name='sar', hidden=True)
    async def set_role(self, ctx):
        """ allow role permissions """
        if(zb_checks.pattern(ctx, '^(.\w+)\s+(\w+\W+){1,}(\d)$') and
           int(ctx.message.content[-1:]) >= 1 and
           int(ctx.message.content[-1:]) <= 5):
            pass
        else:
            await ctx.send('Please use format `.sar <role_name> [1-5]`.')
            return
        if zb_checks.is_owner(ctx) or zb_checks.has_permission(ctx,1):
            try:
                role = a
                pass
            except:
                await ctx.send('Please use format `.sar <role_name> [1-5]`.')
                return

            sql = """ UPDATE roles
                      SET role_perms = %s
                      WHERE guild_id = %s
                      AND role_id = %s """
            conn = None
            updated_rows = 0

            role_perms = 1
            role_id = 533701082283638797

            try:
                # connect to the PostgreSQL database
                conn, cur = zb_checks.sql_login()
                # execute the UPDATE  statement
                cur.execute(sql, (role_perms, ctx.guild.id, role_id))
                # get the number of updated rows
                updated_rows = cur.rowcount
                # Commit the changes to the database
                conn.commit()
                # Close communication with the PostgreSQL database
                cur.close()
            except (Exception, dbSQL.DatabaseError) as error:
                print(error)
            finally:
                if conn is not None:
                    conn.close()

            return updated_rows


def setup(bot):
    bot.add_cog(SetupCog(bot))
