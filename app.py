from flask import Flask
from flask import render_template, request, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)

DB_HOST = "localhost"
DB_NAME = "bytes-bots"
DB_USER = "postgres"
DB_PASS = "root"
DB_PORT = "5432"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)


@app.route("/")
def home():
    return render_template("home.html", name="home")


@app.route("/search", methods=["POST"])
def test():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    studentName = request.form['studentName']
    query = "SELECT * FROM public.reportcards WHERE studentname ILIKE '%" + studentName +"%' ORDER BY studentname ASC"
    cur.execute(query)
    return render_template('response.html', data=cur.fetchall())


if __name__ == "__main__":
    app.run(debug=True)
