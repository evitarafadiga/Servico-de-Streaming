import psycopg2
import psycopg2.extensions
import select

conn = psycopg2.connect(database='postgres', user='postgres',
                        password='1234', host='127.0.1.1')
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

curs = conn.cursor()
hora = curs.execute("SELECT date('now');")

print('Conectado às', str(hora))
curs.execute("LISTEN channel_1;")

while True:
    select.select([conn], [], [])
    conn.poll()
    while conn.notifies:
        notify = conn.notifies.pop()
        print("FOI NOTIFICADO: ", notify.pid, notify.channel, notify.payload)