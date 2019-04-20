#!/usr/local/bin/python3.6
import re
import psycopg2 as dbSQL
from bin import zb_config

_var = zb_config


#################
##             ##
##  Functions  ##
##             ##
#################
def error(e):
    error = ('__**`Error:`**__\n```' +
             str(e) + '```')
    return error

def sql_login():
    conn = dbSQL.connect(host = 'localhost',
                         database=_var.dbName,
                         user=_var.dbUser,
                         password=_var.dbPass)
    cur = conn.cursor()
    return conn, cur

def get_role_id(ctx, role):
    role_id = []
    role_name = []
    
    # Finds role_id by name
    l = str(ctx.guild.roles).split('<Role id=')[1:]
    roles = [x.lower() for x in l]

    for x in range(len(roles)):
        if role in roles[x-1]:
            role_id.append(roles[x-1].split()[0])
            role_name.append(l[x-1].split('\'')[1])

    return role_id, role_name

def select(ctx, list_id, list_name):
    choice = '```'
    for x in range(len(list_id)):
        choice = (choice + str(x+1) + '.  Object ID = ' + str(list_id[x]) +
                  ' -- Name = ' + list_name[x] + '\n')
    choice = choice + '```'

    return choice


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
        print('worked')
    except (Exception, dbSQL.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

    if updated_rows > 0:
        return True
    else:
        return False
