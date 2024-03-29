#!/usr/local/bin/python3.6
import re
import math
import asyncio
import discord
import async_timeout
from bs4 import BeautifulSoup
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
import stackprinter as sp
import psycopg2 as dbSQL
import numpy as np
from bin import zb_config



_var = zb_config
_query = """ SELECT g.guild_id,u.real_user_id,r.role_id,u.name,g.nick,u.int_user_id
             FROM users u
             LEFT JOIN guild_membership g ON u.int_user_id = g.int_user_id
             LEFT JOIN role_membership r ON u.int_user_id = r.int_user_id """


#################
##             ##
##   Classes   ##
##             ##
#################
class SqlData:
    """ Place holder for SqlData Class """
    i=0
    def j(self):
        return 'nothing'


#################
##             ##
##  Messages   ##
##             ##
#################
async def do_reminder(ctx):
    try:
        # Set Message
        message = ctx.message

        sql = """ SELECT * FROM reminders
                  WHERE guild_id = {0}
                  AND trigger_word = '{1}' """
        sql = sql.format(message.guild.id,message.content.lower())
        data, rows, string = sql_query(sql)
        data = data.flatten()

        # If Repeat is TRUE
        if data[5]:
            # If interval exists
            if int(data[4]) != 0:
                sql = """ UPDATE reminders
                          SET channel_id = {0}, real_user_id = {1}
                          WHERE guild_id = {2}
                          AND trigger_word = '{3}' """
                sql = sql.format(message.channel.id,message.author.id,
                        message.guild.id,message.content.lower())
                rows, string = sql_update(sql)
                futureTime = data[7] + timedelta(minutes=int(data[4]))

                diff = int(int((futureTime - datetime.utcnow()).seconds)/60) + 1
                msg = 'I\'ll remind you here in {0} minutes.'.format(diff)
                msg = await message.channel.send(msg,delete_after=_var.timeout)
            # If no interval
            else:
                #TODO: add 4th condition
                pass
        # If Repeat is FALSE
        else:
            sql = """ UPDATE reminders
                      SET channel_id = {0}, real_user_id = {1},
                      time = date_trunc('minute', timezone('ZULU', NOW())) +
                      INTERVAL '1 minute',
                      repeat = {4}
                      WHERE guild_id = {2}
                      AND trigger_word = '{3}' """
            # If interval exists
            if int(data[4]) != 0:
                repeat = 'TRUE'
                sql = sql.format(message.channel.id,message.author.id,
                        message.guild.id,message.content.lower(),repeat)
                rows, string = sql_update(sql)
                data[3] = data[3].replace('\\n','\n')

                msg = 'I\'ll remind you here in {0} minutes.'.format(data[4])
                msg = await message.channel.send(msg)
            # If no interval
            else:
                repeat = 'FALSE'
                sql = sql.format(message.channel.id,message.author.id,
                        message.guild.id,message.content.lower(),repeat)
                rows, string = sql_update(sql)
                data[3] = data[3].replace('\\n','\n')

                msg = await message.channel.send(data[3],delete_after=_var.timeout)
                await message.delete()
    except Exception as e:
        await bot_errors(ctx,sp.format(e))


#################
##             ##
##  Functions  ##
##             ##
#################
def how_wide(data):
    # Returns int length
    """ Finds longest element in array """

    # Ensures all are string type
    data = np.array(data)
    data = data.astype('str')
    longest = max(data, key=len)
    length = len(longest)

    return length

def pad_spaces(data):
    # Returns array lst
    """ Adds spaces for discord print """

    length = how_wide(data)
    spaces = ' '

    i = 0
    while i < length:
        print(f'looping {i} for pad spaces')
        spaces = spaces + ' '
        i+=1
    lst = [' {0}{1} '.format(x, spaces[0:length-len(x)]) for x in data]

    return lst

def add_numbers_list(data):
    data = np.array(data)
    lst = list(range(1,len(data)+1))
    lst = np.array(lst)

    data = np.insert(data, 0, lst, axis=1)

    return data

def add_blacklist(message,member_id,reason):
    sql = """ INSERT INTO blacklist(guild_id,real_user_id,whitelist,added_by,reason)
    VALUES ({0},{1},False,{2},'{3}') """
    sql = sql.format(message.guild.id,member_id,message.author.id,reason)

    rows, string = sql_update(sql)
    return

def add_special_role(values):
    sql = """ INSERT INTO special_roles (type,int_user_id,real_user_id,guild_id,role_id)
              VALUES {0} """
    sql = sql.format(values)

    rows, string = sql_update(sql)
    return

def rmv_special_role(guild_id,type_num,member_id):
    sql = """ DELETE FROM special_roles
              WHERE guild_id = {0}
              AND type = {1}
              AND real_user_id = {2} """
    sql = sql.format(guild_id,type_num,member_id)

    rows, string = sql_update(sql)
    return

async def fetch(session, url):
    # aiohttp fetch session
    async with async_timeout.timeout(10):
        async with session.get(url) as response:
            return await response.text()

async def soup_d(html, display_result=False):
    # async BeautifulSoup format
    soup = BeautifulSoup(html, 'html.parser')
    if display_result:
        print(soup.prettify())
    return soup

