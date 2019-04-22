#!/usr/local/bin/python3.6
import re
import math
import discord
import numpy as np
import psycopg2 as dbSQL
from discord.ext import commands
from bin import zb_config

_var = zb_config


#################
##             ##
##  Functions  ##
##             ##
#################
def how_wide(data):
    longest = max(data, key=len)
    length = len(longest)
    return length

def pad_spaces(data):
    length = how_wide(data)
    spaces = ' '

    i = 0
    while i < length:
        spaces = spaces + ' '
        i+=1
    lst = [' {0}{1} '.format(x, spaces[0:length-len(x)]) for x in data]
    return lst

def get_roles_by_name(ctx, roleName):
    roles = []
    for role in ctx.guild.roles:
        if roleName == role.name.lower():
            roles.append([role.id,role.name])

    return roles

def get_members_ids(ctx):
    idList = []
    for member in ctx.guild.members:
        if member.bot:
            pass
        else:
            idList.append(member.id)

    return idList



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

def pattern(ctx, test):
    p = re.compile(test, re.IGNORECASE)
    if p.match(ctx.message.content.lower()) is None:
        return False
    else:
        return True

def has_permission(ctx, role_perms):
    """ test for valid data in database at two columns """

    sql = """ SELECT role_id
              FROM roles
              WHERE guild_id = %s
              AND NOT role_perms = 0
              AND role_perms <= %s """
    conn = None
    updated_rows = 0
    try:
        # connect to the PostgreSQL database and create cursor
        conn, cur = sql_login()
        # execute the UPDATE  statement
        cur.execute(sql, (ctx.guild.id, role_perms))
        # get the number of updated rows
        updated_rows = cur.rowcount
        # Close communication with the PostgreSQL database
        cur.close()
    except (Exception, dbSQL.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    if updated_rows > 0:
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
            data = cur.fetchall()
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
async def print_string(ctx,string):
    string = print_2000lim(string)

    i = 0
    if len(string[0]) == 1:
        await ctx.send(string)
    else:
        print(len(string))
        while i < len(string):
            await ctx.send(string[i])
            i+=1

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
            string[j] = string[j] + '```'
            j+=1
            if j < msgs:
                string[j] = string[j] + build[allRows] + '```'
        return string

    except Exception as e:
        string = (f'**`ERROR:`** {type(e).__name__} - {e}')
        return string

def print_select(ctx, list_id, list_name, path):
    """ Used to build output for users """

    choice = '```'

    if path == 0:
        for x in range(len(list_id)):
            choice = (choice + str(x+1) + '.  Object ID = ' + str(list_id[x]) +
                      ' -- Name = ' + list_name[x] + '\n')

    choice = choice + '```'

    return choice

async def print_lookup(ctx,rows,data,title,string):
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

    if rows == 0:
        string = ('```\n      ' + title + '\n' + top + '\n' +
                  '   Empty list```')
        await print_string(ctx,string)
        return

    maxRows = range(rows)
    maxEle = range(len(data[0]))
    matrix = [[0 for x in maxRows] for y in maxEle]

    for x in maxEle:
        for y in maxRows:
            matrix[x-1][y-1] = str(data[y-1][x-1])

    lenTotal = -10
    for x in maxEle:
        matrix[x-1][:] = pad_spaces(matrix[x-1][:])
        lenTotal = lenTotal + len(matrix[x-1][0]) + 2

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
    for x in maxRows:
        string = string + '||'
        for y in maxEle:
            string = string + matrix[y-1][x-1]
            if y+1 != len(data[0]) and test < 0:
                string = string + '||'
            else:
                i = test
                while i < 0:
                    string = string + ' '
                    i+=1
                string = string + '||'
        string = string + '\n'
    string = string + bar + '\n'
    string = string + '```'

    await print_string(ctx,string)
    return
