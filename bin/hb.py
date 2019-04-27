#!/usr/local/bin/python3.6
import discord
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
from bin import zb_config

_var = zb_config

async def _heartbeat(bot):
    timeoff = 0
    count = 0
    try:
        print('working')
        curTime = datetime.now()
        guilds = list(bot.guilds)
        pinged = [0] * len(guilds)

        #TODO: autoPurge needs to be added
        # grab channels to purge, msg limit, time, checks bot/text

        for x in range(len(guilds)):
            #TODO: SQL check for bump
            try:
                #TODO: if bump found get last bump time
                # found = 1
                found = 0
            except:
                found = 0

            # If server has time
            if found:
                pass
                # Member Count
                #TODO: count all members
                # update count
                # count = humans
                # game = "with {0} humans".format(count)
                # await bot.change_presence(activity=discord.Game(name=game, type=1))

                # Checks for ping
                if pinged[x-1] == 0:
                    pass
                    # lastBump = datetime.strptime(oldTime, _var.dateFormat)
                    # c = open(filePath + '.channel')
                    # cStrip = c.readlines()
                    # bumChan = cStrip[0].rstrip()
                    # c.close()
                    # channel = discord.Object(id=bumChan)

                    # # Check Time
                    # if lastBump < curTime:
                    #     pinged[x-1] = 1
                    #     lastBump += timedelta(hours=1)

                    #     # Ping all Admins
                    #     if lastBump < curTime:
                    #         await bot.send_message(channel, '@here, helps us grow: ' + '\n Please `!disboard bump` again!')

                    #     # Ping member only
                    #     else:
                    #         m = open(filePath + '.member')
                    #         mStrip = m.readlines()
                    #         bumMemb = mStrip[0].rstrip()
                    #         m.close()
                    #         pMemb = '<@' + bumMemb + '>'
                    #         await bot.send_message(channel, '%s Friendly reminder to `!disboard bump` again!' % pMemb)

                # Has it been an hour since last ping?
                else:
                    pass
                    # try:
                    #     l = open(filePath + '.lping')
                    #     lStrip = l.readlines()
                    #     lPing = lStrip[0].rstrip()
                    #     lastPing = datetime.strptime(lPing, dateFormat) + timedelta(hours=1) - timedelta(minutes=2)
                    # except:
                    #     l = open(filePath + '.lping', 'w+')
                    #     l.write("%s\r\n" % (curTime))
                    #     lastPing = curTime + timedelta(hours=1) - timedelta(minutes=2)
                    # l.close()

                    # # Resets ping timer
                    # if lastPing < curTime:
                    #     pinged[x-1] = 0
                    #     os.remove(filePath + '.lping')
    except Exception as e:
        print(f'**`ERROR:`** {type(e).__name__} - {e}')

    return timeoff