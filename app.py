from typing import ChainMap
from flask import Flask
from flask import render_template, request, jsonify
import psycopg2
import psycopg2.extras

app = Flask(__name__)

DB_HOST = "ec2-52-20-166-21.compute-1.amazonaws.com"
DB_NAME = "d2bhgu2oeoc6np"
DB_USER = "ciqopzuwvoexbs"
DB_PASS = "1607715c655c26b9e8e966b51cd21fb23640135a839807ec5639afee19628349"
DB_PORT = "5432"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)


@app.route("/")
def home():
    return render_template("home.html", name="home")


@app.route("/search", methods=["POST"])
def fetchDatabase():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    studentName = request.form['studentName']
    cur.execute("SELECT studentname, currentclass, id, debriefsheetid, totalclasses FROM reportcards WHERE studentname ILIKE '%" + studentName +"%' ORDER BY studentname ASC")
    students = cur.fetchall();
    results = [];
    for student in students:
        cur.execute(
                    """SELECT debriefid, debriefdate, mentorname 
                        FROM debriefs
                        WHERE studentid = '%s' 
                        AND debriefsheetid ='%s'
                        ORDER BY debriefdate DESC""" 
                        % (student[2],student[3])  
                    )
        debriefs = cur.fetchall()
        cur.execute(
                    """SELECT totalclass, usage, importedclasses 
                        FROM packages
                        WHERE studentid = '%s' 
                        AND debriefsheetid ='%s'""" 
                        % (student[2],student[3]) 
                    )
        packages = cur.fetchone()
        results.append({**dict(student), **dict(debriefs[0]), **dict(packages), 'noOfDebriefs': len(debriefs)  })
    return render_template("response.html", data=results)

@app.route("/checkin", methods=["GET"])
def checkinList():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT studentname, CAST(checkintime AS varchar(10)) FROM checkin")
    students = cur.fetchall();
    return render_template("checkin.html", data=students)


if __name__ == "__main__":
    app.run(debug=True)