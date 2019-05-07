import discord
from discord.ext import commands
from bin import zb

_ignore_guilds = [509242768401629204]

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

            if len(before.roles) == len(after.roles):
                pass
            elif before.guild.id in _ignore_guilds:
                return
            elif len(before.roles) < len(after.roles):
                role = zb.get_diff_role(after.roles,before.roles)
                if role.name != 'BotAdmin':
                    embed=discord.Embed(description=before.mention +
                            f" **was given the `{role.name}` role**", color=0x117ea6)
                    embed.set_author(name=before, icon_url=after.avatar_url)
                    await zb.print_log(self,before,embed)
            elif len(before.roles) > len(after.roles):
                role = zb.get_diff_role(before.roles,after.roles)
                if role.name != 'BotAdmin':
                    embed=discord.Embed(description=before.mention +
                            f" **was removed from the `{role.name}` role**", color=0x117ea6)
                    embed.set_author(name=before, icon_url=after.avatar_url)
                    await zb.print_log(self,before,embed)

        except Exception as e:
            await zb.bot_errors(self,e)


def setup(bot):
    bot.add_cog(onmemberupdateCog(bot))
