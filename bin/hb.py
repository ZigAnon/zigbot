#!/usr/local/bin/python3.6
import discord
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
    lub = datetime.now()
    timeoff = 0
    try:
        curTime = datetime.now()
        guilds = list(bot.guilds)
        pinged = [0] * len(guilds)

        for guild in guilds:
            # Update member count
            memberChan = False
            memCount = 0
            sql = """ SELECT members
                      FROM guilds
                      WHERE guild_id = {0} """
            sql = sql.format(guild.id)
            data, rows, string = zb.sql_query(sql)

            for member in guild.members:
                if not member.bot:
                    memCount += 1
            if memCount != data[0]:
                sql = """ UPDATE guilds
                          SET members = {0}
                          WHERE guild_id = {1} """
                sql = sql.format(memCount,guild.id)
                junk, junk1 = zb.sql_update(sql)

                for channel in guild.voice_channels:
                    if channel.name.lower().startswith('members: '):
                        await channel.edit(name=f'Members: {memCount}',
                                reason='Member count')
                        memberChan = True
                if not memberChan:
                    chan = await guild.create_voice_channel(name=f'Members: {memCount}',
                            reason='Member count')
                    await chan.edit(position=0)

            # Remove bans from users that hammered server
            zb.reset_hammer(guild)

            # Perform reminders
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

            # Every 15 mins
            try:
                time = datetime.utcnow().minute
                if time in [0,15,30,45]:
                    vRoles = zb.get_roles_by_group_id(guild.id,50)
                    # Count all users across all servers
                    sql = """ SELECT is_bot
                              FROM users
                              WHERE is_bot = FALSE """
                    data, rows, string = zb.sql_query(sql)
                    await bot.change_presence(activity=discord.Game(name=f'with {rows} users', type=1))

                    # SQL TASKS
                    zb.reset_voice_updating(guild)
            except Exception as e:
                await zb.bot_errors(self,sp.format(e))

            # Voice role check
            try:
                # Adds missing role
                sql = """ SELECT miss.real_user_id, rr.role_id
                          FROM (
                              SELECT u.real_user_id,g.guild_id,g.voice_channel
                              FROM guild_membership g
                              LEFT JOIN roles r ON g.voice_channel = r.channel_id
                              LEFT JOIN users u ON g.int_user_id = u.int_user_id
                              LEFT JOIN role_membership m ON (
                                  r.role_id = m.role_id
                                  AND m.role_id in (
                                      SELECT role_id
                                      FROM roles
                                      WHERE group_id = 50)
                                  )
                              WHERE g.guild_id = {0}
                              AND g.is_member = TRUE
                              AND m.guild_id IS NULL
                              AND NOT g.voice_channel = 0) miss
                          LEFT JOIN roles rr ON miss.voice_channel = rr.channel_id """
                sql = sql.format(guild.id)

                data, rows, string = zb.sql_query(sql)
                if rows > 0:
                    i = 0
                    while i < rows:
                        member = guild.get_member(data[i][0])
                        add = guild.get_role(data[i][1])
                        await member.add_roles(add,reason='Voice chat fix')
                        i+=1

                # Removes extra roles
                sql = """ SELECT u.real_user_id, m.role_id
                          FROM role_membership m
                          LEFT JOIN users u ON m.int_user_id = u.int_user_id
                          LEFT JOIN guild_membership g ON m.int_user_id = g.int_user_id
                          WHERE role_id in (
                              SELECT role_id
                              FROM roles
                              WHERE group_id = 50)
                          AND m.guild_id = {0}
                          AND g.guild_id = {0}
                          AND g.is_member = TRUE
                          AND g.voice_channel = 0 """
                sql = sql.format(guild.id)

                data, rows, string = zb.sql_query(sql)
                if rows > 0:
                    i = 0
                    while i < rows:
                        member = guild.get_member(data[i][0])
                        rmv = guild.get_role(data[i][1])
                        await member.remove_roles(rmv,reason='Voice chat fix')
                        i+=1

            except Exception as e:
                await zb.bot_errors(self,sp.format(e))

            # Auto purge channels
            try:
                sql = """ SELECT channel_id, message_limit, days_to_keep, del_check
                          FROM channels
                          WHERE guild_id = {0}
                          AND (
                              last_message >= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '5 minutes'
                              OR last_message <= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '1 week'
                          )
                          AND auto_purge = TRUE
                          AND is_deleted = FALSE """
                sql = sql.format(guild.id)

                data, rows, string = zb.sql_query(sql)
                data = data.tolist()

                # if purge channels found
                if rows > 0:
                    i = 0
                    while i < rows:
                        pChan = guild.get_channel(int(data[i][0]))
                        limit = int(data[i][1])
                        days = int(data[i][2])
                        beforeTime = datetime.now() - timedelta(days=days)
                        try:
                            def is_bot(m):
                                return m.author.bot
                            def is_text(m):
                                if 'http' in m.content.lower():
                                    return False
                                try:
                                    url = m.attachments[0].url
                                    return False
                                except:
                                    return True

                            if data[i][3] == 'bot':
                                await pChan.purge(limit=limit, before=beforeTime,
                                        check=is_bot)
                            elif data[i][3] == 'text':
                                await pChan.purge(limit=limit, before=beforeTime,
                                        check=is_text)
                            else:
                                await pChan.purge(limit=limit, before=beforeTime)
                        except:
                            pass
                        i+=1

                # Reset Weekly inactive channels
                sql = """ UPDATE channels
                          SET last_message = CURRENT_TIMESTAMP AT TIME ZONE 'ZULU'
                          WHERE guild_id = {0}
                          AND last_message <= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '1 week'
                          AND auto_purge = TRUE
                          AND is_deleted = FALSE """
                sql = sql.format(guild.id)

                junk1, junk2 = zb.sql_update(sql)

            except Exception as e:
                await zb.bot_errors(self,sp.format(e))

            # RSS Feeds
            try:
                sql = """ SELECT test_value, hook_url, embed_color,
                          avatar_url, parse_url, date_format
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

                        dateformat = data[i][5]
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
                                    response = requests.post(url, headers=headers, data=push)
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
                await zb.bot_errors(self,sp.format(e))

    except Exception as e:
        await zb.bot_errors(self,sp.format(e))


    # Keeps heartbeat stable
    dub = datetime.now()
    lubDub = (dub-lub).total_seconds()
    if int(lubDub) > 60:
        timeoff = 60
    else:
        timeoff = int(lubDub)

    return timeoff
