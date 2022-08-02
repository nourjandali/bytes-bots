from flask import Flask
from flask import render_template, request
import psycopg2
import psycopg2.extras
import datetime
from flask import jsonify

app = Flask(__name__)

keepalive_kwargs = {
    "keepalives": 1,
    "keepalives_idle": 1000,
    "keepalives_interval": 1000,
    "keepalives_count": 100
}

DB_HOST = "ec2-52-20-166-21.compute-1.amazonaws.com"
DB_NAME = "d2bhgu2oeoc6np"
DB_USER = "ciqopzuwvoexbs"
DB_PASS = "1607715c655c26b9e8e966b51cd21fb23640135a839807ec5639afee19628349"
DB_PORT = "5432"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT, **keepalive_kwargs)


@app.route("/")
def home():
    return render_template("home.html", name="home")


@app.route("/search", methods=["POST"])
def fetchDatabase():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    studentName = request.form['studentName']
    cur.execute(
        "SELECT studentname, currentclass, id, debriefsheetid, totalclasses FROM reportcards WHERE studentname ILIKE '%" + studentName + "%' ORDER BY studentname ASC")
    students = cur.fetchall();

    cur.execute("SELECT studentid FROM checkin")
    checkin = cur.fetchall();
    checkinStudents = [item for sublist in checkin for item in sublist]
    
    results = [];
    for student in students:
        cur.execute(
            """SELECT debriefid, debriefdate, mentorname 
                        FROM debriefs
                        WHERE studentid = '%s' 
                        AND debriefsheetid ='%s'
                        ORDER BY debriefdate DESC"""
            % (student[2], student[3])
        )
        debriefs = cur.fetchall()
        cur.execute(
            """SELECT totalclass, usage, importedclasses 
                        FROM packages
                        WHERE studentid = '%s' 
                        AND debriefsheetid ='%s'"""
            % (student[2], student[3])
        )
        packages = cur.fetchone()
        if len(debriefs):
            results.append({**dict(student), **dict(debriefs[0]), **dict(packages), 'noOfDebriefs': len(debriefs)})
        else:
            results.append({**dict(student), **dict(packages), 'noOfDebriefs': len(debriefs)})

        

        print(checkinStudents)
    return render_template("response.html", data=results,checkinStudents=checkinStudents )


@app.route("/checkin", methods=["GET"])
def checkinList():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT studentname, studentid, checkintime FROM checkin ORDER BY checkintime DESC")
    students = cur.fetchall();

    v = {}
    for student in students:
        v.setdefault(student[2].strftime("%A (%b %d)"), []).append(student)

    # return jsonify(v);
    return render_template("checkin.html", data=v)


@app.route("/checkin", methods=["POST"])
def addtoCheckinList():
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    studentName = request.form['studentName']
    studentId = request.form['studentId']
    checkinDate = datetime.datetime.now()
    cur.execute("INSERT INTO checkin (studentname, studentid, checkintime) VALUES ('" + studentName + "', '" + studentId + "', '" + checkinDate.strftime("%Y-%m-%d, %H:%M:%S") + "') ")
    return "Success"

@app.route("/checkin/<studentId>", methods=["DELETE"])
def removeFromCheckinList(studentId):
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("DELETE FROM checkin WHERE studentid='" + studentId + "' ")
    return "Success"


if __name__ == "__main__":
    app.run(debug=True)
