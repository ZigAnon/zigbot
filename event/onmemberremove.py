import discord
from discord.ext import commands
import stackprinter as sp
from bin import zb

class onmemberremoveCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_member_remove(self, member):

        try:
            # If any bot
            if member.bot:
                return

            # try:
            #     info = await member.guild.fetch_ban(member)
            #     print(info)
            # except:
            #     pass

            # banlist = await member.guild.bans()
            # for banned in banlist:
            #     if member.id == banned.id:
            #         return

            embed=discord.Embed(description=member.mention + " " +
                    member.name, color=0xff470f)
            embed.add_field(name="Join Date", value=member.joined_at,
                    inline=False)
            if not zb.is_pattern(member.display_name,'^[A-Z]\w+[0-9]{3,}'):
                embed.set_thumbnail(url=member.avatar_url)
                embed.set_author(name="Member Left",
                        icon_url=member.avatar_url)

                await zb.print_log(self,member,embed)
                # junk1, junk2 = zb.del_all_special_role(member.guild,member.id)

        except Exception as e:
            await zb.bot_errors(self,sp.format(e))


def setup(bot):
    bot.add_cog(onmemberremoveCog(bot))
