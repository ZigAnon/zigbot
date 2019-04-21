import discord
import psycopg2 as dbSQL
from discord.ext import commands
from bin import zb_checks


class SetupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='setup', hidden=True)
    async def server_setup(self, ctx):
        """Command which aid's in setting up perms"""
        if zb_checks.is_owner(ctx) or zb_checks.has_permission(ctx,1):

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

        # Ensures only bot owner or user with perms can use command
        if zb_checks.is_owner(ctx) or zb_checks.has_permission(ctx,1):

            # Verifies pattern is valid
            if(zb_checks.pattern(ctx, '^(.\w+)\s+(\w+\W+){1,}(\d)$') and
               int(ctx.message.content[-1:]) >= 0 and
               int(ctx.message.content[-1:]) <= 5):
                role = ctx.message.content[5:-2].lower()
                role_perms = int(ctx.message.content[-1:])
            else:
                await ctx.send('Please use format `.sar <role_name> [1-5]`.')
                return

            # Get role id by name
            role_id, role_name = zb_checks.get_role_id(ctx,role)

            if len(role_id) > 1:
                channel = ctx.message.channel
                select = zb_checks.select(ctx, role_id, role_name, 0)
                await ctx.send('Multiple roles were found for `' + role + '`.\n' +
                               'Which one do you wish to modify:\n' + select)

                def check(m):
                    try:
                        test = int(m.content)
                    except:
                        test = 0
                    return (0 < test <= len(role_id) and
                            m.channel == channel and
                            m.author == ctx.author)

                try:
                    msg = await self.bot.wait_for('message', timeout=10.0, check=check)
                    role_id = role_id[int(msg.content)-1]
                    role_name = role_name[int(msg.content)-1]
                except Exception as e:
                    await ctx.send('Invalid choice. Next time please use a listed number.')
                    return
            else:
                try:
                    role_id = role_id[0]
                except:
                    await ctx.send('Unable to find the role `' + role + '`.\n' +
                                   'Check your spelling and try again.')
                    return

            sql = """ UPDATE roles
                      SET role_perms = %s
                      WHERE guild_id = %s
                      AND role_id = %s """
            conn = None
            updated_rows = 0

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
            except (Exception, dbSQL.DatabaseError) as e:
                await ctx.send(zb_checks.error(e))
            finally:
                if conn is not None:
                    conn.close()

            if updated_rows > 0:
                await ctx.send('Updated role `' + str(role_name) +
                               '` with id `' + str(role_id) +
                               '`.\nPermission is now ' + str(role_perms))
            else:
                await ctx.send('Something went wrong.\n' +
                               'Check the spelling and try again. ' +
                               'I\'ll let <@280455061140930562> know there is an issue')

            return updated_rows


def setup(bot):
    bot.add_cog(SetupCog(bot))
