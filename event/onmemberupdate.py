import discord
from discord.ext import commands
from bin import zb

class onmemberupdateCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        try:
            # Ignore self
            if before == self.bot.user:
                return

            if before.nick == after.nick:
                pass
            elif before.nick is None and not after.nick is None:
                if await zb.is_good_nick(self,after):
                    embed=discord.Embed(description=before.mention +
                            " **added nickname**", color=0x117ea6)
                    embed.add_field(name="Before", value=before.display_name,
                            inline=False)
                    embed.add_field(name="After", value=after.display_name,
                            inline=False)
                    embed.set_author(name=before, icon_url=after.avatar_url)
                    await zb.print_log(self,before,embed)
            elif not before.nick is None and not after.nick is None:
                if await zb.is_good_nick(self,after):
                    embed=discord.Embed(description=before.mention +
                            " **nickname changed**", color=0x117ea6)
                    embed.add_field(name="Before", value=before.display_name,
                            inline=False)
                    embed.add_field(name="After", value=after.display_name,
                            inline=False)
                    embed.set_author(name=before, icon_url=after.avatar_url)
                    await zb.print_log(self,before,embed)
            elif not before.nick is None and after.nick is None:
                if await zb.is_good_nick(self,after):
                    embed=discord.Embed(description=before.mention +
                            " **removed nickname**", color=0x117ea6)
                    embed.add_field(name="Before", value=before.display_name,
                            inline=False)
                    embed.add_field(name="After", value=after.display_name,
                            inline=False)
                    embed.set_author(name=before, icon_url=after.avatar_url)
                    await zb.print_log(self,before,embed)

            # Checks for ignored role (voice)
            sql = """ SELECT role_id
                      FROM roles
                      WHERE guild_id = {0}
                      AND group_id = 50
                      AND role_id = {1} """
            if len(before.roles) == len(after.roles):
                pass
            elif len(before.roles) < len(after.roles):
                role = zb.get_diff_role(after.roles,before.roles)
                sql = sql.format(before.guild.id,role.id)
                junk, rows, junk2 = zb.sql_query(sql)
                if rows > 0:
                    return
                if role.name != 'BotAdmin':
                    embed=discord.Embed(description=before.mention +
                            f" **was given the `{role.name}` role**", color=0x117ea6)
                    embed.set_author(name=before, icon_url=after.avatar_url)
                    await zb.print_log(self,before,embed)
            elif len(before.roles) > len(after.roles):
                role = zb.get_diff_role(before.roles,after.roles)
                sql = sql.format(before.guild.id,role.id)
                junk, rows, junk2 = zb.sql_query(sql)
                if rows > 0:
                    return
                if role.name != 'BotAdmin':
                    embed=discord.Embed(description=before.mention +
                            f" **was removed from the `{role.name}` role**", color=0x117ea6)
                    embed.set_author(name=before, icon_url=after.avatar_url)
                    await zb.print_log(self,before,embed)

        except Exception as e:
            await zb.bot_errors(self,e)


def setup(bot):
    bot.add_cog(onmemberupdateCog(bot))