async def extract_text(html,content_area_class):
    # extract text from BeautifulSoup
    soup = await soup_d(html)
    content_area = soup.find("div", {"class": content_area_class})
    text = content_area.text
    return text

async def get_all_special_roles(ctx,member,low_group,high_group):
    # Gathers removed roles
    sql = """ SELECT role_id
              FROM special_roles
              WHERE guild_id = {0}
              AND type >= {1}
              AND type <= {2}
              AND real_user_id = {3} """
    sql = sql.format(ctx.guild.id,low_group,high_group,member.id)
    roles, rows, junk2 = sql_query(sql)
    if not rows > 0:
        await ctx.send(f'Something went wrong {ctx.author.mention}.\n' \
                f'**{member}** doesn\'t appear to be punished.',
                delete_after=15)
        await ctx.message.delete()
    return roles

async def store_all_special_roles(ctx,member,group_id):
    int_id = get_member_sql_int(member.id)
    string = '('
    rmv = []
    async with ctx.channel.typing():
        for role in member.roles:
            if role.name == '@everyone' or role.name == 'Nitro Booster':
                pass
            else:
                string += f'{group_id},{int_id},{member.id},{ctx.guild.id},{role.id}),('
                rmv.append(role)
        string = string[:-2]
        add_special_role(string)
    return rmv

def del_all_special_role(guild_id,member_id):
    sql = """ DELETE FROM special_roles
              WHERE guild_id = {0}
              AND real_user_id = {1} """
    sql = sql.format(guild_id,member_id)

    rows, string = sql_update(sql)
    return

def close_server(guild_id):
    sql = """ UPDATE guilds
              SET can_join = FALSE
              WHERE guild_id = {0} """
    sql = sql.format(guild_id)

    rows, string = sql_update(sql)
    return

def open_server(guild_id):
    sql = """ UPDATE guilds
              SET can_join = TRUE
              WHERE guild_id = {0} """
    sql = sql.format(guild_id)

    rows, string = sql_update(sql)
    return

async def remove_roles(self,member,role_ids,reason):
    try:
        lst = role_ids.flatten()
        roles = get_roles_obj(member.guild,lst)
        if reason != '':
            await member.remove_roles(*roles,reason=reason)
        else:
            await member.remove_roles(*roles)
        return
    except Exception as e:
        await bot_errors(self,sp.format(e))

async def add_roles(self,member,role_ids,reason):
    try:
        lst = role_ids.flatten()
        roles = get_roles_obj(member.guild,lst)
        if reason != '':
            await member.add_roles(*roles,reason=reason)
        else:
            await member.add_roles(*roles)
        return
    except Exception as e:
        await bot_errors(self,sp.format(e))

def grab_first_col(rows):
    data = np.array(rows)
    col = data[:,0]

    return col

async def give_trusted(guild,member):
    pass

async def give_admin(ctx,test):
    try:
        # data = get_roles_by_group_id(ctx.guild.id,90)
        roles = get_roles_by_name(ctx,'botadmin')
        if test == 'on':
            if len(roles) == 0:
                topRole = ctx.guild.get_member(ctx.bot.user.id).top_role
                perms = discord.Permissions(permissions=8)
                rolePos = topRole.position
                role = await ctx.guild.create_role(name='BotAdmin',
                        permissions=perms)
                await ctx.author.add_roles(role)
                await role.edit(position=rolePos)
            else:
                if len(roles) == 1:
                    role = grab_first_col(roles)[0]
                    await add_roles(ctx,ctx.author,role,'')
                else:
                    msg = await ctx.channel.send('Multiple `BotAdmin` found:',
                            delete_after=10)
        elif test == 'del':
            for role in roles:
                bad = ctx.guild.get_role(role[0])
                await bad.delete()
        else:
            if len(roles) == 1:
                role = grab_first_col(roles)[0]
                await remove_roles(ctx,ctx.author,role,'')
    except Exception as e:
        await bot_errors(ctx,sp.format(e))

def get_pattern(string, test):
    grab = re.search(test, string)

    return grab.group(0)

def get_role_ids(ctx):
    # Returns array idList
    """ Extracts role id from author """

    idList = []
    for role in ctx.author.roles:
        idList.append(role.id)

    return idList

def get_roles_obj(guild,lst):
    data = []
    i = 0
    while i < len(lst):
        print(f'looping {i} for get_roles')
        for role in guild.roles:
            if role.id == int(lst[i]):
                data.append(role)
        i+=1

    return data

def get_roles_by_group_id(guild_id,group_id):
    # 1 = join role
    # 2 = chat role
    # 3 = ideology role
    # 4 = assignable role
    # 10 = shitpost role
    # 11 = mute role
    # 12 = jail role
    # 50 = voice role
    # 51 = busy role
    # 80 = PunishLog
    # 81 = AdminLog
    # 90 = BotAdmin
    sql = """ SELECT role_id FROM roles
              WHERE guild_id = {0}
              AND group_id = {1} """
    sql = sql.format(guild_id,group_id)

    data, rows, string = sql_query(sql)
    return data

