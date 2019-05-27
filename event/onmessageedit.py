import discord
from discord.ext import commands
import stackprinter as sp
from bin import zb

class onmessageeditCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        try:
            # If any bot
            if before.author.bot:
                return

            # Counts embeded links
            try:
                eCount = len(after.embeds)
            except:
                eCount = 0

            if(before.clean_content == after.clean_content and
                    eCount > 0):
                return

            # Truncates long messages
            bcc = (before.clean_content[:1021] + '...') if len(before.clean_content) > 1024 else before.clean_content
            acc = (after.clean_content[:1021] + '...') if len(after.clean_content) > 1024 else after.clean_content

            # Sends edited message
            embed=discord.Embed(description="**Message edited in " +
                    before.channel.mention + "** " +
                    f'[Jump to Message]({before.jump_url})', color=0x117ea6)
            embed.add_field(name="Before", value=bcc,
                    inline=False)
            embed.set_author(name=before.author, icon_url=before.author.avatar_url)
            embed.add_field(name="After", value=acc,
                    inline=False)
            await zb.print_log(self,before.author,embed)
        except Exception as e:
            await zb.bot_errors(self,sp.format(e))


def setup(bot):
    bot.add_cog(onmessageeditCog(bot))
