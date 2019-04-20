#!/usr/local/bin/python3.6
from bin import zb_config

_var = zb_config

def is_owner(ctx):
    if int(ctx.author.id) == int(_var.ownerID):
        return True
    else:
        return False