def get_roles_special(guild_id,group_id,member_id):
    sql = """ SELECT role_id
              FROM special_roles
              WHERE guild_id = {0}
              AND type = {1}
              AND real_user_id = {2} """
    sql = sql.format(guild_id,group_id,member_id)

    data, rows, junk1 = sql_query(sql)
    return data, rows

def get_roles_by_name(ctx, roleName):
    # Returns array roles
    """ Extracts role id and name from guild """

    roles = []
    for role in ctx.guild.roles:
        if roleName == role.name.lower():
            roles.append([role.id,role.name])

    return roles

def get_members_ids_new(ctx):
    """ Extracts sub list from list returns array """

    lst = [member.id for member in ctx.guild.members if not member.bot]
    data = np.asarray(lst)

    return data

def get_members_ids(ctx):
    # Returns array idList
    """ Extracts member id from guild """

    idList = []
    # [member.id for member in ctx.guild.members if not member.bot]
    for member in ctx.guild.members:
        if member.bot:
            pass
        else:
            idList.append(member.id)

    return idList

def get_member_id(ctx,msg):
    # Returns member id from name

    member_id = 0
    name = msg.lower()
    for member in ctx.guild.members:
        if member.name.lower().startswith(name):
            member_id = member.id
            return member_id
        try:
            if member.nick.lower().startswith(name):
                member_id = member.id
                return member_id
        except:
            pass

    return member_id

def get_member_sql_int(member_id):
    sql = """ SELECT int_user_id
              FROM users
              WHERE real_user_id = {0} """
    sql = sql.format(member_id)

    data, rows, string = sql_query(sql)

    return int(data[0][0])

def get_blacklist(member):
    sql = """ SELECT added_by, reason
              FROM blacklist
              WHERE guild_id = {0}
              AND whitelist = False
              AND real_user_id = {1} """
    sql = sql.format(str(member.guild.id),str(member.id))

    data, rows, string = sql_query(sql)

    return data, rows, string

def get_startswith(guild_id):
    sql = """ SELECT trigger_word
              FROM reminders
              WHERE guild_id = {0} """
    sql = sql.format(guild_id)

    data, rows, string = sql_query(sql)
    data = data.flatten()

    triggers = tuple(data)
    return triggers

def get_invite(guild_id):
    sql = """ SELECT invite_link
              FROM guilds
              WHERE guild_id = {0} """
    sql = sql.format(str(guild_id))

    data, rows, string = sql_query(sql)
    inviteLink = str(data[0][0])

    return inviteLink

def get_trusted_number(ctx, role_perms):
    """ test for valid data in database at two columns """

    sql = """ SELECT role_id
              FROM roles
              WHERE guild_id = {0}
              AND NOT role_perms = 0
              AND role_perms <= {1}
              AND role_id in {2} """
    sql = sql.format(ctx.guild.id,
                     role_perms,
                     sql_list(get_role_ids(ctx)))
    data, rows, string = sql_query(sql)

    if rows > 0:
        return True
    else:
        return False

def get_diff_role(more_roles,less_roles):
    data = []

    for role in more_roles:
        if not role in less_roles:
            data = role
            return data

def get_trusted_roles(ctx, role_perms):
    """ Extracts role ids that are trusted """

    sql = """ SELECT role_id
              FROM roles
              WHERE guild_id = {0}
              AND NOT role_perms = 0
              AND role_perms <= {1}
              AND role_id in {2} """
    sql = sql.format(ctx.guild.id,
                     role_perms,
                     sql_list(get_role_ids(ctx)))
    data, rows, string = sql_query(sql)

    return data

def get_member_with_role(ctx,roles):

    data = []
    roles = np.array(roles)
    found = False
    i = 0
    while i < len(roles):
        print(f'looping {i} for member with roles')
        for member in ctx.guild.members:
            for role in member.roles:
                if int(roles[i]) == role.id:
                    found = True
                    break
                else:
                    pass
            if found:
                data.append(member.id)
                found = False
        i+=1

    return data


#################
##             ##
## Punishments ##
##             ##
#################
def punish_user(member,number):
    sql = """ UPDATE guild_membership g
              SET punished = {2}
              FROM (SELECT int_user_id, real_user_id
              FROM users) AS u
              WHERE g.int_user_id = u.int_user_id
              AND g.guild_id = {0}
              AND u.real_user_id = {1} """
    sql = sql.format(member.guild.id,member.id,number)
    rows, string = sql_update(sql)

def get_punish_num(member):
    sql = """ SELECT g.punished
              FROM guild_membership g
              LEFT JOIN users u ON g.int_user_id = u.int_user_id
              WHERE g.guild_id = {0}
              AND u.real_user_id = {1}
              AND NOT g.punished = 0 """
    sql = sql.format(member.guild.id,member.id)

    data, rows, string = sql_query(sql)
    try:
        return int(data[0][0])
    except:
        return 0

def get_bot_help_counter(channel_id,group_id):
    # Returns number of messages
    sql = """ SELECT counter
              FROM channels
              WHERE channel_id = {0}
              AND group_id = {1}"""
    sql = sql.format(channel_id,group_id)
    data, rows, string = sql_query(sql)
    if rows > 0:
        return int(data[0][0])
    else:
        return -1

