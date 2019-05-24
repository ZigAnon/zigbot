import discord
from discord.ext import commands
from bin import zb

class onmemberremoveCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_member_remove(self, member):

        try:
            # Ignore self
            if member == self.bot.user:
                return

            embed=discord.Embed(description=member.mention + " " +
                    member.name, color=0xff470f)
            embed.add_field(name="Join Date", value=member.joined_at,
                    inline=False)
            embed.set_thumbnail(url=member.avatar_url)
            embed.set_author(name="Member Left",
                    icon_url=member.avatar_url)

            await zb.print_log(self,member,embed)
            junk1, junk2 = zb.rmv_all_special_role(member.guild,member.id)

        except Exception as e:
            await zb.bot_errors(self,e)


def setup(bot):
    bot.add_cog(onmemberremoveCog(bot))
