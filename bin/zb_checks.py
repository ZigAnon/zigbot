#!/usr/local/bin/python3.6
import psycopg2 as dbSQL
from bin import zb_config

_var = zb_config

def sql_login():
    conn = dbSQL.connect(host = 'localhost',
                         database=_var.dbName,
                         user=_var.dbUser,
                         password=_var.dbPass)
    cur = conn.cursor()
    return conn, cur

def is_owner(ctx):
    if int(ctx.author.id) == int(_var.ownerID):
        return True
    else:
        return False

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
