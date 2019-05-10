#!/usr/local/bin/python3.6
import re
import math
import asyncio
import discord
from discord.ext import commands
from datetime import datetime
from datetime import timedelta
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
                msg = await message.channel.send(msg)
                await asyncio.sleep(_var.timeout)
                await msg.delete()
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

                msg = await message.channel.send(data[3])
                await message.delete()
            await asyncio.sleep(_var.timeout)
            await msg.delete()
    except Exception as e:
        await bot_errors(ctx,e)


#################
##             ##
##  Functions  ##
##             ##
#################
async def timed_msg(channel,string,seconds):
    try:
        string = string.replace('\\n','\n')
        msg = await channel.send(string)
        await asyncio.sleep(seconds)
        await msg.delete()
    except Exception as e:
        print(f'**`ERROR:`** {type(e).__name__} - {e}')

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

def close_server(guild_id):
    sql = """ UPDATE guilds
              SET can_join = FALSE
              WHERE guild_id = {0} """
    sql = sql.format(guild_id)

    rows, string = sql_update(sql)
    return

def open_server(guild_id):
    sql = """ UPDATE guilds
              SET can_join = NULL
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
        await bot_errors(self,e)

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
        await bot_errors(self,e)

def grab_first_col(rows):
    data = np.array(rows)
    col = data[:,0]

    return col

async def give_admin(ctx,test):
    try:
        # data = get_roles_special(ctx.guild.id,90)
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
                    msg = await ctx.channel.send('Multiple `BotAdmin` found:')
                    await asyncio.sleep(10)
                    await msg.delete()
        elif test == 'del':
            for role in roles:
                bad = ctx.guild.get_role(role[0])
                await bad.delete()
        else:
            if len(roles) == 1:
                role = grab_first_col(roles)[0]
                await remove_roles(ctx,ctx.author,role,'')
    except Exception as e:
        await bot_errors(ctx,e)

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
        for role in guild.roles:
            if role.id == int(lst[i]):
                data.append(role)
        i+=1

    return data

def get_roles_special(guild_id,group_id):
    # 1 = join role
    # 2 = chat role
    # 3 = ideology role
    # 10 = shitpost role
    # 11 = mute role
    # 12 = jail role
    # 90 = BotAdmin
    sql = """ SELECT role_id FROM roles
              WHERE guild_id = {0}
              AND group_id = {1} """
    sql = sql.format(guild_id,group_id)

    data, rows, string = sql_query(sql)
    return data

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
def get_punish_num(member):
    sql = """ SELECT g.punished
              FROM guild_membership g
              LEFT JOIN users u ON g.int_user_id = u.int_user_id
              WHERE g.guild_id = {0}
              AND u.real_user_id = {1}
              AND NOT g.punished IS NULL """
    sql = sql.format(member.guild.id,member.id)

    data, rows, string = sql_query(sql)
    return int(data[0][0])

def mention_spamming(member):
    # Set hammer
    sql = """ UPDATE guild_membership g
              SET hammer = hammer + 1
              FROM (SELECT int_user_id, real_user_id
              FROM users) AS u
              WHERE g.int_user_id = u.int_user_id
              AND g.guild_id = {0}
              AND u.real_user_id = {1} """
    sql = sql.format(member.guild.id,member.id)
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

async def toggle_updating(ctx, sqlTbl, sqlCol, guild_id, member_id):
    """ Toggle updating """

    if is_updating(ctx, sqlTbl, sqlCol, guild_id, member_id):
        toggle = 'FALSE'
    else:
        toggle = 'TRUE'

    int_id = get_member_sql_int(member_id)

    sql = """ UPDATE {0}
              SET {1} = {2}
              WHERE guild_id = {3}
              AND int_user_id = {4}"""
    sql = sql.format(sqlTbl,sqlCol,toggle,guild_id,int_id)

    rows, string = sql_update(sql)
    return


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

def is_updating(ctx, sqlTbl, sqlCol, guild_id, member_id):
    """ Updateing check """

    int_id = get_member_sql_int(member_id)

    sql = """ SELECT {0}
              FROM {1}
              WHERE guild_id = {2}
              AND int_user_id = {3}
              AND {0} = TRUE """
    sql = sql.format(sqlCol,sqlTbl,guild_id,int_id)
    data, rows, string = sql_query(sql)

    if rows > 0:
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

async def is_good_nick(ctx,member):
    try:
        try:
            found = get_pattern(member.display_name,
                    '(([A-z]{2,})|([0-9]{2,}))\w+')
            return True
        except:
            await member.edit(nick='Invalid Nickname')
            return False
    except Exception as e:
        await bot_errors(ctx,e)

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
            string = (f'**`ERROR:`** {type(e).__name__} - {e}')
        finally:
            if conn is not None:
                conn.close()

    except Exception as e:
        string = (f'**`ERROR:`** {type(e).__name__} - {e}')

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
            string = (f'**`ERROR:`** {type(e).__name__} - {e}')
        finally:
            if conn is not None:
                conn.close()

    except Exception as e:
        string = (f'**`ERROR:`** {type(e).__name__} - {e}')

    return rows, string


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
        await bot_errors(ctx,e)

async def bot_errors(ctx,e):
    """ Or bot_errors(self,e) """
    try:
        """ Send Bot Errors to log """
        string = (f'**`ERROR:`** {type(e).__name__} - {e}')

        channel = ctx.bot.get_channel(_var.botErrors)
        await channel.send(string)
    except Exception as e:
        print(f'**`ERROR:`** {type(e).__name__} - {e}')

async def print_string(ctx,string):
    try:
        string = print_2000lim(string)

        i = 0
        if len(string[0]) == 1:
            await ctx.send(string)
        else:
            while i < len(string):
                await ctx.send(string[i])
                i+=1
    except Exception as e:
        await bot_errors(ctx,e)


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
            while i < rows:
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
        string = (f'**`ERROR:`** {type(e).__name__} - {e}')
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
        await bot_errors(ctx,e)

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
                bar = bar + '='
                i+=1
            bar = bar + '===---'
        else:
            bar = top

        string = '```\n      ' + title + '\n' + bar + '\n'
        i = 0
        while i < rows:
            string = string + '||'
            j = 0
            while j < len(data[0]):
                string = string + matrix[j][i]
                if j+1 != len(data[0]) and test < 0:
                    string = string + '||'
                else:
                    k = test
                    while k < 0:
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
        await bot_errors(ctx,e)
