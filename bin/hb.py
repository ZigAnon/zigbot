#!/usr/local/bin/python3.6
import discord
import asyncio
import requests
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
from bs4 import BeautifulSoup as bs
import feedparser as fp
import numpy as np
from bin import zb_config
from bin import zb

_var = zb_config

async def _heartbeat(bot):
    timeoff = 0
    count = 0
    try:
        print('working')
        curTime = datetime.now()
        guilds = list(bot.guilds)
        pinged = [0] * len(guilds)

        # Auto Purges specified channels in database
        #await zb.autoPurge(bot)

        #TODO: autoPurge needs to be added
        # grab channels to purge, msg limit, time, checks bot/text

        # Count all users across all servers
        sql = """ SELECT is_bot
                  FROM users
                  WHERE is_bot = FALSE """
        data, rows, string = zb.sql_query(sql)
        await bot.change_presence(activity=discord.Game(name=f'with {rows} users', type=1))

        for guild in guilds:
            sql = """ SELECT * FROM reminders
                      WHERE guild_id = {0}
                      AND NOT interval = 0 """
            sql = sql.format(guild.id)
            array, rows, string = zb.sql_query(sql)
            i = 0
            while i < rows:
                data = array[i]
                data = data.flatten()
                # If Repeat is TRUE
                if data[5]:
                    if int(data[4]) != 0:
                        futureTime = data[7] + timedelta(minutes=int(data[4]))
                        member = guild.get_member(int(data[1]))
                        channel = guild.get_channel(int(data[2]))
                        if datetime.utcnow() > futureTime:
                            sql = """ UPDATE reminders
                                      SET repeat = False,
                                      time = date_trunc('minute', timezone('ZULU', NOW()))
                                      WHERE guild_id = {0}
                                      AND trigger_word = '{1}' """
                            sql = sql.format(guild.id,data[6])
                            rows, string = zb.sql_update(sql)
                            if data[10]:
                                msg = await channel.send(member.mention + ' ' + data[3])
                            else:
                                msg = await channel.send(data[3])
                    else:
                        #TODO: add 4th condition
                        pass
                # If Repeat is FALSE
                else:
                    futureTime = data[7] + timedelta(minutes=(int(data[4])/2))
                    channel = guild.get_channel(int(data[2]))
                    if datetime.utcnow() > futureTime:
                        sql = """ UPDATE reminders
                                  SET time = date_trunc('minute', timezone('ZULU', NOW()))
                                  WHERE guild_id = {0}
                                  AND trigger_word = '{1}' """
                        sql = sql.format(guild.id,data[6])
                        rows, string = zb.sql_update(sql)
                        data[9] = data[9].replace('\\n','\n')
                        msg = await channel.send(data[9])
                    pass
                i+=1

            # RSS Feeds
            try:
                sql = """ SELECT test_value, hook_url, embed_color,
                          avatar_url, parse_url
                          FROM webhooks
                          WHERE guild_id = {0}
                          AND type = 'rss'
                          AND is_active = TRUE """
                sql = sql.format(guild.id)

                data, rows, string = zb.sql_query(sql)
                data = data.tolist()

                # If webhook active, grab test_value
                if rows > 0:
                    i = 0
                    while i < len(data):
                        rss = fp.parse(data[i][4])

                        # cURL import
                        url = data[i][1]
                        headers = {
                            'Content-Type': 'application/json',
                        }

                        dateformat = '%a, %d %b %Y %H:%M:%S %z'
                        lastPost = datetime.strptime(data[i][0],dateformat)
                        oldest = lastPost
                        for post in reversed(rss.entries):
                            articleDate = datetime.strptime(post.published,dateformat)
                            if articleDate > lastPost:
                                try:
                                    soup = bs(post.content[0]['value'], features='html.parser')
                                    thumb = soup.find('img')['src']
                                except:
                                    thumb = ""
                                try:
                                    author = post.author
                                except:
                                    author = rss.feed.title
                                push = ('{' +
                                        '"username": ' + f'"{rss.feed.title}",'
                                        '"embeds": [{' +
                                            '"title": ' + f'"{post.title}",'
                                            '"color": ' + f'{data[i][2]},'
                                            '"url": ' + f'"{post.link}",'
                                            '"description": ' + f'"{post.summary}",'
                                            '"thumbnail": {"url": ' + f'"{thumb}"' + '},'
                                            '"footer": {"text": ' + f'"Published by: {author}"' + '},'
                                            '"timestamp": ' + f'"{articleDate}"' + '}],'
                                            '"avatar_url": ' + f'"{data[i][3]}"' + '}')

                                try:
                                    j = 0
                                    response = requests.post(url, headers=headers, data=push)
                                    if response.status_code == 400:
                                        while response.status_code == 400 and j < 3:
                                            await asyncio.sleep(1)
                                            response = requests.post(url, headers=headers, data=push)
                                            j+=1
                                except:
                                    pass

                                if articleDate > oldest:
                                    oldest = articleDate
                                    # Update recent push
                                    sql = """ UPDATE webhooks
                                              SET test_value = '{0}'
                                              WHERE hook_url = '{1}' """
                                    sql = sql.format(post.published,data[i][1])
                                    junk1, junk2 = zb.sql_update(sql)
                        i+=1

            except Exception as e:
                print(f'**`ERROR:`** {type(e).__name__} - {e}')

    except Exception as e:
        print(f'**`ERROR:`** {type(e).__name__} - {e}')

    return timeoff
