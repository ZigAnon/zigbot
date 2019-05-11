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
    #@is_in_guild(507208948760182800)
    async def define(self, ctx, *, word: str):
        """ Posts navigateable Oxford dictionary list """
        try:
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
            r = requests.get(url, headers = {'app_id' : var.oxID,
                'app_key' : var.oxKey})

            # Checks for 404 or if Definitions is found
            if r.status_code is 200:
                # Builds the list to reduce API calls
                try:
                    data = r.json()
                    howmany = list(data['results'][0]['lexicalEntries'][0]['entries'][0]['senses'])
                    exit = False
                    pass
                except:
                    howmany = [None]
                    exit = True

            count = 0
            cont = f'Test = {count}'
            msg = await ctx.send(cont)
            emojis = []
            ids = [524826613221949440,533784440388845580]

            def a_check(m):
                return (m.author == ctx.message.author and
                        m.channel == ctx.message.channel)

            def r_check(reaction, user):
                return (reaction.message.id == msg.id and user == ctx.author and
                        reaction.message.channel == ctx.message.channel and
                        reaction.emoji.id in ids)

            for id in ids:
                emoji = self.bot.get_emoji(id)
                emojis.append(emoji)
                print(emojis)
                try:
                    await msg.add_reaction(emoji=emoji)
                except:
                    await ctx.send(f'I could not find emoji.id = {id}',
                            delete_after=5)
            while True:
                done, pending = await asyncio.wait([
                                    self.bot.wait_for('message', check=a_check),
                                    self.bot.wait_for('reaction_add', check=r_check),
                                    self.bot.wait_for('reaction_remove', check=r_check)
                                ], timeout = 10, return_when=asyncio.FIRST_COMPLETED)

                try:
                    stuff = done.pop().result()
                except:
                    break

                try:
                    emoji_id = int(zb.get_pattern(str(stuff), '(?<=Emoji\sid=)((\w+)(?=\s))'))
                    emoji_name = zb.get_pattern(str(stuff), "(?<=name=')((\w+)(?='>))")
                    if emoji_id == ids[0]:
                        count -= 1
                        await msg.edit(content=f'Test = {count}')
                    else:
                        count += 1
                        await msg.edit(content=f'Test = {count}')
                except:
                    break

                for future in pending:
                    future.cancel()
            await msg.clear_reactions()
            await msg.edit(delete_after=10)

                # # Skips if error
                # if exit is False:
                #     defNumb = 0
                #     change = 1
                #     addReact = 1
                #     first = True
                #     firstSet = True
                #     forward = 'right'
                #     step = 'left'

                #     # Checks for definition change, if none, it stops
                #     while True:
                #         if change is 1:
                #             change = 0
                #             embed=discord.Embed(title="Oxford Living Dictionary:",
                #                     url=f'https://{language}.oxforddictionaries.com/' \
                #                             f'definition/{search}',
                #                             color=0xf5d28a)
                #             oxford = data['results'][0]['lexicalEntries'][0]['entries'][0]['senses'][defNumb]['definitions']
                #             embed.add_field(name=f'{word.capitalize()}:',
                #                     value=oxford[0],
                #                     inline=False)
                #             embed.set_footer(text=f'{defNumb+1} of {len(howmany)}')
                #             if addReact is 0:
                #                 await msg.edit(embed=embed)

                #         if addReact is 1:
                #             addReact = 0
                #             msg = await ctx.channel.send(embed=embed)
                #             l = await msg.add_reaction('\U00002B05')
                #             m = await msg.add_reaction('\U000027A1')
                #             nav = None
                #         else:
                #             nav = await
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(DictionaryCog(bot))
