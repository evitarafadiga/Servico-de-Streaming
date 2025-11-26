import flask, psycopg2, psycopg2.extensions, select, os, time
from flask import render_template

app = flask.Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def stream_messages(channel):
    conn = None
    try: 
        conn = psycopg2.connect(DATABASE_URL)
        conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        
        curs = conn.cursor()
        curs.execute("LISTEN channel_%d;" % int(channel))
        
        while True:
            ready = select.select([conn], [], [], 10)
            if ready[0]:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop()
                    yield "data: " + notify.payload + "\n\n"
            
            yield "data: \n\n"
    except GeneratorExit:
        print(f"Disconectado do canal: {channel}")
    except Exception as e:
        print(f"Erro de mensagem: {e}")
    finally:
        if conn:
            conn.close()            
            
@app.route("/message/<channel>", methods=['GET'])
def get_messages(channel):
    response = flask.Response(stream_messages(channel), mimetype='text/event-stream')
    response.headers.add('Cache-Control', 'no-cache')
    response.headers.add('Connection', 'keep-alive')
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/", methods=['GET','POST'])
def index():
    return render_template('index.html')

if __name__ == "__main__":

    app.run()