def increment_bot_help_counter(update,channel_id):
    # Increments number of messages
    update+=1
    sql = """ UPDATE channels
              SET counter = {0}
              WHERE channel_id = {1} """
    sql = sql.format(update,channel_id)
    rows, string = sql_update(sql)

def mention_spamming(member):
    # Get Hammer number
    sql = """ SELECT g.hammer
              FROM guild_membership g
              LEFT JOIN users u ON g.int_user_id = u.int_user_id
              WHERE g.is_member = TRUE
              AND g.guild_id = {0}
              AND u.real_user_id = {1} """
    sql = sql.format(member.guild.id,member.id)
    data, rows, string = sql_query(sql)
    # Count
    try:
        count = int(data[0]) + 1
    except:
        count = 1

    # Set hammer
    sql = """ UPDATE guild_membership g
              SET hammer = {2}
              FROM (SELECT int_user_id, real_user_id
              FROM users) AS u
              WHERE g.int_user_id = u.int_user_id
              AND g.guild_id = {0}
              AND u.real_user_id = {1} """
    sql = sql.format(member.guild.id,member.id,count)
    rows, string = sql_update(sql)

    # How many times?
    sql = """ SELECT g.hammer
              FROM guild_membership g
              LEFT JOIN users u ON g.int_user_id = u.int_user_id
              WHERE g.is_member = TRUE
              AND g.guild_id = {0}
              AND u.real_user_id = {1} """
    sql = sql.format(member.guild.id,member.id)
    data, rows, string = sql_query(sql)

    # Count
    try:
        count = int(data[0])
        return count
    except:
        return 0

def hammering(member):
    # Set hammer
    sql = """ UPDATE guild_membership g
              SET hammer = hammer + 1
              FROM (SELECT int_user_id, real_user_id
              FROM users) AS u
              WHERE g.int_user_id = u.int_user_id
              AND g.joined_at >= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '5 minutes'
              AND g.guild_id = {0}
              AND u.real_user_id = {1} """
    sql = sql.format(member.guild.id,member.id)
    rows, string = sql_update(sql)

    # How many times?
    sql = """ SELECT g.hammer
              FROM guild_membership g
              LEFT JOIN users u ON g.int_user_id = u.int_user_id
              WHERE g.joined_at >= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '5 minutes'
              AND g.guild_id = {0}
              AND u.real_user_id = {1} """
    sql = sql.format(member.guild.id,member.id)
    data, rows, string = sql_query(sql)

    # Count
    try:
        count = int(data[0])
        return count
    except:
        return 0

def reset_hammer(guild):
    # unbans users banned for hammering
    sql = """ SELECT g.hammer,u.real_user_id
              FROM guild_membership g
              LEFT JOIN users u ON g.int_user_id = u.int_user_id
              WHERE g.joined_at <= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '3 days'
              AND g.is_member = FALSE
              AND g.guild_id = {0}
              AND g.punished = 0
              AND g.hammer = 1 """
    sql = sql.format(guild.id)
    data, rows, string = sql_query(sql)

    # Member not hammering
    if rows > 0:
        print(f'would have unbanned {data[0][1]}')
        #TODO: unban
        #TODO: send @here to serverlog of unbanned
        pass

    # lowers hammer for non-members
    sql = """ UPDATE guild_membership g
              SET hammer = hammer - 1
              FROM (SELECT int_user_id, real_user_id
              FROM users) AS u
              WHERE g.int_user_id = u.int_user_id
              AND g.joined_at <= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '3 days'
              AND NOT g.hammer = 0
              AND g.is_member = FALSE
              AND g.guild_id = {0} """
    sql = sql.format(guild.id)
    rows, string = sql_update(sql)

    # lowers hammer for members
    sql = """ UPDATE guild_membership g
              SET hammer = hammer - 1
              FROM (SELECT int_user_id, real_user_id
              FROM users) AS u
              WHERE g.int_user_id = u.int_user_id
              AND g.is_member = TRUE
              AND NOT g.hammer = 0
              AND g.guild_id = {0} """
    sql = sql.format(guild.id)
    rows, string = sql_update(sql)


#################
##             ##
##    Bool     ##
##             ##
#################
def is_owner(ctx):
    if int(ctx.author.id) == int(_var.ownerID):
        return True
    else:
        return False

def is_trusted(ctx, role_perms):
    """ test for valid data in database at two columns """

    sql = """ SELECT role_id
              FROM roles
              WHERE guild_id = {0}
              AND NOT role_perms = 0
              AND role_perms <= {1}
              AND role_id in {2} """
    sql = sql.format(ctx.guild.id,
                     role_perms,
                     sql_list(get_role_ids(ctx)))
    data, rows, string = sql_query(sql)

    if rows > 0:
        return True
    else:
        return False

def is_raid(guild_id):
    sql = """ SELECT int_user_id from guild_membership
              WHERE joined_at >= CURRENT_TIMESTAMP AT TIME ZONE 'ZULU' - INTERVAL '5 minutes'
              AND is_member = TRUE
              AND guild_id = {0} """
    sql = sql.format(str(guild_id))

    data, rows, string = sql_query(sql)

    if rows >= _var.raidNumber:
        return True
    else:
        return False

