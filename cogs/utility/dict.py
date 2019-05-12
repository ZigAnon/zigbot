import asyncio
import discord
import requests
from discord.ext import commands
from bin import zb
from bin import zb_config

_var = zb_config


class DictionaryCog(commands.Cog):
    """ Dictionary API calls """

    def __init__(self, bot):
        self.bot = bot

    def is_in_guild(guild_id):
        async def predicate(ctx):
            return ctx.guild and ctx.guild.id == guild_id
        return commands.check(predicate)

    @commands.command(name='define', description='Defines word using Oxford Living Dictionary.')
    @is_in_guild(507208948760182800)
    async def define(self, ctx, *, word: str):
        """ Posts navigateable Oxford dictionary list """
        try:
            embedList = []
            language = 'en'
            search = word.replace(' ', '_').lower()
            url = 'https://od-api.oxforddictionaries.com:443/api/' \
                    f'v1/entries/{language}/{search}'
            linkurl = f'<https://{language}.oxforddictionaries.com/' \
                    f'definition/{search}>'

            # url Normalized frequency
            urlFR = 'https://od-api.oxforddictionaries.com:443/api/' \
                    f'v1/stats/frequency/word/{language}/' \
                    f'?corpus=nmc&lemma={search}'
            r = requests.get(url, headers = {'app_id' : _var.oxID,
                'app_key' : _var.oxKey})

            # Checks for 404 or if Definitions is found
            if r.status_code is 200:
                # Builds the list to reduce API calls
                try:
                    data = r.json()
                    howmany = len(list(data['results'][0]['lexicalEntries'][0]['entries'][0]['senses']))
                    exit = False
                    pass
                except:
                    return

                # Loads embeded terms
                i = 0
                while i < howmany:
                    embed=discord.Embed(title="Oxford Living Dictionary:",
                            url=f'https://{language}.oxforddictionaries.com/' \
                                    f'definition/{search}',
                                    color=0xf5d28a)
                    oxford = data['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][i]['definitions']
                    embed.add_field(name=f'{word.capitalize()}:',
                            value=oxford[0],
                            inline=False)
                    if i == 0:
                        initialEmbed = embed
                    embedList.append(embed)
                    i+=1
                msg = await zb.print_embed_nav(self,ctx,initialEmbed,
                        embedList,howmany)
                await msg.edit(delete_after=10)
            else:
                msg = await ctx.send(f'Unable to find **{word.capitalize()}** ' \
                        'in Oxford Living', delete_after=10)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(DictionaryCog(bot))
