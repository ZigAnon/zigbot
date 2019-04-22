#!/usr/local/bin/python3.6
import discord
from discord.ext import commands
from bin import zb_config

_var = zb_config

async def _heartbeat(bot):
    timeoff = 0
    try:
        print('working')
        #TODO: autoPurge needs to be added
        # grab channels to purge, msg limit, time, checks bot/text
    except Exception as e:
        print(f'**`ERROR:`** {type(e).__name__} - {e}')

    return timeoff