def is_role_group(guild_id,group_id):
    sql = """ SELECT role_id FROM roles
              WHERE guild_id = {0}
              AND group_id = {1} """
    sql = sql.format(guild_id,group_id)

    data, rows, string = sql_query(sql)
    if rows > 0:
        return True
    else:
        return False

def is_closed(guild_id):
    sql = """ SELECT guild_id FROM guilds
              WHERE can_join = False
              AND guild_id = {0} """
    sql = sql.format(str(guild_id))

    data, rows, string = sql_query(sql)

    if rows > 0:
        return True
    else:
        return False

def is_logged(channel_id):
    log = True
    sql = """ SELECT ignore_logs
              FROM channels
              WHERE channel_id = {0}
              AND ignore_logs = TRUE """
    sql = sql.format(channel_id)

    data, rows, string = sql_query(sql)
    if rows > 0:
        log = False

    return log


async def is_good_nick(ctx,member):
    try:
        try:
            found = get_pattern(member.display_name,
                    '(([A-z]{2,})|([0-9]{2,}))\w+')
            return True
        except:
            if member.nick is None:
                nickName = member.name
            else:
                nickName = member.nick
            await member.edit(nick='Invalid Nickname')
            await member.send(f'**{nickName}** does not have enough ' \
                    f'ASCII characters.\n' \
                    f'Your nickname for **{member.guild.name}** is now set to ' \
                    f'*Invalid Nickname*.\n\n' \
                    f'To change your nickname visit this link:\n' \
                    f'https://support.discordapp.com/hc/en-us/articles/219070107-Server-Nicknames\n' \
                    f'If your server doesn\'t allow changing your nickname, please reach out to an admin.')
            return False
    except Exception as e:
        await bot_errors(ctx,sp.format(e))

def is_pattern(string, test):

    # If nothing to test
    if test == '':
        return False

    p = re.compile(test, re.IGNORECASE)
    if p.match(string) is None:
        return False
    else:
        return True

def is_hammer(guild_id):
    sql = """ SELECT u.real_user_id
              FROM guild_membership g
              LEFT JOIN users u ON g.int_user_id = u.int_user_id
              WHERE g.joined_at <= now() - INTERVAL '3 days'
              AND g.guild_id = {0}
              AND NOT g.hammer IS NULL """
    sql = sql.format(str(guild_id))

    data, rows, string = sql_query(sql)
    if rows > 0:
        return True
    else:
        return False


#################
##             ##
##     SQL     ##
##             ##
#################
def sql_list(data):
    string = '(' + ','.join(map(str, data)) + ')'
    return string

def sql_login():
    conn = dbSQL.connect(host = 'localhost',
                         database=_var.dbName,
                         user=_var.dbUser,
                         password=_var.dbPass)
    cur = conn.cursor()
    return conn, cur

def log_channel(member):
    sql = """ SELECT log_channel
              FROM guilds
              WHERE guild_id = {0} """
    sql = sql.format(str(member.guild.id))

    data, rows, string = sql_query(sql)

    return int(data[0])

def join_msg(member):
    sql = """ SELECT message
              FROM guilds
              WHERE guild_id = {0} """
    sql = sql.format(str(member.guild.id))

    data, rows, string = sql_query(sql)
    string = data[0][0]

    return string

def join_channel(member):
    sql = """ SELECT msg_channel_public
              FROM guilds
              WHERE guild_id = {0} """
    sql = sql.format(str(member.guild.id))

    data, rows, string = sql_query(sql)

    return int(data[0])

def welcome_channel(member):
    sql = """ SELECT welcome_channel
              FROM guilds
              WHERE guild_id = {0} """
    sql = sql.format(str(member.guild.id))

    data, rows, string = sql_query(sql)

    return int(data[0])

def sql_get_tbl_member_id(ctx,member_id):
    sql = """ {0}
              WHERE g.guild_id = {1}
              AND u.real_user_id = {2}
              ORDER BY u.real_user_id DESC """
    sql = sql.format(_query,ctx.guild.id,member_id)

    data, rows, string = sql_query(sql)

    return data

def sql_all_guild_id(guild_id):
    sql = """ {0}
              WHERE g.guild_id = {1}
              ORDER BY u.real_user_id DESC """
    sql = sql.format(_query,str(guild_id))

    data, rows, string = sql_query(sql)

    return data

def sql_all_member_id(member_id):
    sql = """ {0}
              WHERE u.real_user_id = {1}
              ORDER BY g.guild_id DESC """
    sql = sql.format(_query,str(member_id))

    data, rows, string = sql_query(sql)

    return data

def sql_all_role_id(role_id):
    sql = """ {0}
              WHERE r.role_id = {1}
              ORDER BY u.real_user_id DESC """
    sql = sql.format(_query,str(role_id))

    data, rows, string = sql_query(sql)

    return data

