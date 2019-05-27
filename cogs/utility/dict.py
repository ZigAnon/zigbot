import asyncio
import discord
import requests
from discord.ext import commands
import stackprinter as sp
from bin import zb
from bin import zb_config

_var = zb_config


class DictionaryCog(commands.Cog):
    """ Dictionary API calls """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='wdefine', description='Defines word using Merriam-Webster Dictionary.')
    async def wdefine(self, ctx, *, word: str):
        """ Posts navigateable Webster dictionary list """
        try:
            async with ctx.channel.typing():
                embedList = []
                language = 'en'
                search = word.replace(' ', '_').lower()
                url = 'https://www.dictionaryapi.com/api/v3/references/' \
                        f'collegiate/json/{search}?key={_var.webKey}'
                linkurl = '<https://www.merriam-webster.com/dictionary/' \
                        f'{search}>'

                # url Normalized frequency
                r = requests.get(url)

                # Checks for 404 or if Definitions is found
                if r.status_code is 200:
                    # Builds the list to reduce API calls
                    try:
                        data = r.json()
                        howmany = len(list(data))
                    except:
                        return

                    # Loads embeded terms
                    i = 0
                    while i < howmany:
                        print(f'looping {i} for webster')
                        embed=discord.Embed(title="Merriam-Webster Dictionary:",
                                url='https://www.merriam-webster.com/dictionary/' \
                                        f'{search}', color=0xf5d28a)
                        try:
                            webster = data[i]['shortdef']
                        except:
                            msg = await ctx.send(f'Unable to find **{word.capitalize()}** ' \
                                    'in Merriam-Webster', delete_after=10)
                            return
                        embed.add_field(name=f'{word.capitalize()}:',
                                value=webster[0], inline=False)
                        if i == 0:
                            initialEmbed = embed
                        embedList.append(embed)
                        i+=1
            if len(embedList) > 0:
                msg = await zb.print_embed_nav(self,ctx,initialEmbed,
                        embedList,howmany,1,'')
            else:
                msg = await ctx.send(f'Unable to find **{word.capitalize()}** ' \
                        'in Merriam-Webster', delete_after=10)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='define', description='Defines word using Oxford Living Dictionary.')
    async def define(self, ctx, *, word: str):
        """ Posts navigateable Oxford dictionary list """
        try:
            async with ctx.channel.typing():
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
                    except:
                        return

                    # Loads embeded terms
                    i = 0
                    while i < howmany:
                        print(f'looping {i} for oxford')
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
            if len(embedList) > 0:
                msg = await zb.print_embed_nav(self,ctx,initialEmbed,
                        embedList,howmany,1,'')
            else:
                msg = await ctx.send(f'Unable to find **{word.capitalize()}** ' \
                        'in Oxford Living', delete_after=10)

        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))

    @commands.command(name='inspire', description='Generatates inspirational quote with InspiroBot')
    async def inspire(self, ctx):
        """ Posts embeded inspirational image """
        try:
            url = 'http://inspirobot.me/api?generate=true'
            r = requests.get(url)
            embed=discord.Embed(title="I'm InspiroBot.",
                    url='http://inspirobot.me/',
                    color=0x14380D,
                    description='I am an artificial intelligence dedicated to ' +
                    'generating unlimited amounts of unique inspirational quotes ' +
                    'for endless enrichment of pointless human existence.')
            embed.set_thumbnail(url='http://inspirobot.me/website/images/inspirobot-dark-green.png')
            embed.set_image(url=r.text)
            await zb.print_embed_ts(ctx,ctx.author,embed)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,sp.format(e))

def setup(bot):
    bot.add_cog(DictionaryCog(bot))
