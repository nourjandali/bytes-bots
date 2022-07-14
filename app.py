from typing import ChainMap
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
    cur.execute("SELECT studentname,currentclass,id,debriefsheetid, totalclasses FROM reportcards WHERE studentname ILIKE '%" + studentName +"%' ORDER BY studentname ASC")
    students = cur.fetchall();
    results = [];
    for student in students:
        cur.execute("""SELECT debriefid,debriefdate,mentorname from debriefs
        WHERE studentid = '%s' and debriefsheetid ='%s'
        ORDER BY debriefdate DESC""" % (student[2],student[3])  
                    )
        debriefs = cur.fetchall()
        cur.execute("""Select totalclass, usage, importedclasses from packages
                    where studentid = '%s' and debriefsheetid ='%s'""" % (student[2],student[3]) 
                    )
        packages = cur.fetchone()
        results.append({**dict(student), **dict(debriefs[0]), **dict(packages), 'noOfDebriefs': len(debriefs)  })
    return render_template('response.html', data=results)


if __name__ == "__main__":
    app.run(debug=True)