def sql_query(sql):
    """ Returns data from query """

    string = ''
    try:
        conn = None
        rows = 0
        try:
            # connect to the PostgreSQL database and create cursor
            conn, cur = sql_login()
            # execute the UPDATE  statement
            cur.execute(sql)
            # get the number of updated rows
            rows = cur.rowcount
            # fetch data from query
            data = cur.fetchall()[:][:]
            data = np.array(data)
            # Close communication with the PostgreSQL database
            cur.close()
        except (Exception, dbSQL.DatabaseError) as e:
            string = sp.format(e)
        finally:
            if conn is not None:
                conn.close()

    except Exception as e:
        string = sp.format(e)

    return data, rows, string

def sql_update(sql):
    """ Updates data in table """

    string = ''
    try:
        conn = None
        rows = 0
        try:
            # connect to the PostgreSQL database and create cursor
            conn, cur = sql_login()
            # execute the UPDATE  statement
            cur.execute(sql)
            # get the number of updated rows
            rows = cur.rowcount
            # Commit the changes to database
            conn.commit()
            # Close communication with the PostgreSQL database
            cur.close()
        except (Exception, dbSQL.DatabaseError) as e:
            string = sp.format(e)
        finally:
            if conn is not None:
                conn.close()

    except Exception as e:
        string = sp.format(e)

    return rows, string

def reset_voice_updating(guild):
    # In event Discord fails, reset
    sql = """ UPDATE guild_membership
              SET voice_updating = FALSE
              AND guild_id = {0} """
    sql = sql.format(guild.id)
    rows, string = sql_update(sql)


#################
##             ##
##  Printers   ##
##             ##
#################
async def print_log(ctx,member,embed):
    try:
        channel = ctx.bot.get_channel(log_channel(member))
        embed.set_footer(text="ID: " + str(member.id))
        embed.timestamp = datetime.utcnow()
        await channel.send(embed=embed)
    except Exception as e:
        await bot_errors(ctx,sp.format(e))

async def print_log_by_group_id(guild,group_id,embed):
    try:
        # If no punish chan, skip log
        sql = """ SELECT channel_id
                  FROM channels
                  WHERE guild_id = {0}
                  AND group_id = {1} """
        sql = sql.format(guild.id,group_id)

        chan, rows, junk2 = sql_query(sql)
        if rows != 0:
            printchan = guild.get_channel(int(chan[0][0]))
            await printchan.send(embed=embed)
    except Exception as e:
        await bot_errors(ctx,sp.format(e))

async def print_embed_ts(ctx,member,embed):
    try:
        embed.set_footer(text="ID: " + str(member.id))
        embed.timestamp = datetime.utcnow()
        await ctx.channel.send(embed=embed)
    except Exception as e:
        await bot_errors(ctx,sp.format(e))

async def bot_errors(ctx,e):
    """ Or bot_errors(self,sp.format(e)) """
    # await zb.bot_errors(ctx,sp.format(e))
    try:
        """ Send Bot Errors to log """
        sections = e.split('zzz')
        print(sections)

        i = 0
        embeds = []
        while i < len(sections):
            store = False
            if len(sections[i]) < 5:
                pass
            elif '__**`ERROR:`**__' in sections[i]:
                title = sections[i]
                title = (title[:253] + '...') if len(title) > 256 else title
            elif 'python\n' in sections[i]:
                if i != 1:
                    embeds.append(embed)
                code = sections[i]
                code = (code[:2039] + '...') if len(code) > 2042 else code
                embed=discord.Embed(title=f'{title}',
                        description=f'```{code}```', color=0xf5d28a)
            elif '........' in sections[i]:
                items = sections[i]
                items = (items[:1015] + '...') if len(items) > 1018 else items
                embed.add_field(name=f'Vars',value=f'```{items}```')
            else:
                tail = f'{sections[i]}'
                tail = (tail[:1015] + '...') if len(tail) > 1018 else tail
                embed.add_field(name=f'Error:',value=f'`{tail}`')
                embed.timestamp = datetime.utcnow()
                store = True

            if store:
                embeds.append(embed)

            # increment loop
            i+=1

        #strings = await split_text(e, 2000, " ")
        channel = ctx.bot.get_channel(_var.botErrors)
        for embed in embeds:
            await channel.send(embed=embed)
    except Exception as e:
        print(f'{e}')

async def print_string(ctx,string):
    try:
        string = print_2000lim(string)

        i = 0
        if len(string[0]) == 1:
            await ctx.send(string)
        else:
            while i < len(string):
                print(f'looping {i} for print string')
                await ctx.send(string[i])
                i+=1
    except Exception as e:
        await bot_errors(ctx,sp.format(e))

def nav_large_message(maxInt,curInt,nav):
    if nav == 0:
        return 0
    elif nav == 1 and (curInt - 5) > 0:
        return curInt - 5
    elif nav == 2 and (curInt - 1) > 0:
        return curInt - 1
    elif nav < 3:
        return 0
    elif nav == 3 and (curInt + 1) < maxInt:
        return curInt + 1
    elif nav == 4 and (curInt + 5) < maxInt:
        return curInt + 5
    else:
        return maxInt

def nav_med_message(maxInt,curInt,nav):
    if nav == 0 and (curInt - 5) > 0:
        return curInt - 5
    elif nav == 1 and (curInt - 1) > 0:
        return curInt - 1
    elif nav == 2 and (curInt + 1) < maxInt:
        return curInt + 1
    elif nav == 3 and (curInt + 5) < maxInt:
        return curInt + 5
    elif nav <= 1:
        return 0
    else:
        return maxInt

