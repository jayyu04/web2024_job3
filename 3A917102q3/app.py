from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
import logging

app = Flask(__name__)
app.secret_key = "your_secret_key"  # 確保這行設置了你的 secret key

DB_NAME = "mydb.db"

# 設置日誌
logging.basicConfig(filename="error.log", level=logging.ERROR)


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    if "userid" not in session:
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM member WHERE idno = ?", (session["userid"],))
        user = cursor.fetchone()
        conn.close()
        return render_template("index.html", user=user)
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return render_template("error.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        userid = request.form["userid"]
        password = request.form["password"]
        print(f"Trying to log in with userid: {userid} and password: {password}")

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM member WHERE idno = ? AND pwd = ?", (userid, password)
            )
            user = cursor.fetchone()
            conn.close()
            print(f"Query result: {user}")

            if user:
                session["userid"] = user["idno"]
                return redirect(url_for("index"))
            else:
                flash("請輸入正確的帳號密碼")
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return render_template("error.html")

    return render_template("login.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if "userid" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        name = request.form["name"]
        birthdate = request.form["birthdate"]
        bloodtype = request.form["bloodtype"]
        phone = request.form["phone"]
        email = request.form["email"]
        userid = request.form["userid"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE member
                SET nm = ?, birth = ?, blood = ?, phone = ?, email = ?, pwd = ?
                WHERE idno = ?
            """,
                (name, birthdate, bloodtype, phone, email, password, session["userid"]),
            )
            conn.commit()
            conn.close()
            session["userid"] = userid  # 更新 session 中的 userid
            return redirect(url_for("index"))
        except Exception as e:
            logging.error(f"Exception occurred: {e}")
            return render_template("error.html")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM member WHERE idno = ?", (session["userid"],))
        user = cursor.fetchone()
        conn.close()
        return render_template("edit.html", user=user)
    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return render_template("error.html")


@app.route("/logout")
def logout():
    session.pop("userid", None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
