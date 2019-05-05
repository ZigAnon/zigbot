import discord
from discord.ext import commands
from bin import zb
from bin import zb_config

_var = zb_config


class PunishCog(commands.Cog):
    """ Punish members """

    def __init__(self, bot):
        self.bot = bot

    # Hidden means it won't show up on the default help.
    @commands.command(name='raid', hidden=True)
    async def raid_control(self, ctx):
        """Command to show inactive members"""
        try:
            if zb.is_trusted(ctx,3):
                data = [['Open Server', 'Lets members join'], 
                        ['Close Server', 'Auto kicks members who join  ']]
                choice = await zb.print_select(ctx,data)

                sql = """ UPDATE guilds
                          SET can_join = {0}
                          WHERE guild_id = {1} """
            # Open Server
            if choice == 0:
                sql = sql.format('NULL',ctx.guild.id)
                await ctx.send('__**`RAID OFF:`**__ Server is open to public!')
            if choice == 1:
                sql = sql.format('FALSE',ctx.guild.id)
                await ctx.send('__**`RAID ON:`**__ All invite links are disabled!')
            rows, string = zb.sql_update(sql)
        except Exception as e:
            await ctx.send(f'**`ERROR:`** {type(e).__name__} - {e}')
            await zb.bot_errors(ctx,e)


def setup(bot):
    bot.add_cog(PunishCog(bot))