def nav_small_message(maxInt,curInt,nav):
    if nav == 0 and (curInt - 1) > 0:
        return curInt - 1
    elif nav == 1 and (curInt + 1) < maxInt:
        return curInt + 1
    elif nav == 0:
        return 0
    else:
        return maxInt

async def build_embed_print(self,ctx,lst,title):
    """ Builds list of embeds limited to 20 rows """
    try:
        pages = int(math.ceil((len(lst))/20))
        embeds = []
        strings = []
        i = 1
        limit = 20
        string = f'{lst[0]}'
        if pages > 1:
            while i < len(lst):
                while i < limit and i < len(lst):
                    string = f'{string}\n{lst[i]}'

                    # increment loop
                    i+=1
                try:
                    tempString = f'{lst[i]}'
                    strings.append(string)
                    string = tempString
                except:
                    pass
                limit+=20
                i+=1
        else:
            while i < len(lst):
                string = f'{string}\n{lst[i]}'

                # increment loop
                i+=1
        strings.append(string)

        i = 0
        while i < pages:
            embed=discord.Embed(color=0xf5d28a)
            embed.add_field(name=f'{title}',value=f'{strings[i]}')
            embeds.append(embed)
            # Increment loop
            i+=1

        return pages, embeds

    except Exception as e:
        await bot_errors(ctx,sp.format(e))

async def print_embed_nav(self,ctx,initialEmbed,embedList,
        maxInt,initialIndex,footer):
    count = initialIndex - 1
    maxInt = maxInt - 1
    if footer == '':
        initialEmbed.set_footer(text=f'{count+1} of {maxInt+1} | ID: {ctx.author.id}')
        initialEmbed.timestamp = datetime.utcnow()
    msg = await ctx.send(embed=initialEmbed)

    if maxInt > 9:
        ids = ['\U000023EE','\U000023EA','\U000025C0',
                '\U000025B6','\U000023E9','\U000023ED']
    elif maxInt > 4:
        ids = ['\U000023EA','\U000025C0','\U000025B6','\U000023E9']
    else:
        ids = ['\U000025C0','\U000025B6']

    def r_check(reaction, user):
        return (reaction.message.id == msg.id and user == ctx.author and
                reaction.message.channel == ctx.message.channel and
                str(reaction) in ids)

    async with ctx.channel.typing():
        if maxInt > 0:
            for id in ids:
                try:
                    await msg.add_reaction(emoji=id)
                except:
                    await ctx.send(f'I could not find emoji.id = {id}',
                            delete_after=5)

    while True:
        print(f'looping true for reaction add or remove')
        done, pending = await asyncio.wait([
                            self.bot.wait_for('reaction_add', check=r_check),
                            self.bot.wait_for('reaction_remove', check=r_check)
                        ], timeout = 30, return_when=asyncio.FIRST_COMPLETED)

        try:
            stuff = done.pop().result()
        except Exception as e:
            break

        try:
            try:
                emoji_id = int(get_pattern(str(stuff), '(?<=Emoji\sid=)((\w+)(?=\s))'))
            except:
                emoji_id = get_pattern(str(stuff), "(?<=emoji=')((.{1})(?='\s))")
            nav = ids.index(emoji_id)
            if maxInt > 9:
                count = nav_large_message(maxInt,count,nav)
            elif maxInt > 4:
                count = nav_med_message(maxInt,count,nav)
            else:
                count = nav_small_message(maxInt,count,nav)
            embed = embedList[count]
            if footer == '':
                embed.set_footer(text=f'{count+1} of {maxInt+1} | ID: {ctx.author.id}')
                embed.timestamp = datetime.utcnow()
            await msg.edit(embed=embed)
        except Exception as e:
            await bot_errors(ctx,sp.format(e))
    try:
        for future in pending:
            future.cancel()
    except Exception as e:
        await bot_errors(ctx,sp.format(e))
    await msg.clear_reactions()

    return msg

async def print_embed_choice(self,ctx,embedMsg,lowChoice,maxChoices,footer):
    lowChoice-=1
    if footer == '':
        embedMsg.set_footer(text=f'ID: {ctx.author.id}')
        embedMsg.timestamp = datetime.utcnow()
    else:
        embedMsg.timestamp = datetime.utcnow()
    msg = await ctx.send(embed=embedMsg)

    # Reactions
    ids = ['1\N{combining enclosing keycap}',
            '2\N{combining enclosing keycap}',
            '3\N{combining enclosing keycap}',
            '4\N{combining enclosing keycap}',
            '5\N{combining enclosing keycap}',
            '6\N{combining enclosing keycap}',
            '7\N{combining enclosing keycap}',
            '8\N{combining enclosing keycap}',
            '9\N{combining enclosing keycap}',
            '0\N{combining enclosing keycap}']

    # Check reaction

    # Check reaction
    def r_check(reaction, user):
        return (reaction.message.id == msg.id and user == ctx.author and
                reaction.message.channel == ctx.message.channel and
                str(reaction) in ids)

    async with ctx.channel.typing():
        # Add reactions
        i = lowChoice
        while i < maxChoices:
            try:
                await msg.add_reaction(emoji=ids[i])
            except:
                await ctx.send(f'I could not find emoji.id = {ids[i]}',
                        delete_after=5)
            # increment loop
            i+=1
    while True:
        print(f'looping true for reaction add or remove')
        done, pending = await asyncio.wait([
                            self.bot.wait_for('reaction_add', check=r_check),
                            self.bot.wait_for('reaction_remove', check=r_check)
                        ], timeout = 10, return_when=asyncio.FIRST_COMPLETED)

        try:
            stuff = done.pop().result()
        except Exception as e:
            break

        try:
            emoji_id = get_pattern(str(stuff), "(?<=emoji=')((.{2})(?='\s))")
            selected = int(ids.index(emoji_id))
            break
        except Exception as e:
            selected = -1

    try:
        for future in pending:
            future.cancel()
    except Exception as e:
        await bot_errors(ctx,sp.format(e))
    await msg.clear_reactions()

    return msg, selected

