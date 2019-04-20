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

    @commands.command(name='connect', hidden=True)
    @commands.is_owner()
    async def postgre_version(self, ctx):
        DataStructCog.connect()


def setup(bot):
    bot.add_cog(DataStructCog(bot))
