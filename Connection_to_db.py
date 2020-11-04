import psycopg2


def command_execution(string_to_execute):
        con = psycopg2.connect(  # connecting to PostgreSQL database
            database='urls',
            user='postgres',
            password='',
            host="127.0.0.1",
            port="5432"
        )
        cur = con.cursor()  # creating new cursor object
        cur.execute(string_to_execute)
        con.commit()  # commit changes
        con.close()