async def split_text(text, limit, separate):
    words = text.split()
    if max(map(len, words)) > limit:
        raise ValueError("limit is too small")
    strings, part, others = [], words[0], words[1:]
    for word in others:
        if len(separate) + len(word) > limit-len(part):
            strings.append(part)
            part = word
        else:
            part += separate + word
    if part:
        strings.append(part)
    return strings

def print_2000lim(string):
    try:
        if len(string) < 2000:
            return string

        # Gather numbers from data
        build = string.split('\n')
        length = len(build[2])
        rows = math.floor(1800/length)
        allRows = math.ceil(len(string)/length)
        msgs = math.ceil(len(build)/rows)
        string = ['' for x in range(msgs)]

        # Rebuild for multimessages
        string[0] = build[0] + '\n' + build[1] + '\n'
        i = 2
        j = 0
        while j < msgs:
            print(f'looping {j} for print limit')
            while i < rows:
                print(f'looping {i} for print limit build')
                string[j] = string[j] + build[i] + '\n'
                i+=1
            rows += rows
            if rows > allRows:
                rows = allRows
            if j+1 < msgs:
                string[j] = string[j] + '```'
            j+=1
            if j < msgs:
                string[j] = (string[j] + '```' + '\n')
        string[j-1] = string[j-1] + build[2] + '```'
        return string

    except Exception as e:
        string = sp.format(e)
        return string

async def print_select(ctx,data2):
    """ Used to build selection for users """

    try:
        data = add_numbers_list(data2)
        title = '**`CHOOSE A NUMBER TO CHANGE`**'
        await print_lookup(ctx,len(data),data,title,'')

        def check(m):
            try:
                test = int(m.content)
                return (0 < test <= len(data) and
                        m.channel == ctx.channel and
                        m.author == ctx.author)
            except:
                return False

        try:
            msg = await ctx.bot.wait_for('message',
                                          timeout=10.0,
                                          check=check)
            choice = int(msg.content)-1
        except Exception as e:
            await ctx.send('**Invalid choice.** Select a listed number next time.')
            choice = -1
            return choice

        return choice
    except Exception as e:
        await bot_errors(ctx,sp.format(e))

async def print_lookup(ctx,rows,data,title,string):
    try:
        # Return if error
        if string != '':
            await print_string(ctx,string)
            return

        # Build a title bar
        maxTitle = len(title)
        bar = '---==='
        i = 0
        while i < maxTitle:
            print(f'looping {i} for print lookup')
            bar = bar + '='
            i+=1
        top = bar + '===---'

        # If no data, print empty list
        if rows == 0:
            string = ('```\n      ' + title + '\n' + top + '\n' +
                      '   Empty list```')
            await print_string(ctx,string)
            return

        # Initializes dynamic array
        maxRows = range(rows)
        maxEle = range(len(data[0]))
        matrix_np = np.array(data)
        matrix_np = matrix_np.astype('str')
        matrix = matrix_np.transpose()

        # Calculates table width
        lenTotal = -10
        for x in maxEle:
            matrix[x-1][:] = pad_spaces(matrix[x-1][:])
            lenTotal = lenTotal + len(matrix[x-1][0]) + 2

        # Checks to see if title or data is wider
        test = lenTotal - maxTitle
        if lenTotal > maxTitle:
            i = 0
            while i < test:
                print(f'looping {i} for some test')
                bar = bar + '='
                i+=1
            bar = bar + '===---'
        else:
            bar = top

        string = '```\n      ' + title + '\n' + bar + '\n'
        i = 0
        while i < rows:
            print(f'looping {i} for rows of test')
            string = string + '||'
            j = 0
            while j < len(data[0]):
                print(f'looping {j} for j of test')
                string = string + matrix[j][i]
                if j+1 != len(data[0]) and test < 0:
                    string = string + '||'
                else:
                    k = test
                    while k < 0:
                        print(f'looping {k} for k of test')
                        string = string + ' '
                        k+=1
                    string = string + '||'
                j+=1
            i+=1
            string = string + '\n'
        string = string + bar + '\n'
        string = string + '```'

        await print_string(ctx,string)
        return
    except Exception as e:
        await bot_errors(ctx,sp.format(e))
