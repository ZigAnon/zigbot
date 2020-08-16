import discord
from discord.ext import commands
import stackprinter as sp
from bin import zb

class onmessagedeleteCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Events on member join
    @commands.Cog.listener()
    async def on_message_delete(self, message):

        try:
            # If any bot
            if message.author.bot:
                return

            if not zb.is_logged(message.channel.id):
                return

            # Ignore certain phrases
            if message.content.lower().startswith(('.god', '. god', ', god')):
                return

            # If discord porn/spam bot
            # TODO: danger, takes up too many cases
            if zb.is_pattern(message.author.display_name,'^[A-Z]\w+[0-9]{3,}'):
                return

            embed=discord.Embed(description="**Message sent by " +
                    message.author.mention + " deleted in " +
                    message.channel.mention + "**\n" + message.clean_content,
                    color=0xff470f)
            try:
                atch = message.attachments[0].proxy_url
                embed.set_author(name=message.author, url=atch,
                        icon_url=message.author.avatar_url)
                embed.set_thumbnail(url=atch)
            except:
                embed.set_author(name=message.author,
                        icon_url=message.author.avatar_url)
            embed.add_field(name="Channel ID: " + str(message.channel.id)
                    ,value="Message ID: " + str(message.id))
            await zb.print_log(self,message.author,embed)

        except Exception as e:
            await zb.bot_errors(self,sp.format(e))


def setup(bot):
    bot.add_cog(onmessagedeleteCog(bot))
