import discord
import asyncio
from datetime import datetime as date
from discord.ext import commands
from bin import zb_config
from bin import hb

import sys, traceback, os

# Setup bot prefixes
def get_prefix(bot, message):
    """A callable Prefix for our bot. This could be edited to allow per server prefixes."""

    # Notice how you can use spaces in prefixes. Try to keep them simple though.
    prefixes = ['. ', '.']

    # Check to see if we are outside of a guild. e.g DM's etc.
    if not message.guild:
        # Only allow ? to be used in DMs
        return '?'

    # If we are in a guild, we allow for the user to mention us or use any of the prefixes in our list.
    return commands.when_mentioned_or(*prefixes)(bot, message)

_var = zb_config
bot = commands.Bot(command_prefix=get_prefix, case_insensitive=True)
bot.remove_command('help')

# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import
initial_extensions = ['cogs.guild.cnp',
                      'cogs.guild.cbt',
                      'cogs.admin.serverinfo',
                      'cogs.admin.inactive',
                      'cogs.admin.lookup',
                      'cogs.admin.owner',
                      'cogs.admin.punish',
                      'cogs.help.setup',
                      'cogs.help.help',
                      'cogs.utility.dict',
                      'cogs.utility.members',
                      'event.onmemberban',
                      'event.onmemberjoin',
                      'event.onmemberremove',
                      'event.onmemberunban',
                      'event.onmemberupdate',
                      'event.onmessage',
                      'event.onmessageedit',
                      'event.onmessagedelete',
                      'event.onvoicestateupdate']

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

# Main loop adds a heartbeat to the bot for automated tasks
async def main_loop():
    await bot.wait_until_ready()
    while not bot.is_closed():
        beat = 60 - await hb._heartbeat(bot)
        print(f'{date.now()} - Heartbeat is {beat} seconds')
        await asyncio.sleep(beat)

# Ping tests to see if the bot is active independent from cogs
@bot.command()
async def ping(ctx):
    await ctx.send('pong')

@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')

    # Changes our bots Playing Status. type=1(streaming) for a standard game you could remove type and url.
    await bot.change_presence(activity=discord.Game(name='with Trump', type=1))
    print(f'Successfully logged in and booted...!')

bot.loop.create_task(main_loop())
bot.run(_var.TOKEN, bot=True, reconnect=True)
