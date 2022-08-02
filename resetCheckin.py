import psycopg2
import psycopg2.extras

DB_HOST = "ec2-52-20-166-21.compute-1.amazonaws.com"
DB_NAME = "d2bhgu2oeoc6np"
DB_USER = "ciqopzuwvoexbs"
DB_PASS = "1607715c655c26b9e8e966b51cd21fb23640135a839807ec5639afee19628349"
DB_PORT = "5432"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)


def resetCheckin():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("DELETE FROM checkin")
    data = cur.fetchall();
    print(data)

resetCheckin()