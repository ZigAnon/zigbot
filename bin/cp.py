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
from bin import zb
from bin import zb_config

_var = zb_config
_query = """ SELECT g.guild_id,u.real_user_id,r.role_id,u.name,g.nick,u.int_user_id
             FROM users u
             LEFT JOIN guild_membership g ON u.int_user_id = g.int_user_id
             LEFT JOIN role_membership r ON u.int_user_id = r.int_user_id """

rmvRoles = [[517850437626363925],[513156267024449556],[517140313408536576],
        [509865275705917440],[509865272283496449],[509861871193423873],
        [509866307857154048],[509857601081704448],[513021830173556759],
        [509857604328095775],[520654520443732009]]

_int_user_id = """ SELECT int_user_id
                   FROM users
                   WHERE real_user_id = {0} """

_update_punish = """ UPDATE guild_membership
                     SET punished = {0}
                     WHERE int_user_id = {1}
                     AND guild_id = {2} """

def punish_user(member,number):
    sql = _int_user_id.format(member.id)
    data, rows, string = zb.sql_query(sql)
    intID = int(data[0])

    sql = _update_punish.format(number,intID,member.guild.id)
    rows, string = zb.sql_update(sql)

def is_outranked(member1, member2, role_perms):
    """ test for valid data in database at two columns """

    idList1 = []
    for role in member1.roles:
        idList1.append(role.id)

    idList2 = []
    for role in member2.roles:
        idList2.append(role.id)

    sql = """ SELECT MIN(role_perms)
              FROM roles
              WHERE guild_id = {0}
              AND NOT role_perms = 0
              AND role_perms <= {1}
              AND role_id in {2} """
    sql = sql.format(member1.guild.id,
                     role_perms,
                     zb.sql_list(idList1))
    data1, rows, string = zb.sql_query(sql)

    sql = """ SELECT MIN(role_perms)
              FROM roles
              WHERE guild_id = {0}
              AND NOT role_perms = 0
              AND role_perms <= {1}
              AND role_id in {2} """
    sql = sql.format(member2.guild.id,
                     role_perms,
                     zb.sql_list(idList2))
    data2, rows, string = zb.sql_query(sql)

    try:
        var = int(data2[0])
    except:
        return True
    if rows == 0:
        return True
    elif int(data1[0]) < int(data2[0]):
        return True
    else:
        return False

