from discord.ext import commands
import psycopg2 as dbSQL
from bin import config

_var = config


class DataStructCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def connect():
        """ Connect to the PostgreSQL database server """

        conn = None

        try:
            print('Connecting to the PostgreSQL database...')

            # Connects to database
            conn = dbSQL.connect(host = 'localhost',
                                 database=_var.dbName,
                                 user=_var.dbUser,
                                 password=_var.dbPass)

            # Creates a cursor
            cur = conn.cursor()

        # Print connection version
            print('PostgreSQL database version:')
            cur.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            print(db_version)

        # Close database connection
            cur.close()

        except (Exception, dbSQL.DatabaseError) as error:
                print(error)

        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')

    if __name__ == '__main__':
        connect()

    def update_vendor(role_id, role_perms):
        """ update vendor name based on the vendor id """

        sql = """ UPDATE roles
                  SET role_perms = %s
                  WHERE role_id = %s """
        conn = None
        updated_rows = 0
        try:
            # read database configuration
            # params = config()
            # connect to the PostgreSQL database
            conn = dbSQL.connect(host = 'localhost',
                                 database=_var.dbName,
                                 user=_var.dbUser,
                                 password=_var.dbPass)
            # create a new cursor
            cur = conn.cursor()
            # execute the UPDATE  statement
            cur.execute(sql, (role_perms, role_id))
            # get the number of updated rows
            updated_rows = cur.rowcount
            # Commit the changes to the database
            conn.commit()
            # Close communication with the PostgreSQL database
            cur.close()
        except (Exception, dbSQL.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()

        return updated_rows

    @commands.command(name='connect', hidden=True)
    @commands.is_owner()
    async def postgre_version(self, ctx):
        DataStructCog.connect()

    @commands.command(name='connectt', hidden=True)
    @commands.is_owner()
    async def role_perms(self, ctx):
        print(DataStructCog.update_vendor(526427381989376037,1))


def setup(bot):
    bot.add_cog(DataStructCog(bot))
