from flask import Flask, redirect, url_for, render_template, request, session
from datetime import timedelta
import pprint

from tick_utils import fetch_user, fetch_user_async, knit_ticks_by_date


app = Flask(__name__)
app.secret_key = "secret" #TODO use a real secret
app.permanent_session_lifetime = timedelta(minutes=5)

@app.route("/")
def home():
    ticks = {}
    sorted_ticks = []
    if 'user_ids' in session:
        watched_users = session['user_ids']
        for user_id in watched_users:
            fetch_user(user_id)
        sorted_ticks = knit_ticks_by_date(watched_users) #It would be great to cache the ticks instead of re-scraping mtnproj every time.

    return render_template("index.html", sorted_ticks=sorted_ticks)

@app.route("/add-user-id", methods=["POST", "GET"])
def add_user_id():
    if request.method == "POST":
        session.permanent = True
        user_id = request.form["usrid"]
        if 'user_ids' in session:
            session["user_ids"].append(user_id) #TODO prevent adding duplicate users
        else:
            session['user_ids'] = [user_id]
        fetch_user_async(user_id)
        return redirect(url_for("add_user_id")) 
    else:
        return render_template("adduserid.html")



if __name__ == "__main__":
	app.run(debug=True, port=5001, threaded=True)